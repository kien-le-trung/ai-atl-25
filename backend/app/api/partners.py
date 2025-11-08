from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import ConversationPartner
from app.schemas import PartnerCreate, PartnerUpdate, PartnerResponse
from app.services import face_service
from app.utils.db_helpers import get_next_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/partners", tags=["partners"])


@router.post("/", response_model=PartnerResponse, status_code=201)
def create_partner(
    partner: PartnerCreate,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Create a new conversation partner."""
    db_partner = ConversationPartner(
        id=get_next_id(db, ConversationPartner),
        user_id=user_id,
        **partner.model_dump()
    )
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    return db_partner


@router.get("/", response_model=List[PartnerResponse])
def list_partners(
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """List all conversation partners for the user."""
    partners = db.query(ConversationPartner).filter(
        ConversationPartner.user_id == user_id
    ).all()
    return partners


@router.get("/{partner_id}", response_model=PartnerResponse)
def get_partner(
    partner_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Get a specific conversation partner."""
    partner = db.query(ConversationPartner).filter(
        ConversationPartner.id == partner_id,
        ConversationPartner.user_id == user_id
    ).first()

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    return partner


@router.put("/{partner_id}", response_model=PartnerResponse)
def update_partner(
    partner_id: int,
    partner_update: PartnerUpdate,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Update a conversation partner."""
    partner = db.query(ConversationPartner).filter(
        ConversationPartner.id == partner_id,
        ConversationPartner.user_id == user_id
    ).first()

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    update_data = partner_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(partner, field, value)

    db.commit()
    db.refresh(partner)
    return partner


@router.delete("/{partner_id}", status_code=204)
def delete_partner(
    partner_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Delete a conversation partner."""
    partner = db.query(ConversationPartner).filter(
        ConversationPartner.id == partner_id,
        ConversationPartner.user_id == user_id
    ).first()

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    db.delete(partner)
    db.commit()
    return None


@router.post("/{partner_id}/upload-image", response_model=PartnerResponse)
async def upload_partner_image(
    partner_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Upload a face image for a conversation partner and extract embeddings."""
    # Verify partner exists and belongs to user
    partner = db.query(ConversationPartner).filter(
        ConversationPartner.id == partner_id,
        ConversationPartner.user_id == user_id
    ).first()

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read and save image
        image_data = await image.read()
        image_path = face_service.save_face_image(image_data, image.filename)

        # Extract face embedding
        embedding = face_service.extract_face_embedding(image_path)

        if embedding is None:
            raise HTTPException(
                status_code=400,
                detail="No face detected in image. Please upload a clear photo with a visible face."
            )

        # Update partner with embedding and image path
        partner.image_path = image_path
        partner.image_embedding = embedding.tolist()

        db.commit()
        db.refresh(partner)

        return partner

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading partner image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing image")


@router.post("/search-by-face")
async def search_partners_by_face(
    image: UploadFile = File(...),
    threshold: float = Form(0.6),
    top_k: int = Form(5),
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Search for conversation partners by uploading a face image."""
    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Save temporary image
        image_data = await image.read()
        temp_path = face_service.save_face_image(image_data, image.filename)

        # Find similar faces
        results = face_service.find_similar_faces(
            image_path=temp_path,
            db=db,
            threshold=threshold,
            top_k=top_k
        )

        # Filter by user_id
        user_results = [
            {
                "partner": PartnerResponse.model_validate(partner),
                "similarity": similarity
            }
            for partner, similarity in results
            if partner.user_id == user_id
        ]

        return {
            "query_image": temp_path,
            "results": user_results,
            "count": len(user_results)
        }

    except Exception as e:
        logger.error(f"Error searching by face: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing image")


@router.post("/create-with-image", response_model=PartnerResponse, status_code=201)
async def create_partner_with_image(
    name: str = Form(...),
    relationship: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Create a new conversation partner with optional face image."""
    try:
        # Create partner
        db_partner = ConversationPartner(
            user_id=user_id,
            name=name,
            relationship=relationship,
            notes=notes
        )

        # If image provided, process it
        if image and image.content_type.startswith("image/"):
            image_data = await image.read()
            image_path = face_service.save_face_image(image_data, image.filename)

            # Extract face embedding
            embedding = face_service.extract_face_embedding(image_path)

            if embedding is not None:
                db_partner.image_path = image_path
                db_partner.image_embedding = embedding.tolist()
            else:
                logger.warning(f"No face detected in image for partner {name}")

        db.add(db_partner)
        db.commit()
        db.refresh(db_partner)

        return db_partner

    except Exception as e:
        logger.error(f"Error creating partner with image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating partner")
