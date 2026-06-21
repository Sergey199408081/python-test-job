from sanic import Request
from sanic.response import json
from functools import wraps
from app.services.auth import AuthService
from app.database import get_session_maker


async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]

    async with get_session_maker()() as session:
        auth_service = AuthService(session)
        user = await auth_service.get_current_user(token)
        return user


async def get_current_admin(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]

    async with get_session_maker()() as session:
        auth_service = AuthService(session)
        payload = auth_service.decode_token(token)
        if not payload or payload.role != "admin":
            return None

        from app.models.admin import Admin
        from sqlalchemy import select

        result = await session.execute(
            select(Admin).where(Admin.id == payload.get_user_id())
        )
        return result.scalar_one_or_none()


def auth_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = await get_current_user(request)
        if not user:
            return json({"error": "Unauthorized"}, status=401)
        request.ctx.user = user
        return await func(request, *args, **kwargs)

    return wrapper


def admin_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        admin = await get_current_admin(request)
        if not admin:
            return json({"error": "Admin access required"}, status=403)
        request.ctx.admin = admin
        return await func(request, *args, **kwargs)

    return wrapper
