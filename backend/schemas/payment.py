from pydantic import BaseModel
from typing import Optional


class PaymentStartOut(BaseModel):
    payment_id: int
    reference_number: str
    customer_name: Optional[str]
    amount_cents: int
    fee_cents: int
    total_amount_cents: int
    service: dict


class PaymentConfirmOut(BaseModel):
    status: str
    transaction_id: int
    account_id: int
    new_balance_cents: int
    reference_number: str
    customer_name: str | None
    amount_cents: int
    fee_cents: int
    total_amount_cents: int
    service: dict