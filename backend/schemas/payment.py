# backend/schemas/payment.py
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class PaymentServiceInfo(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    logo_url: Optional[str] = None


class PaymentStartOut(BaseModel):
    payment_id: int
    reference_number: str
    customer_name: Optional[str] = None

    invoice_amount: Optional[Decimal] = None
    invoice_currency: Optional[str] = None

    # debited amount in account currency
    amount: Optional[Decimal] = None
    fee: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None

    currency: Optional[str] = None
    usd_to_khr_rate: Optional[Decimal] = None

    service: PaymentServiceInfo


class PaymentConfirmOut(BaseModel):

    status: str

    transaction_id: Optional[str] = None
    account_id: Optional[int] = None

    # Account balance after payment (confirm endpoint sets this; admin listing may set 0)
    new_balance: Optional[Decimal] = None

    reference_number: str
    customer_name: Optional[str] = None

    # Display amount – may be invoice or debited amount depending on context
    amount: Optional[Decimal] = None
    # Explicit debited amount for confirm endpoint
    amount_debited: Optional[Decimal] = None

    fee: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None

    currency: Optional[str] = None

    # Service info
    service: Optional[PaymentServiceInfo] = None

    # Extra metadata
    session_id: Optional[str] = None
    acknowledgement_id: Optional[str] = None

    cdc_transaction_datetime: Optional[datetime] = None
    cdc_transaction_datetime_utc: Optional[datetime] = None
    # Confirm endpoint uses a preformatted string here
    cdc_transaction_datetime_local: Optional[str] = None

    reversal_transaction_id: Optional[str] = None
    reversal_acknowledgement_id: Optional[str] = None

    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
