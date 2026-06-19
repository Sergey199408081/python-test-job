from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Numeric, 
    DateTime, 
    ForeignKey, 
    func, 
    UniqueConstraint, 
    Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(36), unique=True, index=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", back_populates="payments")
    user = relationship("User", back_populates="payments")

    __table_args__ = (
        UniqueConstraint('transaction_id', name='uq_transaction_id'),
        Index('ix_payment_user_account', 'user_id', 'account_id'),
    )

    def __repr__(self):
        return f"<Payment(id={self.id}, transaction_id='{self.transaction_id}', amount={self.amount})>"