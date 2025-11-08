"""
API endpoints for managing conversation sessions with camera and audio.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import uuid
import cv2
import numpy as np
from io import BytesIO
import logging

from app.core.database import get_db
from app.services.camera_service import CameraService
from app.services.session_service import session_manager
from app.services.face_service import find_similar_faces
from app.models.conversation_partner import ConversationPartner
from app.models.user import User
from app.utils.db_helpers import get_next_id

router = APIRouter(prefix="/api/sessions", tags=["sessions"])
logger = logging.getLogger(__name__)

# Global camera service instance
camera_service = CameraService()
DEFAULT_USER_PASSWORD = "auto-generated"


def ensure_user_exists(user_id: int, db: Session) -> User:
    """
    Ensure a placeholder user exists for the given ID.

    The frontend hard-codes user_id=1 in multiple places, so if the DuckDB file
    was recreated we automatically seed a minimal user instead of failing with 404.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return user

    try:
        placeholder = User(
            id=user_id,
            email=f"default_user_{user_id}@example.com",
            username=f"default_user_{user_id}",
            hashed_password=DEFAULT_USER_PASSWORD,
            is_active=True
        )
        db.add(placeholder)
        db.commit()
        db.refresh(placeholder)
        logger.info(f"Auto-created placeholder user {user_id} for session request")
        return placeholder
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to auto-create user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create default user"
        )


# Request/Response Models
class CameraStartRequest(BaseModel):
    camera_index: Optional[int] = None


class CameraStatusResponse(BaseModel):
    is_active: bool
    camera_index: Optional[int] = None
    message: str


class FaceCaptureResponse(BaseModel):
    success: bool
    partner_id: Optional[int] = None
    partner_name: Optional[str] = None
    is_new_partner: bool
    face_detected: bool
    similarity_score: Optional[float] = None
    message: str


class SessionStartRequest(BaseModel):
    user_id: int
    partner_id: int
    deepgram_api_key: str


class SessionResponse(BaseModel):
    session_id: str
    user_id: int
    partner_id: int
    conversation_id: int
    is_running: bool
    elapsed_seconds: float
    elapsed_formatted: str
    message_count: int


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]


# Camera Endpoints

@router.get("/camera/list")
def list_available_cameras():
    """List all available cameras with their properties."""
    import cv2

    available_cameras = []

    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                backend = cap.getBackendName()

                available_cameras.append({
                    'index': i,
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'backend': backend,
                    'name': f"Camera {i} ({width}x{height})"
                })
            cap.release()

    return {
        'cameras': available_cameras,
        'count': len(available_cameras)
    }


@router.post("/camera/start", response_model=CameraStatusResponse)
def start_camera(
    request: CameraStartRequest,
    db: Session = Depends(get_db)
):
    """Start the camera feed (OBS virtual camera for Meta glasses)."""
    try:
        success = camera_service.start_camera(request.camera_index)

        if success:
            return CameraStatusResponse(
                is_active=True,
                camera_index=camera_service.camera_index,
                message=f"Camera {camera_service.camera_index} started successfully"
            )
        else:
            return CameraStatusResponse(
                is_active=False,
                camera_index=None,
                message="Failed to start camera"
            )

    except Exception as e:
        logger.error(f"Error starting camera: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/camera/stop", response_model=CameraStatusResponse)
def stop_camera():
    """Stop the camera feed."""
    try:
        camera_service.stop_camera()
        return CameraStatusResponse(
            is_active=False,
            camera_index=None,
            message="Camera stopped"
        )

    except Exception as e:
        logger.error(f"Error stopping camera: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/camera/status", response_model=CameraStatusResponse)
def get_camera_status():
    """Get current camera status."""
    return CameraStatusResponse(
        is_active=camera_service.is_active,
        camera_index=camera_service.camera_index,
        message="Camera is active" if camera_service.is_active else "Camera is inactive"
    )


@router.get("/camera/frame")
def get_current_frame():
    """Get the current camera frame as JPEG."""
    try:
        if not camera_service.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Camera is not active"
            )

        frame = camera_service.capture_frame()

        if frame is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to capture frame"
            )

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        io_buf = BytesIO(buffer)

        return StreamingResponse(io_buf, media_type="image/jpeg")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting frame: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/camera/capture-face", response_model=FaceCaptureResponse)
