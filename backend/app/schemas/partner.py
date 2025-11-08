from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PartnerCreate(BaseModel):
    """Schema for creating a conversation partner."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class PartnerUpdate(BaseModel):
    """Schema for updating a conversation partner."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class PartnerResponse(BaseModel):
    """Schema for conversation partner response."""
    id: int
    user_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
