from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    balance = Column(Numeric(precision=15, scale=2), default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="accounts")
    payments = relationship(
        "Payment", back_populates="account", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("user_id", name="uq_user_account"),)

    def __repr__(self):
        return (
            f"<Account(id={self.id}, user_id={self.user_id}, balance={self.balance})>"
        )
