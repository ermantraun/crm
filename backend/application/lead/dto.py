from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID
from domen.entities import InsightEntity  # доменная сущность инсайта

__all__ = [
    "LeadCreateInDTO",
    "LeadOutDTO",
]


@dataclass(slots=True)
class LeadCreateInDTO:
    note: str
    email: str | None = None
    phone: str | None = None
    name: str | None = None
    source: str | None = None
    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "phone": self.phone,
            "name": self.name,
            "note": self.note,
            "source": self.source,
        }


@dataclass(slots=True)
class LeadOutDTO:

    id: UUID
    note: str
    created_at: datetime
    email: str | None = None
    phone: str | None = None
    name: str | None = None
    source: str | None = None
    insights: List[InsightEntity] = field(default_factory=list)  # новое поле

    @classmethod
    def from_model(cls, model: Any) -> "LeadOutDTO":

        return cls(
            id=model.id,
            note=model.note,
            email=getattr(model, "email", None),
            phone=getattr(model, "phone", None),
            name=getattr(model, "name", None),
            source=getattr(model, "source", None),
            created_at=model.created_at,
            insights=getattr(model, "insights", []) or [],  # копируем инсайты
        )

@dataclass(slots=True)
class InsighCreateInDto:
    content: str
    lead_id: str
    content_hash: str