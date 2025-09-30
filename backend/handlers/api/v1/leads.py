from fastapi import APIRouter, status
from dishka.integrations.fastapi import FromDishka, DishkaRoute
from application.lead.dto import LeadCreateInDTO
from application.lead.interactors import CreateLeadInteractor, GetLeadInteractor
from uuid import UUID
from .schemas import LeadCreateIn, LeadOut
from .responses_descriptions import lead_responses

router = APIRouter(prefix="/leads", tags=["Leads"], route_class=DishkaRoute)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    name="Create lead",
    summary="Создать лида",
    responses={
        status.HTTP_201_CREATED: lead_responses["create"][201],
        status.HTTP_200_OK: lead_responses["create"][200],
        status.HTTP_422_UNPROCESSABLE_ENTITY: lead_responses["create"][422],
    },
    response_model=LeadOut,
)
async def create_lead(
    payload: LeadCreateIn,
    interactor: FromDishka[CreateLeadInteractor],
) -> LeadOut:
    dto = LeadCreateInDTO(
        note=payload.note,
        email=payload.email,
        phone=payload.phone,
        name=payload.name,
        source=payload.source,
    )
    result = await interactor.create_lead(dto)
    return LeadOut(
        id=result.id,  
        note=result.note,
        email=result.email,
        phone=result.phone,
        name=result.name,
        source=result.source,
        created_at=result.created_at.isoformat(),
        insights=[],
    )

@router.get(
    "/{lead_id}",
    status_code=status.HTTP_200_OK,
    name="Get lead",
    summary="Получить лида",
    responses={
        status.HTTP_200_OK: lead_responses["get"][200],
        status.HTTP_404_NOT_FOUND: lead_responses["get"][404],
    },
    response_model=LeadOut,
)
async def get_lead(
    lead_id: UUID,
    interactor: FromDishka[GetLeadInteractor],
) -> LeadOut:
    result = await interactor.get_lead(lead_id)
    return LeadOut(
        id=result.id,
        note=result.note,
        email=result.email,
        phone=result.phone,
        name=result.name,
        source=result.source,
        created_at=result.created_at.isoformat(),
        insights=[],
    )