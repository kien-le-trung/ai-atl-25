from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import partners, conversations, suggestions

# Create FastAPI app
app = FastAPI(
    title="AI Conversation Assistant API",
    description="API for analyzing conversations and providing intelligent suggestions",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(partners.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")
app.include_router(suggestions.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "AI Conversation Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
