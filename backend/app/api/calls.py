"""
API endpoints for Vapi voice AI calls.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.services.vapi_service import vapi_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/calls", tags=["calls"])


class CreateCallRequest(BaseModel):
    """Request model for creating a call."""

    phone_number: str = Field(
        ...,
        description="Customer phone number in E.164 format (e.g., +1234567890)"
    )
    assistant_overrides: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional overrides for the assistant configuration"
    )


class CreateCallWithContextRequest(BaseModel):
    """Request model for creating a call with conversation context."""

    phone_number: str = Field(
        ...,
        description="Customer phone number in E.164 format (e.g., +1234567890)"
    )
    person_name: str = Field(
        ...,
        description="Name of the person being called"
    )
    person_information: str = Field(
        default="",
        description="Information about the person (job, role, etc.)"
    )
    conversation_summary: str = Field(
        default="",
        description="Summary of previous conversations"
    )


@router.get("/health")
def health_check():
    """
    Health check endpoint for Vapi call service.

    Returns service status and configuration state.
    """
    is_configured = vapi_service.is_configured()

    return {
        "status": "healthy" if is_configured else "unconfigured",
        "service": "vapi_calls",
        "configured": is_configured,
        "capabilities": ["outbound_calls", "ai_assistant", "transcription"]
    }


@router.post("/create")
def create_call(request: CreateCallRequest):
    """
    Create and initiate a new AI voice call.

    This endpoint initiates an outbound call using Vapi's AI assistant.
    The call will be made using the configured assistant and phone number.

    Args:
        request: Call creation request with phone number and optional overrides

    Returns:
        Call information including call ID and status

    Example:
        ```
        POST /api/calls/create
        {
            "phone_number": "+1234567890",
            "assistant_overrides": {
                "variableValues": {
                    "person_name": "John Doe"
                }
            }
        }
        ```
    """
    try:
        logger.info(f"Creating call to {request.phone_number}")

        call_data = vapi_service.create_call(
            phone_number=request.phone_number,
            assistant_overrides=request.assistant_overrides
        )

        return {
            "success": True,
            "message": "Call initiated successfully",
            "data": call_data
        }

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating call: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create call: {str(e)}"
        )


@router.post("/create-with-context")
def create_call_with_context(request: CreateCallWithContextRequest):
    """
    Create an AI voice call with conversation context.

    This endpoint creates a call with personalized context about the person
    being called, including their information and conversation history.

    Args:
        request: Call request with phone number and context information

    Returns:
        Call information including call ID and status

    Example:
        ```
        POST /api/calls/create-with-context
        {
            "phone_number": "+1234567890",
            "person_name": "Jane Smith",
            "person_information": "Software Engineer at TechCorp",
            "conversation_summary": "Discussed project timelines and deliverables"
        }
        ```
    """
    try:
        logger.info(f"Creating contextual call to {request.phone_number} for {request.person_name}")

        call_data = vapi_service.create_call_with_context(
            phone_number=request.phone_number,
            person_name=request.person_name,
            person_information=request.person_information,
            conversation_summary=request.conversation_summary
        )

        return {
            "success": True,
            "message": f"Call to {request.person_name} initiated successfully",
            "data": call_data
        }

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating call: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create call: {str(e)}"
        )


@router.get("/{call_id}")
async def get_call(call_id: str):
    """
    Get call details and transcript.

    Retrieves information about a specific call including its status,
    transcript, duration, and cost.

    Args:
        call_id: The Vapi call ID

    Returns:
        Call details including transcript and metadata

    Example:
        ```
        GET /api/calls/abc123-def456-ghi789
        ```
    """
    try:
        logger.info(f"Retrieving call: {call_id}")

        call_data = await vapi_service.get_call(call_id)

        return {
            "success": True,
            "data": call_data
        }

    except Exception as e:
        logger.error(f"Error retrieving call {call_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve call: {str(e)}"
        )


@router.get("/")
async def list_calls(limit: int = 10):
    """
    List recent calls.

    Retrieves a list of recent calls made through the system.

    Args:
        limit: Maximum number of calls to return (default: 10)

    Returns:
        List of calls with their basic information

    Example:
        ```
        GET /api/calls?limit=20
        ```
    """
    try:
        logger.info(f"Listing calls (limit: {limit})")

        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )

        calls_data = await vapi_service.list_calls(limit=limit)

        return {
            "success": True,
            "data": calls_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing calls: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list calls: {str(e)}"
        )


@router.get("/ping/pong")
def ping_pong():
    """
    Simple ping-pong endpoint for testing.

    Returns a pong response to verify the API is working.
    """
    return {
        "ping": "pong",
        "service": "vapi_calls",
        "status": "active"
    }
