from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.account import Account
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth import AuthService
from decimal import Decimal


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.auth_service = AuthService(session)

    async def create_user(self, user_data: UserCreate) -> User:
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=self.auth_service.get_password_hash(user_data.password),
        )
        self.session.add(user)
        await self.session.flush()
        
        account = Account(user_id=user.id, balance=Decimal("0.00"))
        self.session.add(account)
        await self.session.flush()
        
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        user = await self.get_user(user_id)
        if not user:
            return None
        
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.password is not None:
            user.password_hash = self.auth_service.get_password_hash(user_data.password)
        
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        user = await self.get_user(user_id)
        if not user:
            return False
        await self.session.delete(user)
        await self.session.commit()
        return True

    async def get_user_account(self, user_id: int) -> Account | None:
        result = await self.session.execute(select(Account).where(Account.user_id == user_id))
        return result.scalar_one_or_none()