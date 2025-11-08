from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import SuggestionsResponse, FactResponse
from app.services import conversation_service

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


@router.get("/{partner_id}", response_model=SuggestionsResponse)
async def get_conversation_suggestions(
    partner_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """
    Get personalized conversation suggestions for a specific partner.

    This endpoint analyzes past conversations and extracted facts to generate:
    - Conversation starters
    - Follow-up questions
    - New topic suggestions
    """
    try:
        suggestions = await conversation_service.get_conversation_suggestions(
            db=db,
            user_id=user_id,
            partner_id=partner_id
        )
        return suggestions
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}")


@router.get("/{partner_id}/facts", response_model=List[FactResponse])
def get_partner_facts(
    partner_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """
    Get all extracted facts about a conversation partner.

    Returns all current facts organized by category with confidence scores.
    """
    try:
        facts = conversation_service.get_partner_facts(
            db=db,
            user_id=user_id,
            partner_id=partner_id
        )
        return facts
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve facts: {str(e)}")
