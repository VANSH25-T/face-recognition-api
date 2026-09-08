"""
Face Recognition API
A FastAPI-based REST API for face recognition, detection, and verification.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from pathlib import Path
import face_recognition
from pydantic import BaseModel
from typing import List, Optional
import io
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Face Recognition API",
    description="API for face detection, recognition, and verification",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
Path("known_faces").mkdir(exist_ok=True)
Path("uploaded_images").mkdir(exist_ok=True)

# Global variables for storing known faces
known_encodings = []
known_names = []


# Pydantic models
class FaceMatch(BaseModel):
    name: str
    confidence: float
    distance: float


class FaceDetectionResponse(BaseModel):
    faces_detected: int
    face_locations: List[dict]


class FaceRecognitionResponse(BaseModel):
    matches: List[FaceMatch]
    unknown_faces: int


class StatusResponse(BaseModel):
    status: str
    message: str


# Helper functions
def load_known_faces():
    """Load and encode all known faces from the known_faces directory."""
    global known_encodings, known_names
    known_encodings = []
    known_names = []
    
    known_faces_dir = Path("known_faces")
    if not known_faces_dir.exists():
        logger.warning("known_faces directory not found")
        return
    
    for person_dir in known_faces_dir.iterdir():
        if person_dir.is_dir():
            for image_path in person_dir.glob("*.jpg"):
                try:
                    image = face_recognition.load_image_file(str(image_path))
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        known_encodings.append(encodings[0])
                        known_names.append(person_dir.name)
                        logger.info(f"Loaded face for: {person_dir.name}")
                except Exception as e:
                    logger.error(f"Error loading {image_path}: {str(e)}")
    
    logger.info(f"Total known faces loaded: {len(known_encodings)}")


def process_image(image_bytes: bytes) -> np.ndarray:
    """Convert image bytes to numpy array."""
    image = Image.open(io.BytesIO(image_bytes))
    image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return image_np


def get_face_locations(image_np: np.ndarray) -> List[tuple]:
    """Detect face locations in an image."""
    rgb_image = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image, model="hog")
    return face_locations


def get_face_encodings(image_np: np.ndarray, face_locations: List[tuple]) -> List[np.ndarray]:
    """Get face encodings for detected faces."""
    rgb_image = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    return face_encodings


def recognize_faces(face_encodings: List[np.ndarray], tolerance: float = 0.6) -> List[FaceMatch]:
    """Recognize faces by comparing with known faces."""
    matches_list = []
    
    for face_encoding in face_encodings:
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        
        if len(distances) > 0:
            best_match_index = np.argmin(distances)
            best_distance = distances[best_match_index]
            
            if best_distance < tolerance:
                confidence = 1 - best_distance
                match = FaceMatch(
                    name=known_names[best_match_index],
                    confidence=round(confidence, 4),
                    distance=round(best_distance, 4)
                )
                matches_list.append(match)
    
    return matches_list


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Load known faces on startup."""
    load_known_faces()
    logger.info("API started and faces loaded")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "message": "Face Recognition API is active",
        "version": "1.0.0"
    }


@app.post("/api/detect-faces", response_model=FaceDetectionResponse, tags=["Detection"])
async def detect_faces(file: UploadFile = File(...)):
    """
    Detect faces in an uploaded image.
    
    Returns:
        - Number of faces detected
        - Face locations (top, right, bottom, left coordinates)
    """
    try:
        image_bytes = await file.read()
        image_np = process_image(image_bytes)
        
        face_locations = get_face_locations(image_np)
        
        face_locations_dict = [
            {
                "top": int(top),
                "right": int(right),
                "bottom": int(bottom),
                "left": int(left)
            }
            for top, right, bottom, left in face_locations
        ]
        
        return FaceDetectionResponse(
            faces_detected=len(face_locations),
            face_locations=face_locations_dict
        )
    
    except Exception as e:
        logger.error(f"Error in detect_faces: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


@app.post("/api/recognize-faces", response_model=FaceRecognitionResponse, tags=["Recognition"])
async def recognize_faces_endpoint(file: UploadFile = File(...), tolerance: float = 0.6):
    """
    Recognize faces in an uploaded image against known faces.
    
    Parameters:
        - file: Image file (jpg, png, etc.)
        - tolerance: Face distance tolerance (0.0-1.0, lower = stricter matching)
    
    Returns:
        - List of recognized faces with confidence scores
        - Number of unknown faces
    """
    try:
        if len(known_encodings) == 0:
            raise HTTPException(
                status_code=400,
                detail="No known faces loaded. Please add faces to the known_faces directory."
            )
        
        image_bytes = await file.read()
        image_np = process_image(image_bytes)
        
        face_locations = get_face_locations(image_np)
        face_encodings = get_face_encodings(image_np, face_locations)
        
        matches = recognize_faces(face_encodings, tolerance)
        unknown_faces = len(face_encodings) - len(matches)
        
        return FaceRecognitionResponse(
            matches=matches,
            unknown_faces=max(0, unknown_faces)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in recognize_faces: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


@app.post("/api/verify-face", tags=["Verification"])
async def verify_face(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    """
    Verify if two images contain the same person.
    
    Parameters:
        - file1: First image file
        - file2: Second image file
    
    Returns:
        - Boolean indicating if faces match
        - Distance score
    """
    try:
        image1_bytes = await file1.read()
        image2_bytes = await file2.read()
        
        image1_np = process_image(image1_bytes)
        image2_np = process_image(image2_bytes)
        
        face_locations1 = get_face_locations(image1_np)
        face_locations2 = get_face_locations(image2_np)
        
        if len(face_locations1) == 0 or len(face_locations2) == 0:
            raise HTTPException(status_code=400, detail="No faces detected in one or both images")
        
        encodings1 = get_face_encodings(image1_np, face_locations1)
        encodings2 = get_face_encodings(image2_np, face_locations2)
        
        if len(encodings1) == 0 or len(encodings2) == 0:
            raise HTTPException(status_code=400, detail="Could not encode faces")
        
        distance = face_recognition.face_distance([encodings1[0]], encodings2[0])[0]
        match = distance < 0.6
        
        return {
            "match": bool(match),
            "distance": round(float(distance), 4),
            "confidence": round(1 - float(distance), 4)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verify_face: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing images: {str(e)}")


@app.post("/api/reload-faces", response_model=StatusResponse, tags=["Management"])
async def reload_faces():
    """Reload all known faces from the known_faces directory."""
    try:
        load_known_faces()
        return StatusResponse(
            status="success",
            message=f"Loaded {len(known_encodings)} faces"
        )
    except Exception as e:
        logger.error(f"Error in reload_faces: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error reloading faces: {str(e)}")


@app.get("/api/status", response_model=dict, tags=["Health"])
async def get_status():
    """Get API status and number of known faces."""
    return {
        "status": "running",
        "known_faces_loaded": len(known_encodings),
        "unique_people": len(set(known_names)),
        "people": list(set(known_names))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
