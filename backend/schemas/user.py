#backend\schemas\user.py
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from .account import AccountOut


class MeOut(BaseModel):
    """Response schema for /me endpoint."""
    user: dict
    total_balance: Decimal
    accounts: List[AccountOut]


class UserBase(BaseModel):
    """Shared base for user models."""
    name: str
    phone: str
    role: Optional[str] = "user"


class UserCreate(UserBase):
    """Used when creating a new user (from admin)."""
    password: str  # plaintext input, will be hashed before saving


class UserOut(UserBase):
    """Response schema for reading user info."""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Used for login requests."""
    phone: str
    password: str
