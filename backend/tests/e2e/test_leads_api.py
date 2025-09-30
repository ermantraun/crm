import pytest

pytestmark = pytest.mark.e2e

async def test_create_and_get_lead(client):
    headers = {"Idempotency-Key": "abc-123"}
    resp = await client.post(
        "/leads",
        json={"note": "Первый лид", "email": "e@x.ru"},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    lead_id = data["id"]
    assert data["note"] == "Первый лид"
    resp_dup = await client.post(
        "/leads",
        json={"note": "Первый лид", "email": "e@x.ru"},
        headers=headers,
    )
    assert resp_dup.status_code == 200
    assert resp_dup.json()["detail"] == "OK"
    get_resp = await client.get(f"/leads/{lead_id}")
    assert get_resp.status_code == 200
    got = get_resp.json()
    assert got["id"] == lead_id
    assert got["note"] == "Первый лид"

async def test_validation_error(client):
    resp = await client.post("/leads", json={"note": "   "})
    assert resp.status_code == 422
    body = resp.json()
    assert "note is required" in body["detail"]
