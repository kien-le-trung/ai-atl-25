from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models import Conversation, Message, ExtractedFact, Topic, ConversationPartner
from app.services.gemini_service import gemini_service
from sqlalchemy import desc


class ConversationService:
    """Service for managing conversations and extracting knowledge."""

    async def create_conversation(
        self,
        db: Session,
        user_id: int,
        partner_id: int,
        messages: List[Dict[str, str]],
        title: Optional[str] = None
    ) -> Conversation:
        """
        Create a new conversation with messages.

        Args:
            db: Database session
            user_id: ID of the user
            partner_id: ID of the conversation partner
            messages: List of messages with 'sender' and 'content'
            title: Optional conversation title

        Returns:
            Created conversation object
        """
        # Create conversation
        conversation = Conversation(
            user_id=user_id,
            partner_id=partner_id,
            title=title,
            started_at=datetime.utcnow()
        )
        db.add(conversation)
        db.flush()

        # Add messages
        for msg_data in messages:
            message = Message(
                conversation_id=conversation.id,
                sender=msg_data['sender'],
                content=msg_data['content'],
                timestamp=msg_data.get('timestamp', datetime.utcnow())
            )
            db.add(message)

        db.commit()
        db.refresh(conversation)
        return conversation

    async def analyze_and_store_insights(
        self,
        db: Session,
        conversation_id: int
    ) -> Dict[str, Any]:
        """
        Analyze a conversation and store extracted insights.

        Args:
            db: Database session
            conversation_id: ID of the conversation to analyze

        Returns:
            Analysis results
        """
        # Get conversation with messages
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        if conversation.is_analyzed:
            raise ValueError(f"Conversation {conversation_id} already analyzed")

        # Get messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp).all()

        # Format messages for analysis
        message_data = [
            {
                'sender': msg.sender,
                'content': msg.content,
                'timestamp': msg.timestamp
            }
            for msg in messages
        ]

        # Get partner name
        partner = db.query(ConversationPartner).filter(
            ConversationPartner.id == conversation.partner_id
        ).first()

        # Analyze with Gemini
        analysis = await gemini_service.analyze_conversation(
            messages=message_data,
            partner_name=partner.name
        )

        # Store summary
        conversation.summary = analysis.get('summary', '')
        conversation.is_analyzed = True

        # Store extracted facts
        for fact_data in analysis.get('extracted_facts', []):
            fact = ExtractedFact(
                partner_id=conversation.partner_id,
                conversation_id=conversation.id,
                category=fact_data.get('category', 'general'),
                fact_key=fact_data.get('fact_key', ''),
                fact_value=fact_data.get('fact_value', ''),
                confidence=fact_data.get('confidence', 0.8)
            )
            db.add(fact)

        # Store topics
        for topic_name in analysis.get('main_topics', []):
            # Check if topic exists
            topic = db.query(Topic).filter(Topic.name == topic_name).first()
            if not topic:
                topic = Topic(name=topic_name)
                db.add(topic)
                db.flush()

            # Associate topic with conversation
            if topic not in conversation.topics:
                conversation.topics.append(topic)

        # Generate and store embedding for semantic search
        conversation_text = " ".join([msg['content'] for msg in message_data])
        summary_text = f"{conversation.summary} {conversation_text[:500]}"

        try:
            embedding = await gemini_service.generate_embedding(summary_text)
            conversation.embedding = embedding
        except Exception as e:
            print(f"Failed to generate embedding: {e}")

        conversation.ended_at = datetime.utcnow()
        db.commit()

        return analysis

    async def get_conversation_suggestions(
        self,
        db: Session,
        user_id: int,
        partner_id: int
    ) -> Dict[str, Any]:
        """
        Get personalized conversation suggestions based on past interactions.

        Args:
            db: Database session
            user_id: ID of the user
            partner_id: ID of the conversation partner

        Returns:
            Conversation suggestions and questions
        """
        # Get partner
        partner = db.query(ConversationPartner).filter(
            ConversationPartner.id == partner_id,
            ConversationPartner.user_id == user_id
        ).first()

        if not partner:
            raise ValueError(f"Partner {partner_id} not found")

        # Get extracted facts
        facts = db.query(ExtractedFact).filter(
            ExtractedFact.partner_id == partner_id,
            ExtractedFact.is_current == True
        ).order_by(desc(ExtractedFact.confidence)).limit(20).all()

        fact_data = [
            {
                'category': fact.category,
                'fact_key': fact.fact_key,
                'fact_value': fact.fact_value,
                'confidence': fact.confidence
            }
            for fact in facts
        ]

        # Get recent topics
        recent_conversations = db.query(Conversation).filter(
            Conversation.partner_id == partner_id,
            Conversation.is_analyzed == True
        ).order_by(desc(Conversation.started_at)).limit(5).all()

        topics = set()
        for conv in recent_conversations:
            for topic in conv.topics:
                topics.add(topic.name)

        # Generate suggestions with Gemini
        suggestions = await gemini_service.generate_conversation_starters(
            partner_name=partner.name,
            extracted_facts=fact_data,
            recent_topics=list(topics)
        )

        return {
            "partner_name": partner.name,
            "known_facts_count": len(fact_data),
            "recent_topics": list(topics),
            **suggestions
        }

    def get_partner_facts(
        self,
        db: Session,
        user_id: int,
        partner_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all current facts about a conversation partner.

        Args:
            db: Database session
            user_id: ID of the user
            partner_id: ID of the conversation partner

        Returns:
            List of facts
        """
        # Verify partner belongs to user
        partner = db.query(ConversationPartner).filter(
            ConversationPartner.id == partner_id,
            ConversationPartner.user_id == user_id
        ).first()

        if not partner:
            raise ValueError(f"Partner {partner_id} not found")

        # Get facts
        facts = db.query(ExtractedFact).filter(
            ExtractedFact.partner_id == partner_id,
            ExtractedFact.is_current == True
        ).order_by(
            desc(ExtractedFact.confidence),
            desc(ExtractedFact.extracted_at)
        ).all()

        return [
            {
                "id": fact.id,
                "category": fact.category,
                "fact_key": fact.fact_key,
                "fact_value": fact.fact_value,
                "confidence": fact.confidence,
                "extracted_at": fact.extracted_at.isoformat()
            }
            for fact in facts
        ]


# Singleton instance
conversation_service = ConversationService()
