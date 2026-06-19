import uuid
import pytest
from tests.conftest import make_signature, get_user_token


@pytest.mark.asyncio
async def test_webhook_success(client):
    txn_id = str(uuid.uuid4())
    sig = make_signature(account_id=1, amount=100, transaction_id=txn_id, user_id=1)
    _, resp = await client.post("/api/webhook/payment", json={
        "transaction_id": txn_id,
        "account_id": 1,
        "user_id": 1,
        "amount": 100,
        "signature": sig,
    })
    assert resp.status == 201
    data = resp.json
    assert data["status"] == "processed"
    assert data["transaction_id"] == txn_id
    assert float(data["amount"]) == 100.0


@pytest.mark.asyncio
async def test_webhook_invalid_signature(client):
    txn_id = str(uuid.uuid4())
    _, resp = await client.post("/api/webhook/payment", json={
        "transaction_id": txn_id,
        "account_id": 1,
        "user_id": 1,
        "amount": 100,
        "signature": "invalidsignature",
    })
    assert resp.status == 400


@pytest.mark.asyncio
async def test_webhook_duplicate_transaction(client):
    txn_id = str(uuid.uuid4())
    sig = make_signature(account_id=1, amount=50, transaction_id=txn_id, user_id=1)

    _, resp1 = await client.post("/api/webhook/payment", json={
        "transaction_id": txn_id,
        "account_id": 1,
        "user_id": 1,
        "amount": 50,
        "signature": sig,
    })
    assert resp1.status == 201

    _, resp2 = await client.post("/api/webhook/payment", json={
        "transaction_id": txn_id,
        "account_id": 1,
        "user_id": 1,
        "amount": 50,
        "signature": sig,
    })
    assert resp2.status == 400


@pytest.mark.asyncio
async def test_webhook_invalid_data(client):
    _, resp = await client.post("/api/webhook/payment", json={})
    assert resp.status == 400


@pytest.mark.asyncio
async def test_webhook_nonexistent_user(client):
    txn_id = str(uuid.uuid4())
    sig = make_signature(account_id=1, amount=100, transaction_id=txn_id, user_id=99999)
    _, resp = await client.post("/api/webhook/payment", json={
        "transaction_id": txn_id,
        "account_id": 1,
        "user_id": 99999,
        "amount": 100,
        "signature": sig,
    })
    assert resp.status == 400


@pytest.mark.asyncio
async def test_webhook_amount_credited_to_account(client):
    token = await get_user_token(client)
    _, accounts_resp = await client.get("/api/user/accounts", headers={"Authorization": f"Bearer {token}"})
    initial_balance = float(accounts_resp.json[0]["balance"])

    txn_id = str(uuid.uuid4())
    amount = 250
    sig = make_signature(account_id=1, amount=amount, transaction_id=txn_id, user_id=1)
    _, resp = await client.post("/api/webhook/payment", json={
        "transaction_id": txn_id,
        "account_id": 1,
        "user_id": 1,
        "amount": amount,
        "signature": sig,
    })
    assert resp.status == 201

    _, accounts_resp2 = await client.get("/api/user/accounts", headers={"Authorization": f"Bearer {token}"})
    new_balance = float(accounts_resp2.json[0]["balance"])
    assert new_balance == initial_balance + amount


@pytest.mark.asyncio
async def test_webhook_payment_appears_in_user_payments(client):
    token = await get_user_token(client)
    txn_id = str(uuid.uuid4())
    amount = 777
    sig = make_signature(account_id=1, amount=amount, transaction_id=txn_id, user_id=1)

    await client.post("/api/webhook/payment", json={
        "transaction_id": txn_id,
        "account_id": 1,
        "user_id": 1,
        "amount": amount,
        "signature": sig,
    })

    _, resp = await client.get("/api/user/payments", headers={"Authorization": f"Bearer {token}"})
    assert resp.status == 200
    payments = resp.json
    txn_ids = [p["transaction_id"] for p in payments]
    assert txn_id in txn_ids


@pytest.mark.asyncio
async def test_webhook_creates_account_if_not_exists(client):
    from sqlalchemy import select
    from app.database import get_session_maker
    from app.models.user import User

    async with get_session_maker()() as s:
        result = await s.execute(select(User).where(User.email == "newaccount@test.com"))
        user = result.scalar_one_or_none()
        if not user:
            from app.services.auth import pwd_context
            user = User(
                email="newaccount@test.com",
                password_hash=pwd_context.hash("pass123"),
                full_name="No Account User",
            )
            s.add(user)
            await s.commit()
            await s.refresh(user)

    txn_id = str(uuid.uuid4())
    sig = make_signature(account_id=999, amount=500, transaction_id=txn_id, user_id=user.id)
    _, resp = await client.post("/api/webhook/payment", json={
        "transaction_id": txn_id,
        "account_id": 999,
        "user_id": user.id,
        "amount": 500,
        "signature": sig,
    })
    assert resp.status == 201

    async with get_session_maker()() as s:
        from app.models.account import Account
        result = await s.execute(select(Account).where(Account.user_id == user.id))
        account = result.scalar_one_or_none()
        assert account is not None
        assert float(account.balance) == 500.0


@pytest.mark.asyncio
async def test_webhook_signature_verification_with_example():
    secret = "gfdmhghif38yrf9ew0jkf32"
    sig = make_signature(
        account_id=1,
        amount=100,
        transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
        user_id=1,
        secret_key=secret,
    )
    assert sig == "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"