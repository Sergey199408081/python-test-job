import hashlib
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.payment import Payment
from app.models.account import Account
from app.models.user import User
from app.schemas.payment import WebhookRequest
from app.config import settings


class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def verify_signature(self, data: WebhookRequest) -> bool:
        sorted_keys = sorted(["account_id", "amount", "transaction_id", "user_id"])
        concat_str = "".join(str(getattr(data, key)) for key in sorted_keys) + settings.SECRET_KEY
        expected_signature = hashlib.sha256(concat_str.encode()).hexdigest()
        return expected_signature == data.signature

    async def process_webhook(self, data: WebhookRequest) -> Payment | None:
        if not self.verify_signature(data):
            return None

        existing_payment = await self.session.execute(
            select(Payment).where(Payment.transaction_id == data.transaction_id)
        )
        if existing_payment.scalar_one_or_none():
            return None

        account = await self.session.execute(
            select(Account).where(Account.id == data.account_id, Account.user_id == data.user_id)
        )
        account = account.scalar_one_or_none()

        if not account:
            user = await self.session.execute(select(User).where(User.id == data.user_id))
            user = user.scalar_one_or_none()
            if not user:
                return None
            
            account = Account(user_id=data.user_id, balance=Decimal("0.00"))
            self.session.add(account)
            await self.session.flush()

        payment = Payment(
            transaction_id=data.transaction_id,
            account_id=account.id,
            user_id=data.user_id,
            amount=data.amount,
        )
        self.session.add(payment)

        account.balance += data.amount

        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def get_user_payments(self, user_id: int) -> list[Payment]:
        result = await self.session.execute(
            select(Payment).where(Payment.user_id == user_id).order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())