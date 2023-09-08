from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class TokenData(BaseModel):
    id: Optional[int] = None


class UserCreate(BaseModel):
    email: EmailStr
    name: str


class OrderCreate(BaseModel):
    item: str
    amount: int
    owner_id: int


class OrderOut(BaseModel):
    item: str
    amount: str
    delivered: bool
    created_at: datetime


class OrdersOut(BaseModel):
    items: List[OrderOut] | Optional[str] = None
    result: bool
    success_message: str
