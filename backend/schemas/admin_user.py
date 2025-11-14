# backend/schemas/admin_user.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AdminUserSummary(BaseModel):
    id: int
    name: Optional[str] = None
    phone: str
    role: str
    created_at: Optional[datetime] = None


class AdminUserListResponse(BaseModel):
    items: List[AdminUserSummary]
    total: int
    page: int
    page_size: int


class AdminAccountBalanceUpdateOut(BaseModel):
    id: int
    user_id: int
    balance: float
    currency: str
    message: str


class AdminDeleteUserOut(BaseModel):
    message: str
