from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class PaymentStartOut(BaseModel):
    payment_id: int
    reference_number: str
    customer_name: Optional[str]
    amount: Decimal
    fee: Decimal
    total_amount: Decimal
    currency: str
    service: Optional[dict]


class PaymentConfirmOut(BaseModel):
    status: str
    transaction_id: int
    account_id: int
    new_balance: Decimal
    reference_number: str
    customer_name: Optional[str]
    amount: Decimal
    fee: Decimal
    total_amount: Decimal
    currency: str
    service: Optional[dict]
