import uuid
from typing import Any, Mapping, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound
from application.lead import dto as lead_dto_module
from application.lead import interfaces
from application.lead import exceptions as lead_exceptions
from domen import entities
from . import models
from application import common_interfaces

def _lead_model_to_entity(m: models.Lead) -> entities.LeadEntity:
    return entities.LeadEntity(
        id=m.id,
        note=m.note,
        email=m.email,
        phone=m.phone,
        name=m.name,
        source=m.source,
        created_at=m.created_at,
        insights=[
            entities.InsightEntity(
                id=i.id,
                lead_id=i.lead_id,
                intent=entities.IntentEnum(i.intent),
                priority=entities.PriorityEnum(i.priority),
                next_action=entities.NextActionEnum(i.next_action),
                confidence=i.confidence,
                tags=i.tags,
                content_hash=i.content_hash,
                created_at=i.created_at,
            )
            for i in m.insights
        ],
    )

def _insight_model_to_entity(m: models.Insight) -> entities.InsightEntity:
    return entities.InsightEntity(
        id=m.id,
        lead_id=m.lead_id,
        intent=entities.IntentEnum(m.intent),
        priority=entities.PriorityEnum(m.priority),
        next_action=entities.NextActionEnum(m.next_action),
        confidence=m.confidence,
        tags=m.tags,
        content_hash=m.content_hash,
        created_at=m.created_at,
    )

class LeadRepository(interfaces.LeadRepository):
    def __init__(self, session: common_interfaces.DBSession) -> None:
        self.session: AsyncSession = session

    async def create(self, lead: lead_dto_module.LeadCreateInDTO | Mapping[str, Any]) -> entities.LeadEntity:
        if isinstance(lead, lead_dto_module.LeadCreateInDTO):
            payload = lead.to_dict()
        else:
            payload = dict(lead)

        model = models.Lead(**payload)
        self.session.add(model)
        await self.session.flush()          
        await self.session.refresh(model)   
        return _lead_model_to_entity(model)

    async def get(self, lead_id: str) -> entities.LeadEntity:
        try:
            lead_uuid = uuid.UUID(str(lead_id))
        except ValueError:
            raise ValueError("lead_id must be a valid UUID string")
        stmt = (
            select(models.Lead)
            .options(selectinload(models.Lead.insights))  # eager load для async
            .where(models.Lead.id == lead_uuid)
        )
        try:
            res = await self.session.execute(stmt)
            model = res.scalar_one()
        except NoResultFound:
            raise lead_exceptions.LeadNotFoundException()
        return _lead_model_to_entity(model)


class KeysRepository(interfaces.KeysRepository):

    _NAMESPACE = uuid.NAMESPACE_DNS

    def __init__(self, session: common_interfaces.DBSession) -> None:
        self.session: AsyncSession = session

    def _normalize_key(self, key: str) -> uuid.UUID:
        try:
            return uuid.UUID(key)
        except ValueError:
            return uuid.uuid5(self._NAMESPACE, key)

    async def exists(self, key: str) -> bool:
        key_uuid = self._normalize_key(key)
        stmt = select(func.count()).select_from(models.Keys).where(models.Keys.id == key_uuid)
        res = await self.session.execute(stmt)
        return bool(res.scalar_one())

    async def create(self, key: str) -> None:
        key_uuid = self._normalize_key(key)
        self.session.add(models.Keys(id=key_uuid))
        await self.session.flush()


class InsightRepository(interfaces.InsightRepository):
    def __init__(self, session: common_interfaces.DBSession) -> None:
        self.session: AsyncSession = session

    async def create(self, lead_id: str, insight: entities.InsightEntity | Mapping[str, Any]) -> entities.InsightEntity:
        try:
            lead_uuid = uuid.UUID(lead_id)
        except ValueError:
            raise ValueError("lead_id must be a valid UUID string")
        
        if isinstance(insight, Mapping):
            data = dict(insight)
            try:
                intent_val = data["intent"]
                priority_val = data["priority"]
                next_action_val = data["next_action"]
                confidence = float(data.get("confidence", 0))
                tags = data.get("tags")
                content_hash = data["content_hash"]
            except KeyError as e:
                raise ValueError(f"Missing insight field: {e}") from e

            intent_str = entities.IntentEnum(intent_val).value if not isinstance(intent_val, entities.IntentEnum) else intent_val.value
            priority_str = entities.PriorityEnum(priority_val).value if not isinstance(priority_val, entities.PriorityEnum) else priority_val.value
            next_action_str = entities.NextActionEnum(next_action_val).value if not isinstance(next_action_val, entities.NextActionEnum) else next_action_val.value

            model = models.Insight(
                lead_id=lead_uuid,
                intent=intent_str,
                priority=priority_str,
                next_action=next_action_str,
                confidence=confidence,
                tags=tags,
                content_hash=content_hash,
            )
        else:
            model = models.Insight(
                lead_id=lead_uuid,
                intent=insight.intent.value,
                priority=insight.priority.value,
                next_action=insight.next_action.value,
                confidence=insight.confidence,
                tags=insight.tags,
                content_hash=insight.content_hash,
            )

        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _insight_model_to_entity(model)

    async def exists(self, lead_id: str, content_hash: str) -> bool:
        try:
            lead_uuid = uuid.UUID(lead_id)
        except ValueError:
            return False
        stmt = (
            select(func.count())
            .select_from(models.Insight)
            .where(models.Insight.lead_id == lead_uuid, models.Insight.content_hash == content_hash)
        )
        res = await self.session.execute(stmt)
        return bool(res.scalar_one())



__all__: Sequence[str] = [
    "LeadRepository",
    "InsightRepository",
    "KeysRepository",
]
