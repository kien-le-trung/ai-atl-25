from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ExtractedFact(Base):
    """Key facts extracted from conversations about partners."""

    __tablename__ = "extracted_facts"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("conversation_partners.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    category = Column(String, nullable=False)  # e.g., 'interest', 'preference', 'life_event', 'relationship'
    fact_key = Column(String, nullable=False)  # e.g., 'favorite_food', 'job_title'
    fact_value = Column(Text, nullable=False)  # The actual information
    confidence = Column(Float, default=1.0)  # Confidence score (0-1)
    source_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    is_current = Column(Boolean, default=True)  # False if superseded by newer information
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    partner = relationship("ConversationPartner", back_populates="extracted_facts")
