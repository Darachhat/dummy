#backend\schemas\account.py
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class AccountOut(BaseModel):
    id: int
    name: str
    number: str
    balance: Decimal
    currency: str


    class Config:
        from_attributes = True

class AccountCreate(BaseModel):
    name: str
    number: str
    balance: Decimal = Decimal("0.00")
    currency: str

class AccountUpdate(BaseModel):
    balance: Decimal

class AccountRowOut(BaseModel):
    id: int
    account_number: str
    balance: Decimal
    currency: str
    status: Optional[str] = "active"
    class Config:
        from_attributes = True