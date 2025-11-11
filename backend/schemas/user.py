#backend\schemas\user.py
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from .account import AccountOut

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None


class UserBase(BaseModel):
    name: str
    phone: str
    role: Optional[str] = "user"


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    phone: str
    password: str
