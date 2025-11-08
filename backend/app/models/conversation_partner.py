from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship as sa_relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON
from app.core.database import Base


class ConversationPartner(Base):
    """People that users have conversations with."""

    __tablename__ = "conversation_partners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    relationship = Column(String, nullable=True)  # Relationship to user (friend, colleague, etc.)
    image_url = Column(String, nullable=True)  # URL/path to partner's image (legacy)
    image_path = Column(String, nullable=True)  # Local path to uploaded face image
    image_embedding = Column(JSON, nullable=True)  # 4096-dim vector for face recognition stored as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = sa_relationship("User", back_populates="conversation_partners")
    conversations = sa_relationship("Conversation", back_populates="partner")
    extracted_facts = sa_relationship("ExtractedFact", back_populates="partner")
