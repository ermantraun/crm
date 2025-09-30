from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class LeadCreateIn(BaseModel):
    note: str = Field(..., min_length=1)
    email: Optional[str] = Field(None)
    phone: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    source: Optional[str] = Field(None)

class InsightOut(BaseModel):
    id: UUID
    intent: str
    priority: str
    next_action: str
    confidence: float
    tags: Optional[List[str]] = None
    content_hash: str
    created_at: Optional[str] = None

class LeadOut(BaseModel):
    id: UUID
    note: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    source: Optional[str] = None
    created_at: str
    insights: List[InsightOut] = Field(default_factory=list)
