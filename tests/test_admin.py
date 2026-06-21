import pytest
from tests.conftest import get_admin_token, get_user_token


@pytest.mark.asyncio
async def test_admin_get_me_success(client):
    token = await get_admin_token(client)
    _, resp = await client.get(
        "/api/admin/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status == 200
    data = resp.json
    assert data["email"] == "admin@example.com"
    assert data["full_name"] == "Test Admin"
    assert "id" in data


@pytest.mark.asyncio
async def test_admin_get_me_unauthorized(client):
    _, resp = await client.get("/api/admin/me")
    assert resp.status == 403


@pytest.mark.asyncio
async def test_admin_get_me_with_user_token(client):
    token = await get_user_token(client)
    _, resp = await client.get(
        "/api/admin/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status == 403


@pytest.mark.asyncio
async def test_admin_list_users(client):
    token = await get_admin_token(client)
    _, resp = await client.get(
        "/api/admin/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status == 200
    data = resp.json
    assert isinstance(data, list)
    assert len(data) >= 1
    user_emails = [u["email"] for u in data]
    assert "user@example.com" in user_emails


@pytest.mark.asyncio
async def test_admin_list_users_unauthorized(client):
    _, resp = await client.get("/api/admin/users")
    assert resp.status == 403


@pytest.mark.asyncio
async def test_admin_create_user(client):
    token = await get_admin_token(client)
    _, resp = await client.post(
        "/api/admin/users",
        json={
            "email": "newuser@test.com",
            "password": "testpass123",
            "full_name": "New User",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status == 201
    data = resp.json
    assert data["email"] == "newuser@test.com"
    assert data["full_name"] == "New User"
    assert "id" in data


@pytest.mark.asyncio
async def test_admin_create_user_duplicate_email(client):
    token = await get_admin_token(client)
    _, resp = await client.post(
        "/api/admin/users",
        json={
            "email": "user@example.com",
            "password": "testpass123",
            "full_name": "Duplicate User",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status == 400


@pytest.mark.asyncio
async def test_admin_create_user_invalid_data(client):
    token = await get_admin_token(client)
    _, resp = await client.post(
        "/api/admin/users",
        json={
            "email": "invalid",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status == 400


@pytest.mark.asyncio
async def test_admin_update_user(client):
    token = await get_admin_token(client)
    _, create_resp = await client.post(
        "/api/admin/users",
        json={
            "email": "updateme@test.com",
            "password": "testpass123",
            "full_name": "Update Me",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = create_resp.json["id"]

    _, resp = await client.put(
        f"/api/admin/users/{user_id}",
        json={
            "full_name": "Updated Name",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status == 200
    data = resp.json
    assert data["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_admin_update_user_nonexistent(client):
    token = await get_admin_token(client)
    _, resp = await client.put(
        "/api/admin/users/99999",
        json={
            "full_name": "Ghost",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status == 404


@pytest.mark.asyncio
async def test_admin_delete_user(client):
    token = await get_admin_token(client)
    _, create_resp = await client.post(
        "/api/admin/users",
        json={
            "email": "deleteme@test.com",
            "password": "testpass123",
            "full_name": "Delete Me",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = create_resp.json["id"]

    _, resp = await client.delete(
        f"/api/admin/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status == 200


@pytest.mark.asyncio
async def test_admin_delete_user_nonexistent(client):
    token = await get_admin_token(client)
    _, resp = await client.delete(
        "/api/admin/users/99999", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status == 404


@pytest.mark.asyncio
async def test_admin_create_user_unauthorized(client):
    _, resp = await client.post(
        "/api/admin/users",
        json={
            "email": "test@test.com",
            "password": "testpass123",
            "full_name": "Test",
        },
    )
    assert resp.status == 403
