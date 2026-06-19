from sanic import Blueprint, Request
from sanic.response import json
from app.middleware.auth import auth_required
from app.services.user import UserService
from app.services.payment import PaymentService
from app.database import get_session_maker


user_bp = Blueprint("user", url_prefix="/api/user")


@user_bp.get("/me")
@auth_required
async def get_me(request: Request):
    user = request.ctx.user
    return json({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
    })


@user_bp.get("/accounts")
@auth_required
async def get_accounts(request: Request):
    user = request.ctx.user
    
    async with get_session_maker()() as session:
        user_service = UserService(session)
        account = await user_service.get_user_account(user.id)
        
        if not account:
            return json([])
        
        return json([{
            "id": account.id,
            "user_id": account.user_id,
            "balance": str(account.balance),
            "created_at": account.created_at.isoformat() if account.created_at else None,
        }])


@user_bp.get("/payments")
@auth_required
async def get_payments(request: Request):
    user = request.ctx.user
    
    async with get_session_maker()() as session:
        payment_service = PaymentService(session)
        payments = await payment_service.get_user_payments(user.id)
        
        return json([{
            "id": p.id,
            "transaction_id": p.transaction_id,
            "account_id": p.account_id,
            "user_id": p.user_id,
            "amount": str(p.amount),
            "created_at": p.created_at.isoformat() if p.created_at else None,
        } for p in payments])