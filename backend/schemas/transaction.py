# backend/schemas/transaction.py
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class TransactionOut(BaseModel):
    id: int
    transaction_id: Optional[str] = None
    reference_number: Optional[str] = None
    description: Optional[str] = None

    amount: Optional[Decimal] = None
    fee: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None

    customer_name: Optional[str] = None
    service_name: Optional[str] = None
    service_logo_url: Optional[str] = None

    direction: Optional[str] = None
    currency: Optional[str] = None

    account_id: Optional[int] = None
    created_at: Optional[datetime] = None


class PaginatedTransactions(BaseModel):
    items: List[TransactionOut]
    total: int
    page: int
    page_size: int
