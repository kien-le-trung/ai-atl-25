"""
Memory frontend API endpoints.
This module provides API endpoints that match the memory frontend's expectations.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models import ConversationPartner, Conversation
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["memory"])


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    try:
        # Count total conversations
        total = db.query(Conversation).count()
        
        # Count conversations this week
        week_ago = datetime.now() - timedelta(days=7)
        this_week = db.query(Conversation).filter(
            Conversation.started_at >= week_ago
        ).count()
        
        # For now, return a fixed recognition accuracy
        # In production, this would be calculated from actual recognition data
        recognition_accuracy = 85.0
        
        return {
            "total": total,
            "thisWeek": this_week,
            "recognitionAccuracy": recognition_accuracy
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")


@router.get("/conversations")
async def get_conversations_with_persons(db: Session = Depends(get_db)):
    """Get all conversations with person information."""
    try:
        conversations = db.query(Conversation).order_by(
            Conversation.started_at.desc()
        ).limit(50).all()
        
        result = []
        for conv in conversations:
            # Get the partner (person) info
            partner = db.query(ConversationPartner).filter(
                ConversationPartner.id == conv.partner_id
            ).first()
            
            if partner:
                result.append({
                    "id": str(conv.id),
                    "personId": str(partner.id),
                    "location": conv.location or "Unknown",
                    "status": "completed" if conv.full_transcript else "new",
                    "transcript": conv.full_transcript or "",
                    "summary": conv.summary or "",
                    "sentiment": "neutral",
                    "sentimentScore": 70,
                    "talkTimeRatio": "50/50",
                    "topics": [],
                    "createdAt": conv.started_at.isoformat() if conv.started_at else datetime.now().isoformat(),
                    "updatedAt": conv.started_at.isoformat() if conv.started_at else datetime.now().isoformat(),
                    "person": {
                        "id": str(partner.id),
                        "name": partner.name,
                        "photoUrl": partner.image_path or "",
                        "company": "",
                        "school": "",
                        "email": partner.email or "",
                        "lastMeetingDate": conv.started_at.isoformat() if conv.started_at else None,
                        "lastTopic": "",
                        "createdAt": partner.created_at.isoformat() if partner.created_at else datetime.now().isoformat(),
                    }
                })
        
        return result
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")


@router.get("/conversations/{conversation_id}")
async def get_conversation_with_person(conversation_id: str, db: Session = Depends(get_db)):
    """Get a specific conversation with person information."""
    try:
        # Try to convert to int for database query
        try:
            conv_id = int(conversation_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        partner = db.query(ConversationPartner).filter(
            ConversationPartner.id == conv.partner_id
        ).first()
        
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        
        return {
            "id": str(conv.id),
            "personId": str(partner.id),
            "location": conv.location or "Unknown",
            "status": "completed" if conv.full_transcript else "new",
            "transcript": conv.full_transcript or "",
            "summary": conv.summary or "",
            "sentiment": "neutral",
            "sentimentScore": 70,
            "talkTimeRatio": "50/50",
            "topics": [],
            "createdAt": conv.started_at.isoformat() if conv.started_at else datetime.now().isoformat(),
            "updatedAt": conv.started_at.isoformat() if conv.started_at else datetime.now().isoformat(),
            "person": {
                "id": str(partner.id),
                "name": partner.name,
                "photoUrl": partner.image_path or "",
                "company": "",
                "school": "",
                "email": partner.email or "",
                "lastMeetingDate": conv.started_at.isoformat() if conv.started_at else None,
                "lastTopic": "",
                "createdAt": partner.created_at.isoformat() if partner.created_at else datetime.now().isoformat(),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation")


@router.post("/persons")
async def create_person(
    name: str = Form(...),
    company: Optional[str] = Form(None),
    school: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new person."""
    try:
        partner = ConversationPartner(
            name=name,
            email=email,
            relationship="colleague"
        )
        db.add(partner)
        db.commit()
        db.refresh(partner)
        
        return {
            "id": str(partner.id),
            "name": partner.name,
            "photoUrl": "",
            "company": company or "",
            "school": school or "",
            "email": partner.email or "",
            "createdAt": partner.created_at.isoformat() if partner.created_at else datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error creating person: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create person")


@router.post("/photo-upload")
async def upload_photo(
    photo: UploadFile = File(...),
    name: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a photo and create or match a person."""
    try:
        # For MVP, we'll create a new person for each photo
        # In production, this would use face recognition to match existing persons
        
        person_name = name or f"Person {datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create new person
        partner = ConversationPartner(
            name=person_name,
            relationship="colleague"
        )
        db.add(partner)
        db.commit()
        db.refresh(partner)
        
        # Create conversation
        conversation = Conversation(
            user_id=1,  # Default user
            partner_id=partner.id,
            started_at=datetime.now(),
            location=location or "Unknown"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return {
            "conversation": {
                "id": str(conversation.id),
                "personId": str(partner.id),
                "status": "new",
                "location": location or "Unknown",
            },
            "person": {
                "id": str(partner.id),
                "name": partner.name,
                "photoUrl": "",
            },
            "isMatch": False,
            "message": "New contact created"
        }
    except Exception as e:
        logger.error(f"Error uploading photo: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to upload photo")


@router.get("/insights")
async def get_insights(db: Session = Depends(get_db)):
    """Get insights data."""
    try:
        # Return mock insights for now
        return {
            "talkTimeRatio": "55/45",
            "sentimentScore": 75,
            "topTopics": ["Career", "Technology", "Hobbies"],
            "totalMatches": 0
        }
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights")


@router.post("/conversations")
async def create_conversation(
    personId: str = Form(...),
    location: Optional[str] = Form(None),
    transcript: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    try:
        # Convert personId to int
        try:
            partner_id = int(personId)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid person ID")
        
        conversation = Conversation(
            user_id=1,  # Default user
            partner_id=partner_id,
            started_at=datetime.now(),
            location=location or "Unknown",
            full_transcript=transcript or ""
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return {
            "id": str(conversation.id),
            "personId": str(partner_id),
            "location": location or "Unknown",
            "status": "new",
            "transcript": transcript or "",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.get("/conversation-details/{conversation_id}")
async def get_conversation_details(conversation_id: str, db: Session = Depends(get_db)):
    """Get conversation details."""
    try:
        # Return empty details for now
        return {
            "id": conversation_id,
            "conversationId": conversation_id,
            "school": "",
            "company": "",
            "experiences": "",
            "hobbies": "",
            "contacts": "",
        }
    except Exception as e:
        logger.error(f"Error getting conversation details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation details")


@router.get("/conversations/{conversation_id}/follow-ups")
async def get_follow_ups(conversation_id: str, db: Session = Depends(get_db)):
    """Get follow-up actions for a conversation."""
    try:
        # Return empty list for now
        return []
    except Exception as e:
        logger.error(f"Error getting follow-ups: {e}")
        raise HTTPException(status_code=500, detail="Failed to get follow-ups")
