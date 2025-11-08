from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Association table for many-to-many relationship between conversations and topics
conversation_topics = Table(
    'conversation_topics',
    Base.metadata,
    Column('conversation_id', Integer, ForeignKey('conversations.id'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topics.id'), primary_key=True),
    Column('relevance_score', Integer, default=5),  # 1-10 scale
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)


class Topic(Base):
    """Topics discussed in conversations."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=True)  # e.g., 'work', 'hobby', 'family'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversations = relationship("Conversation", secondary=conversation_topics, back_populates="topics")
