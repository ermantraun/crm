import pytest
from application.lead.dto import LeadCreateInDTO
from application.lead import exceptions

pytestmark = pytest.mark.integration

PARAMS = [
    {"email": None, "phone": None, "name": None, "source": None},
    {"email": "user@example.com", "phone": "1234567", "name": "Al", "source": "web"},
    {"email": "a@b.co", "phone": None, "name": "Bob", "source": "ads"},
]

async def _create(interactor_factory, key: str, payload: dict):
    interactor = interactor_factory(key)
    return await interactor.create_lead(LeadCreateInDTO(**payload))

@pytest.mark.parametrize("optional_fields", PARAMS)
async def test_create_lead_variants(create_lead_interactor, get_lead_interactor, optional_fields):
    payload = {
        "note": "Первый контакт",
        **optional_fields,
    }
    dto = await _create(create_lead_interactor, key="key-" + (optional_fields.get("email") or "x"), payload=payload)
    assert dto.id is not None
    assert dto.note == "Первый контакт"
    fetched = await get_lead_interactor.get_lead(str(dto.id))
    assert fetched.id == dto.id
    assert fetched.note == dto.note

async def test_idempotency(create_lead_interactor):
    payload = {"note": "Идемпотентный лид"}
    key = "static-key"
    dto = await _create(create_lead_interactor, key, payload)
    assert dto.note == payload["note"]
    with pytest.raises(exceptions.LeadAlreadyExistsException):
        await _create(create_lead_interactor, key, payload)

async def test_invalid_lead(create_lead_interactor):
    payload = {"note": "   "}  
    with pytest.raises(exceptions.InvalidLeadDataException):
        await _create(create_lead_interactor, "inv-key", payload)
