import pytest
from sanic import Sanic


@pytest.mark.asyncio
async def test_user_login_success(client):
    _, resp = await client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "password123",
    })
    assert resp.status == 200
    data = resp.json
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_user_login_wrong_password(client):
    _, resp = await client.post("/api/auth/login", json={
        "email": "user@example.com",
        "password": "wrongpassword",
    })
    assert resp.status == 401


@pytest.mark.asyncio
async def test_user_login_nonexistent_email(client):
    _, resp = await client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "password123",
    })
    assert resp.status == 401


@pytest.mark.asyncio
async def test_admin_login_success(client):
    _, resp = await client.post("/api/auth/admin/login", json={
        "email": "admin@example.com",
        "password": "admin123",
    })
    assert resp.status == 200
    data = resp.json
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_admin_login_wrong_password(client):
    _, resp = await client.post("/api/auth/admin/login", json={
        "email": "admin@example.com",
        "password": "wrongpassword",
    })
    assert resp.status == 401


@pytest.mark.asyncio
async def test_admin_login_nonexistent_email(client):
    _, resp = await client.post("/api/auth/admin/login", json={
        "email": "nonexistent@example.com",
        "password": "admin123",
    })
    assert resp.status == 401


@pytest.mark.asyncio
async def test_user_login_invalid_data(client):
    _, resp = await client.post("/api/auth/login", json={})
    assert resp.status == 400


@pytest.mark.asyncio
async def test_admin_login_invalid_data(client):
    _, resp = await client.post("/api/auth/admin/login", json={})
    assert resp.status == 400