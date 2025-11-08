"""
API endpoints for partner profile management and analysis.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging

from app.core.database import get_db
from app.core.config import settings
from app.services.profile_service import ProfileBuilder
from app.models.conversation_partner import ConversationPartner

router = APIRouter(prefix="/api/profiles", tags=["profiles"])
logger = logging.getLogger(__name__)


# Request/Response Models
class AnalyzeConversationRequest(BaseModel):
    conversation_id: int
    gemini_api_key: Optional[str] = None


class AnalyzeConversationResponse(BaseModel):
    conversation_id: int
    facts_extracted: int
    topics_identified: int
    summary: Optional[str]


class PartnerProfileResponse(BaseModel):
    partner_id: int
    partner_name: str
    email: Optional[str]
    phone: Optional[str]
    relationship: Optional[str]
    notes: Optional[str]
    statistics: Dict
    facts: Dict
    topics: List[str]
    last_conversation: Optional[Dict]
    created_at: Optional[str]


class InsightsResponse(BaseModel):
    partner_id: int
    partner_name: str
    suggestions: List[str]
    profile_summary: Dict


# Endpoints

@router.post("/analyze-conversation", response_model=AnalyzeConversationResponse)
def analyze_conversation(
    request: AnalyzeConversationRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a conversation to extract facts, topics, and generate summary.

    This will:
    1. Extract key facts about the partner
    2. Identify main topics discussed
    3. Generate a conversation summary
    4. Save all data to database
    """
    try:
        api_key = request.gemini_api_key or settings.GOOGLE_API_KEY

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gemini API key required. Provide via request or environment variable."
            )

        # Create profile builder
        builder = ProfileBuilder(gemini_api_key=api_key)

        # Analyze conversation
        result = builder.analyze_conversation(request.conversation_id, db)

        return AnalyzeConversationResponse(
            conversation_id=result['conversation_id'],
            facts_extracted=result['facts_extracted'],
            topics_identified=result['topics_identified'],
            summary=result['summary']
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error analyzing conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{partner_id}", response_model=PartnerProfileResponse)
def get_partner_profile(
    partner_id: int,
    gemini_api_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive profile for a partner based on all conversations.

    Returns:
    - Partner information
    - Conversation statistics
    - Extracted facts grouped by category
    - Topics discussed
    - Most recent conversation
    """
    try:
        # Verify partner exists
        partner = db.query(ConversationPartner).filter(
            ConversationPartner.id == partner_id
        ).first()

        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Partner {partner_id} not found"
            )

        api_key = gemini_api_key or settings.GOOGLE_API_KEY

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gemini API key required"
            )

        # Build profile
        builder = ProfileBuilder(gemini_api_key=api_key)
        profile = builder.build_partner_profile(partner_id, db)

        return PartnerProfileResponse(**profile)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{partner_id}/insights", response_model=InsightsResponse)
def get_conversation_insights(
    partner_id: int,
    gemini_api_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get AI-generated insights and conversation suggestions for a partner.

    Returns intelligent suggestions for future conversations based on
    past interactions, extracted facts, and topics discussed.
    """
    try:
        # Verify partner exists
        partner = db.query(ConversationPartner).filter(
            ConversationPartner.id == partner_id
        ).first()

        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Partner {partner_id} not found"
            )

        api_key = gemini_api_key or settings.GOOGLE_API_KEY

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gemini API key required"
            )

        # Get insights
        builder = ProfileBuilder(gemini_api_key=api_key)
        insights = builder.get_conversation_insights(partner_id, db)

        return InsightsResponse(**insights)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{partner_id}/analyze-all")
def analyze_all_conversations(
    partner_id: int,
    gemini_api_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze all unanalyzed conversations for a partner.

    This is useful for batch processing after multiple conversation sessions.
    """
    try:
        from app.models.conversation import Conversation

        # Verify partner exists
        partner = db.query(ConversationPartner).filter(
            ConversationPartner.id == partner_id
        ).first()

        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Partner {partner_id} not found"
            )

        api_key = gemini_api_key or settings.GOOGLE_API_KEY

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gemini API key required"
            )

        # Get all unanalyzed conversations
        conversations = db.query(Conversation).filter(
            Conversation.partner_id == partner_id,
            Conversation.is_analyzed == False
        ).all()

        if not conversations:
            return {
                "message": f"No unanalyzed conversations found for partner {partner_id}",
                "analyzed_count": 0
            }

        # Analyze each conversation
        builder = ProfileBuilder(gemini_api_key=api_key)
        analyzed_count = 0

        for conversation in conversations:
            try:
                builder.analyze_conversation(conversation.id, db)
                analyzed_count += 1
            except Exception as e:
                logger.error(f"Error analyzing conversation {conversation.id}: {e}")

        return {
            "message": f"Analyzed {analyzed_count} conversations for partner {partner_id}",
            "analyzed_count": analyzed_count,
            "total_conversations": len(conversations)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
