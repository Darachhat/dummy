#backend\schemas\transaction.py
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class TransactionOut(BaseModel):
    id: int
    transaction_id: int
    reference_number: Optional[str]
    description: Optional[str]
    amount: Decimal
    fee: Decimal
    total_amount: Decimal
    customer_name: Optional[str]
    service_name: Optional[str]
    service_logo_url: Optional[str]
    direction: str
    currency: str
    created_at: str

    class Config:
        from_attributes = True