def capture_and_identify_face(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Capture a frame, detect the most prominent face, and identify/create partner.

    This endpoint:
    1. Captures a frame from the camera
    2. Detects the largest face
    3. Extracts face embedding
    4. Searches for matching partner in database
    5. Creates new partner if no match found
    """
    try:
        if not camera_service.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Camera is not active. Start camera first."
            )

        # Ensure user exists (auto-create placeholder if missing)
        ensure_user_exists(user_id, db)

        # Capture and identify face
        result = camera_service.capture_and_identify_face()

        if result is None:
            return FaceCaptureResponse(
                success=False,
                partner_id=None,
                partner_name=None,
                is_new_partner=False,
                face_detected=False,
                similarity_score=None,
                message="No face detected in frame"
            )

        face_img, embedding, face_info = result

        # Save face image temporarily
        temp_filename = f"temp_face_{uuid.uuid4()}.jpg"
        temp_path = camera_service.save_face_image(face_img, temp_filename)

        # Search for similar faces in database
        similar_faces = find_similar_faces(
            image_path=temp_path,
            db=db,
            threshold=0.6,  # 60% similarity threshold
            top_k=1
        )

        if similar_faces and len(similar_faces) > 0:
            # Found matching partner
            partner, similarity = similar_faces[0]

            # Update partner's image with latest capture
            partner.image_path = temp_path
            partner.image_embedding = embedding
            db.commit()

            logger.info(f"Identified existing partner: {partner.name} (ID: {partner.id}, similarity: {similarity:.2f})")

            return FaceCaptureResponse(
                success=True,
                partner_id=partner.id,
                partner_name=partner.name,
                is_new_partner=False,
                face_detected=True,
                similarity_score=similarity,
                message=f"Identified partner: {partner.name}"
            )

        else:
            # Create new partner
            new_partner = ConversationPartner(
                id=get_next_id(db, ConversationPartner),
                user_id=user_id,
                name=f"Unknown Person {uuid.uuid4().hex[:8]}",
                image_path=temp_path,
                image_embedding=embedding,
                notes="Automatically created from face capture"
            )

            db.add(new_partner)
            db.commit()
            db.refresh(new_partner)

            logger.info(f"Created new partner: {new_partner.name} (ID: {new_partner.id})")

            return FaceCaptureResponse(
                success=True,
                partner_id=new_partner.id,
                partner_name=new_partner.name,
                is_new_partner=True,
                face_detected=True,
                similarity_score=None,
                message=f"New partner created: {new_partner.name}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error capturing face: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Session Endpoints

@router.post("/start", response_model=SessionResponse)
def start_session(
    request: SessionStartRequest,
    db: Session = Depends(get_db)
):
    """Start a new conversation session with audio transcription."""
    try:
        # Ensure user exists (auto-create placeholder if missing)
        ensure_user_exists(request.user_id, db)

        # Verify partner exists
        partner = db.query(ConversationPartner).filter(
            ConversationPartner.id == request.partner_id
        ).first()

        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Partner {request.partner_id} not found"
            )

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Create session
        session = session_manager.create_session(
            session_id=session_id,
            user_id=request.user_id,
            partner_id=request.partner_id,
            deepgram_api_key=request.deepgram_api_key,
            db=db
        )

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create session"
            )

        stats = session.get_statistics()

        return SessionResponse(
            session_id=stats['session_id'],
            user_id=stats['user_id'],
            partner_id=stats['partner_id'],
            conversation_id=stats['conversation_id'],
            is_running=stats['is_running'],
            elapsed_seconds=stats['elapsed_seconds'],
            elapsed_formatted=stats['elapsed_formatted'],
            message_count=stats['message_count']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/stop/{session_id}")
def stop_session(session_id: str):
    """Stop an active conversation session."""
    try:
        success = session_manager.stop_session(session_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        return {"message": f"Session {session_id} stopped successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/list", response_model=SessionListResponse)
def list_sessions():
    """List all active sessions."""
    try:
        all_sessions = session_manager.get_all_sessions()

        sessions = [
            SessionResponse(
                session_id=s['session_id'],
                user_id=s['user_id'],
                partner_id=s['partner_id'],
                conversation_id=s['conversation_id'],
                is_running=s['is_running'],
                elapsed_seconds=s['elapsed_seconds'],
                elapsed_formatted=s['elapsed_formatted'],
                message_count=s['message_count']
            )
            for s in all_sessions
        ]

        return SessionListResponse(sessions=sessions)

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str):
    """Get details of a specific session."""
    try:
        session = session_manager.get_session(session_id)

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        stats = session.get_statistics()

        return SessionResponse(
            session_id=stats['session_id'],
            user_id=stats['user_id'],
            partner_id=stats['partner_id'],
            conversation_id=stats['conversation_id'],
            is_running=stats['is_running'],
            elapsed_seconds=stats['elapsed_seconds'],
            elapsed_formatted=stats['elapsed_formatted'],
            message_count=stats['message_count']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{session_id}/transcripts")
def get_session_transcripts(
    session_id: str,
    max_lines: int = 20,
    db: Session = Depends(get_db)
):
    """Get recent transcripts from a session."""
    try:
        session = session_manager.get_session(session_id)

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        transcripts = session.get_recent_transcripts(max_lines=max_lines)

        partner_name = None
        if session and session.partner_id:
            partner = db.query(ConversationPartner).filter(
                ConversationPartner.id == session.partner_id
            ).first()
            if partner:
                partner_name = partner.name

        return {
            "session_id": session_id,
            "transcripts": transcripts,
            "total_count": len(session.transcripts),
            "detected_partner_name": session.detected_partner_name,
            "partner_name": partner_name
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transcripts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
