from .dto import LeadCreateInDTO, LeadOutDTO, InsighCreateInDto
from . import exceptions
from . import interfaces
from . import validators

from ..common_interfaces import DBSession
from uuid import UUID
import hashlib

class CreateLeadInteractor:
    def __init__(
        self,
        lead_repo: interfaces.LeadRepository,
        keys_repo: interfaces.KeysRepository,
        message_broker: interfaces.MessageBroker,
        session: DBSession,
        context: interfaces.ContextProvider,
    ) -> None:
        self.lead_repo = lead_repo
        self.keys_repo = keys_repo
        self.validator = validators.ValidateLead
        self.message_broker = message_broker
        self.session = session
        self.context = context
        
    async def create_lead(self, lead_dto: LeadCreateInDTO) -> LeadOutDTO:
        idempotency_key = self.context.get_idempotency_key()
        
        key_exists = await self.keys_repo.exists(idempotency_key)
        if key_exists:
            raise exceptions.LeadAlreadyExistsException()
        
        self.validator(lead_dto).validate()
        
        lead_model = await self.lead_repo.create(lead_dto.to_dict())
        
        await self.keys_repo.create(idempotency_key)
        await self.session.commit()
        content_hash = hashlib.sha256(lead_dto.note.encode("utf-8")).hexdigest()
        self.message_broker.publish({
            "lead_id": lead_model.id,
            "content_hash": content_hash,
            "occurred_at": lead_model.created_at.isoformat(),
            "content": lead_dto.note,  
        })
        return LeadOutDTO.from_model(lead_model)
    
class CreateInsightInteractor:
    def __init__(
        self,
        insight_repo: interfaces.InsightRepository,
        session: DBSession,
        InsightGenerator: interfaces.InsightGenerator,
    ) -> None:
        self.insight_repo = insight_repo
        self.session = session
        self.InsightGenerator = InsightGenerator
        self.validator = validators.ValidateInsight
        
    async def create_insight(self, insight: InsighCreateInDto) -> dict:
        self.validator(insight).validate()
        
        insight_exists = await self.insight_repo.exists(insight.lead_id, insight.content_hash)
        if insight_exists:    
            raise exceptions.InsightAlreadyExistsException()
            
        gen_data = self.InsightGenerator.gen(insight.content)
        # Добавляем хэш из входного DTO
        gen_data["content_hash"] = insight.content_hash

        insight_model = await self.insight_repo.create(
            insight.lead_id,
            gen_data,
        )
        await self.session.commit()
        return insight_model
    
class GetLeadInteractor:
    def __init__(self, lead_repo: interfaces.LeadRepository) -> None:
        self.lead_repo = lead_repo
        
    async def get_lead(self, lead_id: UUID) -> LeadOutDTO:
        lead_model = await self.lead_repo.get(lead_id)
        return LeadOutDTO.from_model(lead_model)