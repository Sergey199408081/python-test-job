from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.admin import Admin
from app.schemas.auth import LoginRequest
from app.services.auth import AuthService


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.auth_service = AuthService(session)

    async def authenticate(self, email: str, password: str) -> Admin | None:
        result = await self.session.execute(select(Admin).where(Admin.email == email))
        admin = result.scalar_one_or_none()
        if not admin or not self.auth_service.verify_password(password, admin.password_hash):
            return None
        return admin

    async def get_admin(self, admin_id: int) -> Admin | None:
        result = await self.session.execute(select(Admin).where(Admin.id == admin_id))
        return result.scalar_one_or_none()

    async def create_admin(self, email: str, password: str, full_name: str) -> Admin:
        admin = Admin(
            email=email,
            full_name=full_name,
            password_hash=self.auth_service.get_password_hash(password),
        )
        self.session.add(admin)
        await self.session.commit()
        await self.session.refresh(admin)
        return admin

    def create_token(self, admin: Admin) -> str:
        return self.auth_service.create_access_token(
            data={"sub": str(admin.id), "email": admin.email, "role": "admin"}
        )