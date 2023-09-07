from pydantic import BaseModel, EmailStr
from typing import Optional


class TokenData(BaseModel):
    id: Optional[int] = None


class UserCreate(BaseModel):
    email: EmailStr
    name: str
