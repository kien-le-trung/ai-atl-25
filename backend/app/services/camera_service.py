"""
Camera service for capturing frames from OBS virtual camera (Meta glasses)
and detecting faces for partner identification.
"""
import cv2
import numpy as np
from typing import Optional, Tuple, List
import logging
import tempfile
import os
import threading

logger = logging.getLogger(__name__)

# Lazy-load DeepFace to avoid blocking startup
_deepface = None
_deepface_lock = threading.Lock()


def _get_deepface():
    """Lazy-load DeepFace module to avoid blocking startup"""
    global _deepface
    if _deepface is None:
        with _deepface_lock:
            if _deepface is None:  # Double-check locking
                logger.info("Loading DeepFace models...")
                from deepface import DeepFace as DF
                _deepface = DF
                logger.info("DeepFace models loaded")
    return _deepface


class CameraService:
    """Handles camera capture and face detection from OBS virtual camera."""

    def __init__(self):
        self.camera = None
        self.camera_index = None
        self.is_active = False

    def find_obs_camera(self, max_sources: int = 10) -> Optional[int]:
        """
        Find OBS Virtual Camera among available video sources.

        Args:
            max_sources: Maximum number of camera indices to check

        Returns:
            Camera index if found, None otherwise
        """
        logger.info("Scanning for OBS Virtual Camera...")

        for i in range(max_sources):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    # Get camera name/backend info if possible
                    backend = cap.getBackendName()
                    logger.info(f"Found camera at index {i}, backend: {backend}")

                    # OBS Virtual Camera is usually the last one or has specific properties
                    # We'll return the first working camera for now
                    # In production, you might want to filter by name
                    cap.release()
                    return i
                cap.release()

        return None

    def start_camera(self, camera_index: Optional[int] = None) -> bool:
        """
        Start the camera feed.

        Args:
            camera_index: Specific camera index to use, or None to auto-detect

        Returns:
            True if camera started successfully, False otherwise
        """
        try:
            if camera_index is None:
                camera_index = self.find_obs_camera()

            if camera_index is None:
                logger.error("No camera found")
                return False

            self.camera = cv2.VideoCapture(camera_index)

            if not self.camera.isOpened():
                logger.error(f"Could not open camera {camera_index}")
                return False

            self.camera_index = camera_index
            self.is_active = True

            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            logger.info(f"Camera {camera_index} started: {width}x{height}")

            return True

        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            return False

    def stop_camera(self):
        """Stop the camera feed."""
        if self.camera:
            self.camera.release()
            self.camera = None
            self.is_active = False
            logger.info("Camera stopped")

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the camera.

        Returns:
            Frame as numpy array, or None if capture failed
        """
        if not self.is_active or not self.camera:
            logger.error("Camera is not active")
            return None

        ret, frame = self.camera.read()

        if not ret:
            logger.error("Failed to capture frame")
            return None

        return frame

    def detect_largest_face(self, frame: np.ndarray) -> Optional[Tuple[np.ndarray, dict]]:
        """
        Detect the most prominent (largest) face in the frame.

        Args:
            frame: Input frame as numpy array

        Returns:
            Tuple of (cropped_face_image, face_info) or None if no face detected
            face_info contains: {'x', 'y', 'w', 'h', 'confidence'}
        """
        try:
            # Use OpenCV's Haar Cascade for fast face detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )

            if len(faces) == 0:
                logger.info("No faces detected in frame")
                return None

            # Find largest face by area
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest_face

            # Add padding around the face
            padding = int(w * 0.2)
            x_start = max(0, x - padding)
            y_start = max(0, y - padding)
            x_end = min(frame.shape[1], x + w + padding)
            y_end = min(frame.shape[0], y + h + padding)

            # Crop face region
            face_img = frame[y_start:y_end, x_start:x_end]

            face_info = {
                'x': int(x),
                'y': int(y),
                'w': int(w),
                'h': int(h),
                'confidence': 1.0  # Haar cascade doesn't provide confidence
            }

            logger.info(f"Detected face: {w}x{h} at ({x}, {y})")

            return face_img, face_info

        except Exception as e:
            logger.error(f"Error detecting face: {e}")
            return None

    def extract_face_embedding(self, face_img: np.ndarray) -> Optional[List[float]]:
        """
        Extract face embedding from a face image using DeepFace.

        Args:
            face_img: Face image as numpy array

        Returns:
            Face embedding as list, or None if extraction failed
        """
        try:
            # Lazy-load DeepFace
            DeepFace = _get_deepface()

            # Save face to temporary file (DeepFace requires file path)
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp_path = tmp.name
                cv2.imwrite(tmp_path, face_img)

            try:
                # Extract embedding using DeepFace
                embeddings = DeepFace.represent(
                    img_path=tmp_path,
                    model_name="Facenet512",
                    detector_backend="opencv",
                    enforce_detection=True,
                    align=True,
                )

                if embeddings and len(embeddings) > 0:
                    embedding = embeddings[0]["embedding"]

                    # Pad to 4096 dimensions
                    if len(embedding) < 4096:
                        padded_embedding = np.zeros(4096)
                        padded_embedding[:len(embedding)] = embedding
                        return padded_embedding.tolist()

                    return embedding[:4096]

                return None

            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            logger.error(f"Error extracting face embedding: {e}")
            return None

    def capture_and_identify_face(self) -> Optional[Tuple[np.ndarray, List[float], dict]]:
        """
        Capture a frame, detect the largest face, and extract its embedding.

        Returns:
            Tuple of (face_image, embedding, face_info) or None if failed
        """
        # Capture frame
        frame = self.capture_frame()
        if frame is None:
            return None

        # Detect largest face
        result = self.detect_largest_face(frame)
        if result is None:
            return None

        face_img, face_info = result

        # Extract embedding
        embedding = self.extract_face_embedding(face_img)
        if embedding is None:
            return None

        return face_img, embedding, face_info

    def save_face_image(self, face_img: np.ndarray, filename: str) -> str:
        """
        Save face image to disk.

        Args:
            face_img: Face image as numpy array
            filename: Filename to save as

        Returns:
            Full path to saved image
        """
        upload_dir = "uploads/faces"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, filename)
        cv2.imwrite(file_path, face_img)

        logger.info(f"Face image saved: {file_path}")
        return file_path
