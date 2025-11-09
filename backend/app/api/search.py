from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
from app.services.gemini_service import gemini_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["search"])


class SearchRequest(BaseModel):
    """Request model for Gemini search."""

    prompt: str = Field(..., description="The search query or prompt")
    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Generation temperature (0.0-1.0)"
    )
    thinking_budget: int = Field(
        default=-1,
        description="Thinking budget (-1 for unlimited)"
    )


@router.post("/gemini")
async def search_with_gemini(request: SearchRequest):
    """
    Perform a web search using Gemini 2.5 RPO with thinking capabilities.

    This endpoint uses Gemini's advanced reasoning and web search capabilities
    to answer queries. The response is streamed in real-time.

    Args:
        request: Search request with prompt and optional parameters

    Returns:
        Streaming response with generated text chunks

    Example:
        ```
        POST /api/search/gemini
        {
            "prompt": "Find contact information from these URLs: https://example.com/profile",
            "temperature": 0.2,
            "thinking_budget": -1
        }
        ```
    """
    try:
        logger.info(f"Processing Gemini search request: {request.prompt[:100]}...")

        async def generate():
            """Generator function for streaming response."""
            try:
                async for chunk in gemini_service.search_with_thinking(
                    prompt=request.prompt,
                    temperature=request.temperature,
                    thinking_budget=request.thinking_budget
                ):
                    yield chunk
            except Exception as e:
                logger.error(f"Error during search generation: {e}")
                yield f"\n\nError: {str(e)}"

        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        logger.error(f"Error processing search request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search request failed: {str(e)}"
        )


@router.get("/health")
def search_health_check():
    """Health check endpoint for search service."""
    return {
        "status": "healthy",
        "service": "gemini_search",
        "capabilities": ["web_search", "thinking", "streaming"]
    }
