import cv2
import numpy as np
import os
import logging
from typing import Tuple, Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

FACE_PROTO = os.path.join(MODEL_DIR, "deploy.prototxt")
FACE_MODEL = os.path.join(MODEL_DIR, "res10_300x300_ssd_iter_140000.caffemodel")
AGE_PROTO = os.path.join(MODEL_DIR, "age_deploy.prototxt")
AGE_MODEL = os.path.join(MODEL_DIR, "age_net.caffemodel")
GENDER_PROTO = os.path.join(MODEL_DIR, "gender_deploy.prototxt")
GENDER_MODEL = os.path.join(MODEL_DIR, "gender_net.caffemodel")

FACE_CONFIDENCE_THRESHOLD = 0.5
MODEL_MEAN_VALUES = (78.42633776, 87.76891437, 114.89584775)
AGE_BUCKETS = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
GENDER_LIST = ['Male', 'Female']

try:
    face_net = cv2.dnn.readNet(FACE_MODEL, FACE_PROTO)
    age_net = cv2.dnn.readNet(AGE_MODEL, AGE_PROTO)
    gender_net = cv2.dnn.readNet(GENDER_MODEL, GENDER_PROTO)
    logger.info("Successfully loaded all models.")
except cv2.error as e:
    logger.error(f"Error loading models: {e}")
    face_net = None
    age_net = None
    gender_net = None

def _find_face(frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """Detects the most prominent face in the frame."""
    if face_net is None:
        logger.error("Face detection model not loaded.")
        return None

    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0)) # Mean values specific to face detector

    face_net.setInput(blob)
    detections = face_net.forward()

    best_face_box = None
    max_confidence = 0.0

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > FACE_CONFIDENCE_THRESHOLD and confidence > max_confidence:
            max_confidence = confidence
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            startX = max(0, startX)
            startY = max(0, startY)
            endX = min(w - 1, endX)
            endY = min(h - 1, endY)

            if endX > startX and endY > startY:
                 best_face_box = (startX, startY, endX, endY)

    if best_face_box:
        logger.info(f"Face detected with confidence: {max_confidence:.2f}")
    else:
        logger.warning("No face detected meeting the confidence threshold.")

    return best_face_box


def predict_age_gender(image_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Performs age and gender prediction on the input image bytes.

    Args:
        image_bytes: Raw bytes of the image file.

    Returns:
        A dictionary containing 'age' and 'gender' predictions,
        or None if prediction fails.
    """
    if age_net is None or gender_net is None:
         logger.error("Age/Gender models not loaded.")
         return None

    try:
        image_np = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        if frame is None:
            logger.error("Could not decode image.")
            return None
        (h, w) = frame.shape[:2]
        if h == 0 or w == 0:
            logger.error("Invalid image dimensions.")
            return None

        face_box = _find_face(frame)

        if face_box is None:
            # Option 1: Return None or error if no face found (as implemented)
            logger.warning("No face detected in the image.")
            return {"error": "No face detected"}
            # Option 2: Try predicting on the whole image (less accurate)
            # startX, startY, endX, endY = 0, 0, w, h # Use whole image

        (startX, startY, endX, endY) = face_box

        # Add padding around the face box
        padding = 20 
        face = frame[max(0, startY - padding):min(h, endY + padding),
                     max(0, startX - padding):min(w, endX + padding)]

        if face.size == 0:
            logger.error("Extracted face region is empty.")
            return {"error": "Failed to extract face region"}

        # Models expect 227x227 input, mean subtraction
        face_blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False) # Check swapRB based on model needs

        # 4. Predict Gender
        gender_net.setInput(face_blob)
        gender_preds = gender_net.forward()
        gender = GENDER_LIST[gender_preds[0].argmax()]
        logger.info(f"Gender Prediction Raw: {gender_preds}, Chosen: {gender}")

        # 5. Predict Age
        age_net.setInput(face_blob)
        age_preds = age_net.forward()
        age = AGE_BUCKETS[age_preds[0].argmax()]
        logger.info(f"Age Prediction Raw: {age_preds}, Chosen: {age}")

        return {"age": age, "gender": gender}

    except cv2.error as e:
        logger.error(f"OpenCV error during prediction: {e}")
        return {"error": f"OpenCV processing error: {e}"}
    except Exception as e:
        logger.exception(f"An unexpected error occurred during prediction: {e}")
        return {"error": f"An unexpected server error occurred: {e}"}
