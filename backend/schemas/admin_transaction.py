# backend/schemas/admin_transaction.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AdminTransactionOut(BaseModel):
    id: int
    transaction_id: Optional[str] = None
    direction: Optional[str] = None
    created_at: Optional[datetime] = None

    account_number: Optional[str] = None
    account_id: Optional[int] = None
    user_name: Optional[str] = None
    user_phone: Optional[str] = None

    reference_number: Optional[str] = None
    description: Optional[str] = None

    amount: Optional[float] = None
    fee: Optional[float] = None
    total_amount: Optional[float] = None

    customer_name: Optional[str] = None
    service_name: Optional[str] = None
    service_logo_url: Optional[str] = None

    currency: Optional[str] = None
    invoice_currency: Optional[str] = None
    status: Optional[str] = None


class PaginatedAdminTransactions(BaseModel):
    items: List[AdminTransactionOut]
    total: int
    limit: int
    offset: int


class AdminTransactionDeleteOut(BaseModel):
    message: str
