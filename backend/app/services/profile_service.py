"""
Profile building service that analyzes conversations and builds partner profiles.
"""
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime
import google.generativeai as genai

from app.models.conversation import Conversation, Message
from app.models.conversation_partner import ConversationPartner
from app.models.extracted_fact import ExtractedFact
from app.models.topic import Topic, conversation_topics

logger = logging.getLogger(__name__)


class ProfileBuilder:
    """Builds and maintains partner profiles from conversation data."""

    def __init__(self, gemini_api_key: str):
        """
        Initialize profile builder with Gemini API.

        Args:
            gemini_api_key: Google Gemini API key for analysis
        """
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def analyze_conversation(
        self,
        conversation_id: int,
        db: Session
    ) -> Dict:
        """
        Analyze a conversation and extract facts, topics, and insights.

        Args:
            conversation_id: Conversation ID to analyze
            db: Database session

        Returns:
            Dictionary with analysis results
        """
        try:
            # Get conversation with messages
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Get all messages
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp).all()

            if not messages:
                logger.warning(f"No messages found for conversation {conversation_id}")
                return {
                    'facts_extracted': 0,
                    'topics_identified': 0,
                    'summary': None
                }

            # Build conversation text
            conversation_text = "\n".join([
                f"{msg.sender}: {msg.content}"
                for msg in messages
            ])

            # Extract facts using Gemini
            facts = self._extract_facts(conversation_text, conversation.partner_id, conversation_id, db)

            # Identify topics
            topics = self._identify_topics(conversation_text, conversation_id, db)

            # Generate summary
            summary = self._generate_summary(conversation_text)

            # Update conversation
            conversation.summary = summary
            conversation.is_analyzed = True
            db.commit()

            logger.info(f"Analyzed conversation {conversation_id}: {len(facts)} facts, {len(topics)} topics")

            return {
                'conversation_id': conversation_id,
                'facts_extracted': len(facts),
                'topics_identified': len(topics),
                'summary': summary,
                'facts': facts,
                'topics': topics
            }

        except Exception as e:
            logger.error(f"Error analyzing conversation {conversation_id}: {e}")
            db.rollback()
            raise

    def _extract_facts(
        self,
        conversation_text: str,
        partner_id: int,
        conversation_id: int,
        db: Session
    ) -> List[ExtractedFact]:
        """
        Extract facts about the partner from conversation text.

        Args:
            conversation_text: Full conversation transcript
            partner_id: Partner ID
            conversation_id: Conversation ID
            db: Database session

        Returns:
            List of extracted facts
        """
        try:
            prompt = f"""
Analyze the following conversation and extract key facts about the person speaking.
Focus on:
- Personal information (name, occupation, location, etc.)
- Interests and hobbies
- Preferences and opinions
- Life events and experiences
- Relationships and family
- Goals and aspirations

For each fact, provide:
1. Category (e.g., 'personal_info', 'interest', 'preference', 'life_event', 'relationship')
2. Fact key (e.g., 'occupation', 'favorite_food', 'hobby')
3. Fact value (the actual information)
4. Confidence (0.0-1.0)

Format as JSON array:
[
  {{"category": "personal_info", "fact_key": "occupation", "fact_value": "software engineer", "confidence": 0.9}},
  ...
]

Conversation:
{conversation_text}

Extract facts (return only valid JSON array):
"""

            response = self.model.generate_content(prompt)
            facts_data = self._parse_json_response(response.text)

            # Save facts to database
            saved_facts = []
            for fact_data in facts_data:
                fact = ExtractedFact(
                    partner_id=partner_id,
                    conversation_id=conversation_id,
                    category=fact_data.get('category', 'unknown'),
                    fact_key=fact_data.get('fact_key', 'unknown'),
                    fact_value=fact_data.get('fact_value', ''),
                    confidence=fact_data.get('confidence', 0.8),
                    is_current=True,
                    extracted_at=datetime.utcnow()
                )

                db.add(fact)
                saved_facts.append(fact)

            db.commit()

            return saved_facts

        except Exception as e:
            logger.error(f"Error extracting facts: {e}")
            return []

    def _identify_topics(
        self,
        conversation_text: str,
        conversation_id: int,
        db: Session
    ) -> List[str]:
        """
        Identify main topics discussed in conversation.

        Args:
            conversation_text: Full conversation transcript
            conversation_id: Conversation ID
            db: Database session

        Returns:
            List of topic names
        """
        try:
            prompt = f"""
Analyze the following conversation and identify the main topics discussed.
Return 3-5 specific topics that were discussed.

Examples: "travel", "work", "family", "food", "technology", "sports", etc.

Format as JSON array of strings:
["topic1", "topic2", "topic3"]

Conversation:
{conversation_text}

Topics (return only valid JSON array):
"""

            response = self.model.generate_content(prompt)
            topics_data = self._parse_json_response(response.text)

            # Save topics to database
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            topic_names = []
            for topic_name in topics_data:
                if not isinstance(topic_name, str):
                    continue

                # Find or create topic
                topic = db.query(Topic).filter(Topic.name == topic_name.lower()).first()

                if not topic:
                    topic = Topic(
                        name=topic_name.lower(),
                        category="general"
                    )
                    db.add(topic)
                    db.flush()

                # Associate topic with conversation
                if conversation and topic not in conversation.topics:
                    conversation.topics.append(topic)

                topic_names.append(topic_name)

            db.commit()

            return topic_names

        except Exception as e:
            logger.error(f"Error identifying topics: {e}")
            return []

    def _generate_summary(self, conversation_text: str) -> str:
        """
        Generate a concise summary of the conversation.

        Args:
            conversation_text: Full conversation transcript

        Returns:
            Summary text
        """
        try:
            prompt = f"""
Summarize the following conversation in 2-3 sentences.
Focus on the main topics discussed and any important points mentioned.

Conversation:
{conversation_text}

Summary:
"""

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Summary unavailable"

    def _parse_json_response(self, response_text: str) -> List:
        """
        Parse JSON from Gemini response, handling markdown code blocks.

        Args:
            response_text: Raw response text

        Returns:
            Parsed JSON data
        """
        import json
        import re

        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}\nResponse: {response_text}")
            return []

    def build_partner_profile(
        self,
        partner_id: int,
        db: Session
    ) -> Dict:
        """
        Build a comprehensive profile for a partner based on all conversations.

        Args:
            partner_id: Partner ID
            db: Database session

        Returns:
            Dictionary with partner profile
        """
        try:
            # Get partner
            partner = db.query(ConversationPartner).filter(
                ConversationPartner.id == partner_id
            ).first()

            if not partner:
                raise ValueError(f"Partner {partner_id} not found")

            # Get all conversations with this partner
            conversations = db.query(Conversation).filter(
                Conversation.partner_id == partner_id,
                Conversation.is_analyzed == True
            ).all()

            # Get all extracted facts
            facts = db.query(ExtractedFact).filter(
                ExtractedFact.partner_id == partner_id,
                ExtractedFact.is_current == True
            ).all()

            # Group facts by category
            facts_by_category = {}
            for fact in facts:
                category = fact.category
                if category not in facts_by_category:
                    facts_by_category[category] = []

                facts_by_category[category].append({
                    'key': fact.fact_key,
                    'value': fact.fact_value,
                    'confidence': fact.confidence,
                    'extracted_at': fact.extracted_at.isoformat()
                })

            # Get all topics discussed
            topics = db.query(Topic).join(
                conversation_topics
            ).join(
                Conversation
            ).filter(
                Conversation.partner_id == partner_id
            ).distinct().all()

            # Calculate conversation statistics
            total_conversations = len(conversations)
            total_messages = sum(len(conv.messages) for conv in conversations)

            # Get most recent conversation
            last_conversation = None
            if conversations:
                last_conv = max(conversations, key=lambda c: c.started_at)
                last_conversation = {
                    'id': last_conv.id,
                    'date': last_conv.started_at.isoformat(),
                    'summary': last_conv.summary
                }

            return {
                'partner_id': partner_id,
                'partner_name': partner.name,
                'email': partner.email,
                'phone': partner.phone,
                'relationship': partner.relationship,
                'notes': partner.notes,
                'statistics': {
                    'total_conversations': total_conversations,
                    'total_messages': total_messages,
                    'total_facts': len(facts),
                    'topics_count': len(topics)
                },
                'facts': facts_by_category,
                'topics': [topic.name for topic in topics],
                'last_conversation': last_conversation,
                'created_at': partner.created_at.isoformat() if partner.created_at else None
            }

        except Exception as e:
            logger.error(f"Error building profile for partner {partner_id}: {e}")
            raise

    def get_conversation_insights(
        self,
        partner_id: int,
        db: Session
    ) -> Dict:
        """
        Get actionable insights for conversations with a partner.

        Args:
            partner_id: Partner ID
            db: Database session

        Returns:
            Dictionary with insights and suggestions
        """
        try:
            profile = self.build_partner_profile(partner_id, db)

            # Generate insights using Gemini
            facts_summary = "\n".join([
                f"{category}: {len(facts)} facts"
                for category, facts in profile['facts'].items()
            ])

            topics_summary = ", ".join(profile['topics'][:10])

            prompt = f"""
Based on this person's profile, suggest 3-5 conversation topics or questions
that would be interesting and relevant for future conversations.

Profile:
- Name: {profile['partner_name']}
- Total conversations: {profile['statistics']['total_conversations']}
- Facts: {facts_summary}
- Topics discussed: {topics_summary}

Suggest topics as a JSON array of strings:
["suggestion1", "suggestion2", "suggestion3"]
"""

            response = self.model.generate_content(prompt)
            suggestions = self._parse_json_response(response.text)

            return {
                'partner_id': partner_id,
                'partner_name': profile['partner_name'],
                'suggestions': suggestions,
                'profile_summary': {
                    'facts_count': profile['statistics']['total_facts'],
                    'topics_count': profile['statistics']['topics_count'],
                    'conversations_count': profile['statistics']['total_conversations']
                }
            }

        except Exception as e:
            logger.error(f"Error getting insights for partner {partner_id}: {e}")
            raise
