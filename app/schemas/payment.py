from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
import uuid


class WebhookRequest(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction ID from external system")
    account_id: int = Field(..., description="User's account ID")
    user_id: int = Field(..., description="User ID")
    amount: Decimal = Field(..., gt=0, description="Amount to credit")
    signature: str = Field(..., description="SHA256 signature")


class PaymentResponse(BaseModel):
    id: int
    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)