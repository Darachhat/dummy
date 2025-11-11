#backend\schemas\payment.py 
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from datetime import datetime
from core.utils.timezone import to_local_time

class PaymentRowOut(BaseModel):
    id: int
    method: Optional[str] = None
    amount: Decimal
    currency: str
    created_at: str
    class Config:
        from_attributes = True


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
    cdc_transaction_datetime: Optional[datetime] = None 

    class Config:
        from_attributes = True

    # Custom dict override for timezone formatting
    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        if self.cdc_transaction_datetime:
            data["cdc_transaction_datetime"] = to_local_time(self.cdc_transaction_datetime)
        return data
