from pydantic import BaseModel
from decimal import Decimal

class AccountOut(BaseModel):
    id: int
    name: str
    number: str
    balance: Decimal
    currency: str


    class Config:
        from_attributes = True