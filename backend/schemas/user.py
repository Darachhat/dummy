from pydantic import BaseModel
from typing import List
from .account import AccountOut
from decimal import Decimal
from datetime import datetime

class MeOut(BaseModel):
    user: dict
    total_balance: Decimal
    accounts: List[AccountOut]

class User(BaseModel):
    id: int | None = None
    name: str
    phone: str
    password_hash: str | None = None
    role: str = "user"

    class Config:
        from_attributes = True 
