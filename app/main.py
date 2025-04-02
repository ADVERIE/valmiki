from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import logging
import os
import threading
from typing import Dict

from . import predictor
from . import grpc_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get("PORT", 8000))
GRPC_PORT = int(os.environ.get("GRPC_PORT", 50052))

app = FastAPI(
    title="Age and Gender Prediction API",
    description="Predicts age and gender from an image containing a face using Caffe models and OpenCV.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup...")
    if predictor.face_net and predictor.age_net and predictor.gender_net:
        logger.info("Models loaded successfully via predictor module.")
    else:
        logger.error("One or more models failed to load. Check predictor logs.")
    
    logger.info(f"REST API running on port {PORT}")
    
    threading.Thread(target=start_grpc_server, daemon=True).start()


def start_grpc_server():
    """Start the gRPC server in a background thread."""
    try:
        logger.info(f"Starting gRPC server on port {GRPC_PORT}...")
        server = grpc_server.serve()
        logger.info(f"gRPC server started successfully on port {GRPC_PORT}")
        server.wait_for_termination()
    except Exception as e:
        logger.error(f"Failed to start gRPC server: {e}")


@app.get("/health", tags=["Health Check"])
async def health_check() -> Dict[str, str]:
    """
    Simple health check endpoint.
    Returns 'OK' if the service is running.
    """
    logger.debug("Health check requested.")
    if not all([predictor.face_net, predictor.age_net, predictor.gender_net]):
         return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "error", "detail": "Models not loaded"})
    return {"status": "OK"}


@app.post("/predict", tags=["Prediction"])
async def predict(file: UploadFile = File(...)) -> JSONResponse:
    """
    Accepts an image file, detects a face, and predicts age and gender.

    - **file**: Image file (e.g., JPG, PNG) containing a face.
    """
    logger.info(f"Received prediction request for file: {file.filename}")

    if not all([predictor.face_net, predictor.age_net, predictor.gender_net]):
         logger.error("Prediction attempted but models are not loaded.")
         raise HTTPException(
             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
             detail="Models are not loaded, service cannot process requests."
         )

    try:
        contents = await file.read()
        if not contents:
             logger.warning("Received empty file.")
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file received.")
    except Exception as e:
        logger.error(f"Error reading uploaded file: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error reading file: {e}")
    finally:
        await file.close()

    try:
        results = predictor.predict_age_gender(contents)

        if results is None:
            logger.error("Prediction function returned None unexpectedly.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Prediction failed.")

        if "error" in results:
             logger.warning(f"Prediction failed with error: {results['error']}")
             if "No face detected" in results['error']:
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=results['error'])
             else:
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=results['error'])

        if "age" in results:
            results["age_group"] = grpc_server.map_age_to_group(results["age"])
        
        logger.info(f"Prediction successful: Age={results.get('age')}, Gender={results.get('gender')}")
        return JSONResponse(content=results)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Unexpected error during prediction endpoint processing: {e}") 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal error occurred: {e}")


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Uvicorn server directly on port {PORT}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True) # reload=True for development
