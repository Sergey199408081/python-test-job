from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from datetime import datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Union[int, str]
    email: str
    role: str
    exp: Optional[Union[int, datetime]] = None

    def get_user_id(self) -> int:
        return int(self.sub)
