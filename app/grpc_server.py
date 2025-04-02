import concurrent.futures
import logging
import os
import grpc
from typing import Dict, Any, Optional

from . import valmiki_pb2
from . import valmiki_pb2_grpc
from .predictor import predict_age_gender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValmikiServicer(valmiki_pb2_grpc.ValmikiServiceServicer):
    """Implementation of the ValmikiService gRPC service."""
    
    def Predict(self, request, context):
        """
        Process image data and return age and gender predictions.
        Maps between the gRPC PredictRequest/PredictResponse and the 
        existing predict_age_gender function.
        """
        logger.info("Received gRPC prediction request")
        
        if not request.image_data:
            logger.error("Empty image data received")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Empty image data")
            return valmiki_pb2.PredictResponse()
        
        try:
            result = predict_age_gender(request.image_data)
            
            if result is None:
                logger.error("Prediction function returned None")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Prediction failed")
                return valmiki_pb2.PredictResponse()
            
            if "error" in result:
                logger.warning(f"Prediction error: {result['error']}")
                if "No face detected" in result["error"]:
                    context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                    context.set_details(result["error"])
                else:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details(result["error"])
                return valmiki_pb2.PredictResponse()
            
            age_group = map_age_to_group(result["age"])
            gender = result["gender"].lower()  # Normalize to lowercase
            
            logger.info(f"Prediction successful: Age={age_group}, Gender={gender}")
            
            return valmiki_pb2.PredictResponse(
                age_group=age_group,
                gender=gender,
                confidence=0.95 
            )
            
        except Exception as e:
            logger.exception(f"Error during prediction processing: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return valmiki_pb2.PredictResponse()

def map_age_to_group(age_range: str) -> str:
    """
    Maps the model's age ranges like '(4-6)' to simplified categories
    that Gyandoot will use for Redis keys.
    """
    age_range = age_range.strip('()')
    
    try:
        parts = age_range.split('-')
        min_age = int(parts[0])
        
        if min_age < 13:
            return "child"
        elif min_age < 20:
            return "teen"
        elif min_age < 35:
            return "young_adult"
        elif min_age < 50:
            return "adult"
        else:
            return "senior"
    except (ValueError, IndexError) as e:
        logger.warning(f"Error parsing age range '{age_range}': {e}")
        return "adult"  

def serve():
    """
    Start the gRPC server on the designated port.
    """
    port = int(os.environ.get("GRPC_PORT", "50052"))
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    valmiki_pb2_grpc.add_ValmikiServiceServicer_to_server(ValmikiServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"gRPC server started on port {port}")
    return server

if __name__ == "__main__":
    
    server = serve()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server") 
