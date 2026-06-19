import pytest
from tests.conftest import get_user_token


@pytest.mark.asyncio
async def test_get_me_success(client):
    token = await get_user_token(client)
    _, resp = await client.get("/api/user/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status == 200
    data = resp.json
    assert data["email"] == "user@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    _, resp = await client.get("/api/user/me")
    assert resp.status == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(client):
    _, resp = await client.get("/api/user/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status == 401


@pytest.mark.asyncio
async def test_get_accounts_success(client):
    token = await get_user_token(client)
    _, resp = await client.get("/api/user/accounts", headers={"Authorization": f"Bearer {token}"})
    assert resp.status == 200
    data = resp.json
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0]
    assert "balance" in data[0]
    assert "user_id" in data[0]


@pytest.mark.asyncio
async def test_get_accounts_unauthorized(client):
    _, resp = await client.get("/api/user/accounts")
    assert resp.status == 401


@pytest.mark.asyncio
async def test_get_payments_success(client):
    token = await get_user_token(client)
    _, resp = await client.get("/api/user/payments", headers={"Authorization": f"Bearer {token}"})
    assert resp.status == 200
    data = resp.json
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_payments_unauthorized(client):
    _, resp = await client.get("/api/user/payments")
    assert resp.status == 401