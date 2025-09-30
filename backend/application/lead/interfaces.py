from abc import abstractmethod  
from typing import Protocol
from . import dto
from domen import entities
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

class Intent(Enum):
    BUY = "buy"
    SUPPORT = "support"
    SPAM = "spam"
    JOB = "job"
    OTHER = "other"


class Priority(Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class NextAction(Enum):
    CALL = "call"
    EMAIL = "email"
    IGNORE = "ignore"
    QUALIFY = "qualify"


@dataclass
class InsightData:
    id: str
    lead_id: str
    intent: Intent
    priority: Priority
    next_action: NextAction
    confidence: float
    tags: List[str]
    created_at: datetime


class LeadRepository(Protocol):
    @abstractmethod
    def create(self, lead: dto.LeadCreateInDTO) -> entities.LeadEntity:
        ...
    
    @abstractmethod
    def get(self, lead_id: str) -> entities.LeadEntity:
        ...

class KeysRepository(Protocol):
    @abstractmethod
    def exists(self, key: str) -> bool:
        ...
    
    @abstractmethod
    def create(self, key: str) -> None:
        ...

class InsightRepository(Protocol):
    @abstractmethod
    def create(self, lead_id: str, insight: entities.InsightEntity | dict) -> entities.InsightEntity:
        ...
    
    @abstractmethod
    def exists(self, lead_id: str, content_hash: str) -> bool:
        ...

class ContextProvider(Protocol):
    @abstractmethod
    def get_idempotency_key(self) -> UUID:
        ...
        
class MessageBroker(Protocol):
    @abstractmethod
    def publish(self, message: dict) -> None:
        ...

class InsightGenerator(Protocol):
    @abstractmethod
    def gen(self, content: str) -> InsightData:
        ...