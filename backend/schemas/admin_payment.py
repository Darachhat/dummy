# backend/schemas/admin_payment.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class PaymentAdminOut(BaseModel):
    """
    Shape matches serialize_payment() output so we can drop
    raw dicts and still keep the same JSON contract.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: Optional[str] = None

    service_id: Optional[int] = None
    service_name: Optional[str] = None
    service_code: Optional[str] = None

    status: Optional[str] = None

    confirmed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    amount: Optional[float] = None
    fee: Optional[float] = None
    total_amount: Optional[float] = None

    currency: Optional[str] = None
    invoice_currency: Optional[str] = None

    reference_number: Optional[str] = None

    session_id: Optional[str] = None
    acknowledgement_id: Optional[str] = None

    cdc_transaction_datetime: Optional[datetime] = None
    cdc_transaction_datetime_utc: Optional[datetime] = None

    reversal_transaction_id: Optional[str] = None
    reversal_acknowledgement_id: Optional[str] = None

    account_id: Optional[int] = None


class PaginatedAdminPayments(BaseModel):
    items: List[PaymentAdminOut]
    total: int
    limit: int
    offset: int


class PaymentStatusUpdateIn(BaseModel):
    status: str


class PaymentStatusUpdateOut(BaseModel):
    message: str
    payment: PaymentAdminOut


class PaymentDeleteOut(BaseModel):
    message: str
