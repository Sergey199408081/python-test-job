import os
import asyncio
import hashlib
import uuid
import pytest
import pytest_asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sanic import Sanic
from sanic_testing import TestManager

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["JWT_SECRET"] = "test_jwt_secret_for_testing_only"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRE_MINUTES"] = "60"
os.environ["DEBUG"] = "False"

from app.database import Base, init_engine, get_session_maker
from app.main import create_app
from app.models.user import User
from app.models.admin import Admin
from app.models.account import Account
from app.services.auth import pwd_context


TEST_USER_EMAIL = "user@example.com"
TEST_USER_PASSWORD = "password123"
TEST_ADMIN_EMAIL = "admin@example.com"
TEST_ADMIN_PASSWORD = "admin123"
SECRET_KEY = "test_secret_key_for_testing_only"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine("sqlite+aiosqlite:///./test.db", echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine):
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as s:
        yield s


@pytest_asyncio.fixture
async def app(engine):
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as s:
        user = User(
            email=TEST_USER_EMAIL,
            password_hash=pwd_context.hash(TEST_USER_PASSWORD),
            full_name="Test User",
        )
        s.add(user)
        await s.flush()

        account = Account(user_id=user.id, balance=Decimal("0.00"))
        s.add(account)

        admin = Admin(
            email=TEST_ADMIN_EMAIL,
            password_hash=pwd_context.hash(TEST_ADMIN_PASSWORD),
            full_name="Test Admin",
        )
        s.add(admin)
        await s.commit()

    Sanic._app_registry.clear()
    application = create_app(database_url="sqlite+aiosqlite:///./test.db")
    TestManager(application)
    yield application


@pytest_asyncio.fixture
async def client(app):
    _, resp = await app.asgi_client.get("/health")
    yield app.asgi_client


async def get_user_token(client) -> str:
    _, resp = await client.post("/api/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    })
    return resp.json["access_token"]


async def get_admin_token(client) -> str:
    _, resp = await client.post("/api/auth/admin/login", json={
        "email": TEST_ADMIN_EMAIL,
        "password": TEST_ADMIN_PASSWORD,
    })
    return resp.json["access_token"]


def make_signature(account_id: int, amount, transaction_id: str, user_id: int, secret_key: str = SECRET_KEY) -> str:
    sorted_keys = sorted(["account_id", "amount", "transaction_id", "user_id"])
    values = {
        "account_id": str(account_id),
        "amount": str(amount),
        "transaction_id": transaction_id,
        "user_id": str(user_id),
    }
    concat_str = "".join(values[k] for k in sorted_keys) + secret_key
    return hashlib.sha256(concat_str.encode()).hexdigest()