"""
Face recognition service using DeepFace
"""
from typing import List, Optional
import os
import numpy as np
from deepface import DeepFace
from sqlalchemy.orm import Session
from app.models.conversation_partner import ConversationPartner
import logging

logger = logging.getLogger(__name__)

# Configuration
UPLOAD_DIR = "uploads/faces"
MODEL_NAME = "Facenet512"  # This generates 512-dim embeddings, but we'll pad to 4096
DETECTOR_BACKEND = "opencv"
DISTANCE_METRIC = "cosine"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_face_embedding(image_path: str) -> Optional[np.ndarray]:
    """
    Extract face embedding from an image using DeepFace

    Args:
        image_path: Path to the image file

    Returns:
        Face embedding as numpy array, or None if no face detected
    """
    try:
        # Use DeepFace.represent to get embeddings
        embeddings = DeepFace.represent(
            img_path=image_path,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,
            align=True,
        )

        if embeddings and len(embeddings) > 0:
            # Get the first face embedding
            embedding = np.array(embeddings[0]["embedding"])

            # Pad to 4096 dimensions to match our database schema
            if len(embedding) < 4096:
                padded_embedding = np.zeros(4096)
                padded_embedding[:len(embedding)] = embedding
                return padded_embedding

            return embedding[:4096]

        return None

    except Exception as e:
        logger.error(f"Error extracting face embedding: {str(e)}")
        return None


def find_similar_faces(
    image_path: str,
    db: Session,
    threshold: float = 0.6,
    top_k: int = 5
) -> List[tuple[ConversationPartner, float]]:
    """
    Find similar faces in the database

    Args:
        image_path: Path to the query image
        db: Database session
        threshold: Similarity threshold (0-1, higher = more similar)
        top_k: Maximum number of results to return

    Returns:
        List of tuples (partner, similarity_score)
    """
    try:
        # Extract embedding from query image
        query_embedding = extract_face_embedding(image_path)
        if query_embedding is None:
            logger.warning("No face detected in query image")
            return []

        # Get all partners with image embeddings from database
        partners = db.query(ConversationPartner).filter(
            ConversationPartner.image_embedding.isnot(None)
        ).all()

        if not partners:
            logger.info("No partners with face embeddings in database")
            return []

        # Calculate cosine similarity with each partner
        results = []
        for partner in partners:
            if partner.image_embedding is None:
                continue

            # Convert stored embedding to numpy array
            partner_embedding = np.array(partner.image_embedding)

            # Calculate cosine similarity
            similarity = cosine_similarity(query_embedding, partner_embedding)

            if similarity >= threshold:
                results.append((partner, float(similarity)))

        # Sort by similarity (highest first) and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    except Exception as e:
        logger.error(f"Error finding similar faces: {str(e)}")
        return []


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score (0-1)
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    similarity = dot_product / (norm1 * norm2)
    # Convert from [-1, 1] to [0, 1]
    return (similarity + 1) / 2


def save_face_image(image_data: bytes, filename: str) -> str:
    """
    Save uploaded face image to disk

    Args:
        image_data: Image file bytes
        filename: Original filename

    Returns:
        Path to saved image
    """
    # Generate unique filename
    import uuid
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(image_data)

    return file_path


def verify_faces(image_path1: str, image_path2: str) -> Optional[dict]:
    """
    Verify if two images contain the same person

    Args:
        image_path1: Path to first image
        image_path2: Path to second image

    Returns:
        Dictionary with verification result or None if error
    """
    try:
        result = DeepFace.verify(
            img1_path=image_path1,
            img2_path=image_path2,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            distance_metric=DISTANCE_METRIC,
        )
        return result

    except Exception as e:
        logger.error(f"Error verifying faces: {str(e)}")
        return None
