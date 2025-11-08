from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import ConversationPartner
from app.schemas import PartnerCreate, PartnerUpdate, PartnerResponse

router = APIRouter(prefix="/partners", tags=["partners"])


@router.post("/", response_model=PartnerResponse, status_code=201)
def create_partner(
    partner: PartnerCreate,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Create a new conversation partner."""
    db_partner = ConversationPartner(
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
