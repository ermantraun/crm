from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from uuid import UUID
from datetime import datetime


EMAIL_MAX_LEN = 255
PHONE_MAX_LEN = 50
NAME_MAX_LEN = 255
SOURCE_MAX_LEN = 100
MIN_NAME_LEN = 2  

class IntentEnum(str, Enum):
    buy = "buy"
    support = "support"
    spam = "spam"
    job = "job"
    other = "other"

class PriorityEnum(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class NextActionEnum(str, Enum):
    call = "call"
    email = "email"
    ignore = "ignore"
    qualify = "qualify"

@dataclass(slots=True)
class InsightEntity:
    id: UUID
    lead_id: UUID
    intent: IntentEnum
    priority: PriorityEnum
    next_action: NextActionEnum
    confidence: float
    content_hash: str
    tags: Optional[List[str]] = None
    created_at: Optional[datetime] = None

@dataclass(slots=True)
class LeadEntity:
    id: UUID
    note: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None
    insights: List[InsightEntity] = field(default_factory=list)

__all__ = [
    "LeadEntity",
    "InsightEntity",
    "IntentEnum",
    "PriorityEnum",
    "NextActionEnum",
    "EMAIL_MAX_LEN",
    "PHONE_MAX_LEN",
    "NAME_MAX_LEN",
    "SOURCE_MAX_LEN",
    "MIN_NAME_LEN",  
]
