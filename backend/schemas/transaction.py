from pydantic import BaseModel
from typing import Optional


class TransactionOut(BaseModel):
    id: int
    transaction_id: int
    reference_number: Optional[str]
    description: str
    amount_cents: int
    fee_cents: int
    total_amount_cents: int
    customer_name: Optional[str]
    service_name: Optional[str]
    service_logo_url: Optional[str]
    direction: str
    created_at: str


    class Config:
        from_attributes = True