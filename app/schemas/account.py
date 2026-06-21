from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import datetime


class AccountBase(BaseModel):
    user_id: int


class AccountCreate(AccountBase):
    pass


class AccountResponse(BaseModel):
    id: int
    user_id: int
    balance: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
