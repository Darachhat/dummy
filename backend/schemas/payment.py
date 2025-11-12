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
    transaction_id: Optional[str] = None
    account_id: int
    new_balance: Decimal
    reference_number: str
    customer_name: Optional[str]
    amount: Decimal
    fee: Decimal
    total_amount: Decimal
    currency: str
    service: Optional[dict]
    session_id: Optional[str] = None
    acknowledgement_id: Optional[str] = None
    cdc_transaction_datetime: Optional[datetime] = None
    cdc_transaction_datetime_utc: Optional[datetime] = None
    reversal_transaction_id: Optional[str] = None
    reversal_acknowledgement_id: Optional[str] = None
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        # convert datetimes to local strings
        if self.cdc_transaction_datetime:
            data["cdc_transaction_datetime"] = to_local_time(self.cdc_transaction_datetime)
        if self.cdc_transaction_datetime_utc:
            # keep UTC string too (isoformat)
            data["cdc_transaction_datetime_utc"] = (self.cdc_transaction_datetime_utc.isoformat()
                                                    if isinstance(self.cdc_transaction_datetime_utc, datetime) else self.cdc_transaction_datetime_utc)
        if self.created_at:
            data["created_at"] = to_local_time(self.created_at)
        if self.confirmed_at:
            data["confirmed_at"] = to_local_time(self.confirmed_at)
        return data

