from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str

    # Google Gemini
    GOOGLE_API_KEY: str
    GEMINI_API_KEY: str = ""  # For google.genai library (different from GOOGLE_API_KEY)

    # Deepgram (for live transcription)
    DEEPGRAM_API_KEY: str = ""

    # Vapi (for voice AI calls)
    VAPI_API_KEY: str = ""
    VAPI_ASSISTANT_ID: str = ""
    VAPI_PHONE_NUMBER_ID: str = ""

    # Application
    SECRET_KEY: str
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()
