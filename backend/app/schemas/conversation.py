from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    sender: str  # 'user' or 'partner'
    content: str
    timestamp: Optional[datetime] = None


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    conversation_id: int
    sender: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    partner_id: int
    title: Optional[str] = None
    messages: List[MessageCreate]


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: int
    user_id: int
    partner_id: int
    title: Optional[str]
    summary: Optional[str]
    is_analyzed: bool
    started_at: datetime
    ended_at: Optional[datetime]
    created_at: datetime
    full_transcript: Optional[str] = None

    class Config:
        from_attributes = True


class FactResponse(BaseModel):
    """Schema for extracted fact response."""
    id: int
    category: str
    fact_key: str
    fact_value: str
    confidence: float
    extracted_at: str


class ConversationDetailResponse(ConversationResponse):
    """Schema for detailed conversation response with messages."""
    messages: List[MessageResponse]
    topics: List[str] = []
    extracted_facts: List[FactResponse] = []


class AnalysisResponse(BaseModel):
    """Schema for conversation analysis response."""
    summary: str
    main_topics: List[str]
    extracted_facts: List[Dict[str, Any]]
    sentiment: str
    key_insights: List[str]
    suggested_topics: List[str]
    suggested_questions: List[str]
    action_items: List[str]


class SuggestionsResponse(BaseModel):
    """Schema for conversation suggestions response."""
    partner_name: str
    known_facts_count: int
    recent_topics: List[str]
    conversation_starters: List[str]
    follow_up_questions: List[str]
    new_topic_suggestions: List[str]

