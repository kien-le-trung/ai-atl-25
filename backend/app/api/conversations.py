from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Conversation
from app.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    AnalysisResponse,
    MessageResponse
)
from app.services import conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Create a new conversation with messages."""
    messages_data = [msg.model_dump() for msg in conversation.messages]

    db_conversation = await conversation_service.create_conversation(
        db=db,
        user_id=user_id,
        partner_id=conversation.partner_id,
        messages=messages_data,
        title=conversation.title
    )

    return db_conversation


@router.get("/", response_model=List[ConversationResponse])
def list_conversations(
    partner_id: int = None,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """List all conversations for the user, optionally filtered by partner."""
    query = db.query(Conversation).filter(Conversation.user_id == user_id)

    if partner_id:
        query = query.filter(Conversation.partner_id == partner_id)

    conversations = query.order_by(Conversation.started_at.desc()).all()
    return conversations


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Get a specific conversation with all messages."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Format response
    return {
        **conversation.__dict__,
        "messages": conversation.messages,
        "topics": [topic.name for topic in conversation.topics]
    }


@router.post("/{conversation_id}/analyze", response_model=AnalysisResponse)
async def analyze_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Analyze a conversation and extract insights using Gemini AI."""
    import traceback

    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    try:
        print(f"Starting analysis for conversation {conversation_id}")
        analysis = await conversation_service.analyze_and_store_insights(
            db=db,
            conversation_id=conversation_id
        )
        print(f"Analysis completed successfully")
        return analysis
    except ValueError as e:
        print(f"ValueError during analysis: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Exception during analysis: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # TODO: Get from authentication
):
    """Delete a conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conversation)
    db.commit()
    return None
