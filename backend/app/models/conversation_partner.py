from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class ConversationPartner(Base):
    """People that users have conversations with."""

    __tablename__ = "conversation_partners"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)  # URL/path to partner's image
    image_embedding = Column(Vector(4096), nullable=True)  # 4096-dim vector for face recognition
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="conversation_partners")
    conversations = relationship("Conversation", back_populates="partner")
    extracted_facts = relationship("ExtractedFact", back_populates="partner")
