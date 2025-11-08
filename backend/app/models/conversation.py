from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON
from app.core.database import Base


class Conversation(Base):
    """Conversation session model."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, server_default=text("nextval('conversations_id_seq')"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("conversation_partners.id"), nullable=False)
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    is_analyzed = Column(Boolean, default=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Vector embedding for semantic search (4096 dimensions) stored as JSON array
    embedding = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="conversations")
    partner = relationship("ConversationPartner", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    topics = relationship("Topic", secondary="conversation_topics", back_populates="conversations")


class Message(Base):
    """Individual message in a conversation."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, server_default=text("nextval('messages_id_seq')"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender = Column(String, nullable=False)  # 'user' or 'partner'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
