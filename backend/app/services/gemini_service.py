import google.generativeai as genai
from typing import List, Dict, Any
import json
from app.core.config import settings

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)


class GeminiService:
    """Service for interacting with Google Gemini AI."""

    def __init__(self):
        # Use gemini-2.0-flash - fast and efficient
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')

    async def analyze_conversation(
        self,
        messages: List[Dict[str, str]],
        partner_name: str
    ) -> Dict[str, Any]:
        """
        Analyze a conversation and extract valuable information.

        Args:
            messages: List of messages with 'sender' and 'content' keys
            partner_name: Name of the conversation partner

        Returns:
            Dictionary containing extracted information
        """
        # Format conversation for analysis
        conversation_text = self._format_conversation(messages)

        prompt = f"""
Analyze the following conversation with {partner_name} and extract valuable information that would help improve future conversations.

{conversation_text}

Please provide a comprehensive analysis in JSON format with the following structure:

{{
    "summary": "A brief 2-3 sentence summary of the conversation",
    "main_topics": ["topic1", "topic2", "topic3"],
    "extracted_facts": [
        {{
            "category": "interest|preference|life_event|relationship|work|personal",
            "fact_key": "brief_key_name",
            "fact_value": "the actual information",
            "confidence": 0.0-1.0
        }}
    ],
    "sentiment": "positive|neutral|negative",
    "key_insights": ["insight1", "insight2"],
    "suggested_topics": ["topic1", "topic2", "topic3"],
    "suggested_questions": ["question1", "question2", "question3"],
    "action_items": ["action1", "action2"]
}}

Focus on extracting:
1. Personal interests and hobbies
2. Preferences (food, activities, etc.)
3. Important life events mentioned
4. Work-related information
5. Relationships and connections
6. Goals and aspirations
7. Challenges or problems discussed
8. Upcoming events or plans

Be thorough and extract as much useful information as possible while maintaining high confidence scores.
"""

        try:
            return self._generate_json_response(prompt)
        except Exception as e:
            raise Exception(f"Failed to analyze conversation: {str(e)}")

    async def generate_conversation_starters(
        self,
        partner_name: str,
        extracted_facts: List[Dict[str, Any]],
        recent_topics: List[str]
    ) -> Dict[str, List[str]]:
        """
        Generate personalized conversation starters based on past interactions.

        Args:
            partner_name: Name of the conversation partner
            extracted_facts: List of facts about the partner
            recent_topics: Recently discussed topics

        Returns:
            Dictionary with conversation starters and questions
        """
        facts_text = self._format_facts(extracted_facts)
        topics_text = ", ".join(recent_topics) if recent_topics else "No recent topics"

        prompt = f"""
Based on the following information about {partner_name}, generate personalized conversation starters and questions.

Known Facts:
{facts_text}

Recently Discussed Topics:
{topics_text}

Generate a JSON response with:
{{
    "conversation_starters": [
        "5 natural conversation starters that reference their interests or recent topics"
    ],
    "follow_up_questions": [
        "5 thoughtful follow-up questions about things they've mentioned before"
    ],
    "new_topic_suggestions": [
        "5 new topics they might enjoy based on their interests"
    ]
}}

Make the suggestions natural, friendly, and show genuine interest. Avoid being too formal or generic.
"""

        try:
            return self._generate_json_response(prompt)
        except Exception as e:
            # Return default suggestions if generation fails
            return {
                "conversation_starters": [f"How have you been, {partner_name}?"],
                "follow_up_questions": ["What have you been up to lately?"],
                "new_topic_suggestions": ["Recent events", "Hobbies", "Plans"],
                "error": str(e)
            }

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Gemini.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding
        """
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")

    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Format messages into a readable conversation."""
        formatted = []
        for msg in messages:
            if msg.get('is_transcript'):
                formatted.append(msg['content'])
            else:
                sender = "You" if msg['sender'] == 'user' else msg.get('partner_name', 'Partner')
                formatted.append(f"{sender}: {msg['content']}")
        return "\n".join(formatted)

    def _format_facts(self, facts: List[Dict[str, Any]]) -> str:
        """Format extracted facts into readable text."""
        if not facts:
            return "No previous facts available"

        formatted = []
        for fact in facts:
            category = fact.get('category', 'general')
            key = fact.get('fact_key', '')
            value = fact.get('fact_value', '')
            formatted.append(f"- [{category}] {key}: {value}")
        return "\n".join(formatted)

    def _generate_json_response(self, prompt: str, retry: bool = True) -> Dict[str, Any]:
        response = self.model.generate_content(prompt)
        result_text = response.text.strip()

        cleaned = self._strip_code_fences(result_text)
        try:
            result = json.loads(cleaned)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            if retry:
                clarification_prompt = (
                    "Your previous response was not valid JSON. "
                    "Respond again strictly as JSON matching the requested schema, with no commentary."
                )
                return self._generate_json_response(
                    prompt + "\n" + clarification_prompt,
                    retry=False
                )

        return {
            "summary": result_text[:200],
            "main_topics": [],
            "extracted_facts": [],
            "sentiment": "neutral",
            "key_insights": [],
            "suggested_topics": [],
            "suggested_questions": [],
            "action_items": [],
            "raw_response": result_text
        }

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()


# Singleton instance
gemini_service = GeminiService()
