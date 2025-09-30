import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from typing import Optional, List
from enum import Enum

class Base(DeclarativeBase):
    pass


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


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    name: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    note: Mapped[str] = mapped_column(sa.Text, nullable=False)
    source: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )

    insights: Mapped[List["Insight"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan", lazy="selectin"
    )


class Insight(Base):
    __tablename__ = "insights"
    __table_args__ = (
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_insight_confidence_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    intent: Mapped[IntentEnum] = mapped_column(
        sa.Enum(IntentEnum, name="intent_enum"), nullable=False
    )
    priority: Mapped[PriorityEnum] = mapped_column(
        sa.Enum(PriorityEnum, name="priority_enum"), nullable=False
    )
    next_action: Mapped[NextActionEnum] = mapped_column(
        sa.Enum(NextActionEnum, name="next_action_enum"), nullable=False
    )
    confidence: Mapped[float] = mapped_column(
        sa.Float, nullable=False, server_default=sa.text("0")
    )
    tags: Mapped[Optional[List[str]]] = mapped_column(
        sa.ARRAY(sa.String()), nullable=True
    )
    content_hash: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )

    lead: Mapped["Lead"] = relationship(back_populates="insights")

class Keys(Base):
    __tablename__ = "keys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
