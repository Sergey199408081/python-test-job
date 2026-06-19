from sanic import Blueprint, Request
from sanic.response import json
from app.middleware.auth import admin_required
from app.services.user import UserService
from app.services.admin import AdminService
from app.database import get_session_maker
from app.models.user import User
from app.models.account import Account
from app.schemas.user import UserCreate, UserUpdate
from decimal import Decimal


admin_bp = Blueprint("admin", url_prefix="/api/admin")


@admin_bp.get("/me")
@admin_required
async def get_admin_me(request: Request):
    admin = request.ctx.admin
    return json({
        "id": admin.id,
        "email": admin.email,
        "full_name": admin.full_name,
    })


@admin_bp.get("/users")
@admin_required
async def get_users(request: Request):
    async with get_session_maker()() as session:
        user_service = UserService(session)
        
        result = await session.execute(
            User.__table__.select()
        )
        users = result.fetchall()
        
        user_list = []
        for u in users:
            account = await session.execute(
                Account.__table__.select().where(Account.user_id == u.id)
            )
            acc = account.first()
            
            user_list.append({
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "account": {
                    "id": acc.id,
                    "balance": str(acc.balance),
                } if acc else None,
            })
        
        return json(user_list)


@admin_bp.post("/users")
@admin_required
async def create_user(request: Request):
    try:
        data = UserCreate(**request.json)
    except Exception as e:
        return json({"error": "Invalid request data", "details": str(e)}, status=400)
    
    async with get_session_maker()() as session:
        user_service = UserService(session)
        
        existing = await user_service.get_user_by_email(data.email)
        if existing:
            return json({"error": "User with this email already exists"}, status=400)
        
        user = await user_service.create_user(data)
        
        return json({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
        }, status=201)


@admin_bp.put("/users/<user_id:int>")
@admin_required
async def update_user(request: Request, user_id: int):
    try:
        data = UserUpdate(**request.json)
    except Exception as e:
        return json({"error": "Invalid request data", "details": str(e)}, status=400)
    
    async with get_session_maker()() as session:
        user_service = UserService(session)
        
        user = await user_service.update_user(user_id, data)
        if not user:
            return json({"error": "User not found"}, status=404)
        
        return json({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
        })


@admin_bp.delete("/users/<user_id:int>")
@admin_required
async def delete_user(request: Request, user_id: int):
    async with get_session_maker()() as session:
        user_service = UserService(session)
        
        success = await user_service.delete_user(user_id)
        if not success:
            return json({"error": "User not found"}, status=404)
        
        return json({"message": "User deleted successfully"})