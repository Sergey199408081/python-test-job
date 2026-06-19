from sanic import Blueprint, Request
from sanic.response import json
from app.services.auth import AuthService
from app.services.admin import AdminService
from app.database import get_session_maker
from app.schemas.auth import LoginRequest


auth_bp = Blueprint("auth", url_prefix="/api/auth")


@auth_bp.post("/login")
async def user_login(request: Request):
    try:
        data = LoginRequest(**request.json)
    except Exception as e:
        return json({"error": "Invalid request data", "details": str(e)}, status=400)
    
    async with get_session_maker()() as session:
        auth_service = AuthService(session)
        user = await auth_service.authenticate(data.email, data.password)
        if not user:
            return json({"error": "Invalid credentials"}, status=401)
        
        token = await auth_service.create_token(user)
        return json({"access_token": token, "token_type": "bearer"})


@auth_bp.post("/admin/login")
async def admin_login(request: Request):
    try:
        data = LoginRequest(**request.json)
    except Exception as e:
        return json({"error": "Invalid request data", "details": str(e)}, status=400)
    
    async with get_session_maker()() as session:
        admin_service = AdminService(session)
        admin = await admin_service.authenticate(data.email, data.password)
        if not admin:
            return json({"error": "Invalid credentials"}, status=401)
        
        token = admin_service.create_token(admin)
        return json({"access_token": token, "token_type": "bearer"})