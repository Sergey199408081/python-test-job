from sanic import Blueprint, Request
from sanic.response import json
from app.services.payment import PaymentService
from app.database import get_session_maker
from app.schemas.payment import WebhookRequest


webhook_bp = Blueprint("webhook", url_prefix="/api/webhook")


@webhook_bp.post("/payment")
async def process_payment_webhook(request: Request):
    try:
        data = WebhookRequest(**request.json)
    except Exception as e:
        return json({"error": "Invalid request data", "details": str(e)}, status=400)

    async with get_session_maker()() as session:
        payment_service = PaymentService(session)
        payment = await payment_service.process_webhook(data)

        if not payment:
            return json(
                {"error": "Invalid signature or duplicate transaction"}, status=400
            )

        return json(
            {
                "id": payment.id,
                "transaction_id": payment.transaction_id,
                "account_id": payment.account_id,
                "user_id": payment.user_id,
                "amount": str(payment.amount),
                "status": "processed",
            },
            status=201,
        )
