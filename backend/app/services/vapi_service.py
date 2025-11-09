"""
Vapi service for making AI-powered phone calls.
"""
import logging
import requests
from typing import Dict, Any, Optional
from vapi import Vapi
from app.core.config import settings

logger = logging.getLogger(__name__)


class VapiService:
    """Service for interacting with Vapi AI phone calls."""

    def __init__(self):
        """Initialize Vapi client."""
        self.api_key = settings.VAPI_API_KEY
        self.assistant_id = settings.VAPI_ASSISTANT_ID
        self.phone_number_id = settings.VAPI_PHONE_NUMBER_ID
        self.client = None

        if self.api_key:
            try:
                self.client = Vapi(token=self.api_key)
                logger.info("Vapi client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Vapi client: {e}")
                self.client = None

    def is_configured(self) -> bool:
        """Check if Vapi is properly configured."""
        return bool(
            self.client and
            self.api_key and
            self.assistant_id and
            self.phone_number_id
        )

    def create_call(
        self,
        phone_number: str,
        assistant_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create and initiate a new call.

        Args:
            phone_number: Customer phone number to call (E.164 format, e.g., +1234567890)
            assistant_overrides: Optional overrides for the assistant (e.g., variable values)

        Returns:
            Dictionary containing call information including call ID

        Raises:
            Exception: If Vapi is not configured or call creation fails
        """
        if not self.is_configured():
            raise Exception(
                "Vapi is not configured. Please set VAPI_API_KEY, "
                "VAPI_ASSISTANT_ID, and VAPI_PHONE_NUMBER_ID in .env"
            )

        # Validate phone number format
        if not phone_number.startswith('+'):
            raise ValueError("Phone number must be in E.164 format (e.g., +1234567890)")

        try:
            logger.info(f"Creating call to {phone_number}")

            resp = self.client.calls.create(
                assistant_id=self.assistant_id,
                phone_number_id=self.phone_number_id,
                customer={"number": phone_number},
                assistant_overrides=assistant_overrides or {}
            )

            call_data = {
                "id": resp.id,
                "status": "initiated",
                "phone_number": phone_number,
                "assistant_id": self.assistant_id
            }

            logger.info(f"Call created successfully: {resp.id}")
            return call_data

        except Exception as e:
            logger.error(f"Failed to create call: {e}")
            raise Exception(f"Failed to create call: {str(e)}")

    def get_call(self, call_id: str) -> Dict[str, Any]:
        """
        Get call details and transcript.

        Args:
            call_id: The Vapi call ID

        Returns:
            Dictionary containing call details and transcript

        Raises:
            Exception: If call retrieval fails
        """
        if not self.api_key:
            raise Exception("Vapi API key not configured")

        try:
            logger.info(f"Retrieving call: {call_id}")

            response = requests.get(
                f"https://api.vapi.ai/call/{call_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=20
            )
            response.raise_for_status()

            call_data = response.json()
            logger.info(f"Call retrieved successfully: {call_id}")

            return {
                "id": call_data.get("id"),
                "status": call_data.get("status"),
                "transcript": call_data.get("transcript", ""),
                "duration": call_data.get("duration"),
                "started_at": call_data.get("startedAt"),
                "ended_at": call_data.get("endedAt"),
                "cost": call_data.get("cost"),
                "metadata": call_data
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve call {call_id}: {e}")
            raise Exception(f"Failed to retrieve call: {str(e)}")

    def list_calls(self, limit: int = 10) -> Dict[str, Any]:
        """
        List recent calls.

        Args:
            limit: Maximum number of calls to return

        Returns:
            Dictionary containing list of calls

        Raises:
            Exception: If listing calls fails
        """
        if not self.api_key:
            raise Exception("Vapi API key not configured")

        try:
            logger.info(f"Listing calls (limit: {limit})")

            response = requests.get(
                "https://api.vapi.ai/call",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"limit": limit},
                timeout=20
            )
            response.raise_for_status()

            calls_data = response.json()
            logger.info(f"Retrieved {len(calls_data)} calls")

            return {
                "calls": calls_data,
                "count": len(calls_data)
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list calls: {e}")
            raise Exception(f"Failed to list calls: {str(e)}")

    def create_call_with_context(
        self,
        phone_number: str,
        person_name: str,
        person_information: str = "",
        conversation_summary: str = ""
    ) -> Dict[str, Any]:
        """
        Create a call with conversation context.

        Args:
            phone_number: Customer phone number (E.164 format)
            person_name: Name of the person being called
            person_information: Information about the person (job, etc.)
            conversation_summary: Summary of previous conversations

        Returns:
            Dictionary containing call information
        """
        assistant_overrides = {
            "variableValues": {
                "person_name": person_name,
                "person_information": person_information,
                "conversation_summary": conversation_summary,
            }
        }

        return self.create_call(
            phone_number=phone_number,
            assistant_overrides=assistant_overrides
        )


# Singleton instance
vapi_service = VapiService()
