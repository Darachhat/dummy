# backend/api/routes/admin/transaction_management.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Any, Dict

from api.deps import get_db
from core.permissions import require_admin
from models.transaction import Transaction
from models.payment import Payment
from models.account import Account
from models.user import User
from schemas.admin_transaction import (
    AdminTransactionOut,
    PaginatedAdminTransactions,
    AdminTransactionDeleteOut,
)

router = APIRouter(
    prefix="/adm/transactions",
    tags=["Admin: Transaction Management"],
    dependencies=[Depends(require_admin)],
)


def serialize_tx(tx: Transaction) -> Dict[str, Any]:
    def g(attr, default=None):
        return getattr(tx, attr, default)

    p = getattr(tx, "payment", None)
    acc = getattr(tx, "account", None)
    acc_user = getattr(acc, "user", None) if acc is not None else None
    svc = getattr(p, "service", None) if p is not None else None

    # base common fields from transaction model
    base = {
        "id": g("id"),
        "transaction_id": g("transaction_id"),
        "direction": g("direction"),
        "created_at": g("created_at"),
    }

    # account / user info (prefer account relationship)
    base["account_number"] = getattr(acc, "number", None) if acc is not None else None
    base["account_id"] = getattr(acc, "id", None) if acc is not None else g("account_id")
    base["user_name"] = getattr(acc_user, "name", None) if acc_user is not None else None
    base["user_phone"] = getattr(acc_user, "phone", None) if acc_user is not None else None

    # transaction-level amount fields (fallbacks will be applied below)
    tx_amount = g("amount")
    tx_fee = g("fee")
    tx_total = g("total_amount")

    if p:
        # prefer payment values where available
        payment_amount = getattr(p, "amount", None)
        payment_fee = getattr(p, "fee", None)
        payment_total = getattr(p, "total_amount", None)

        base.update({
            "reference_number": getattr(p, "reference_number", None),
            "description": getattr(tx, "description", None) or getattr(p, "reference_number", None),
            "amount": float(payment_amount) if payment_amount is not None else (float(tx_amount) if tx_amount is not None else None),
            "fee": float(payment_fee) if payment_fee is not None else (float(tx_fee) if tx_fee is not None else None),
            "total_amount": float(payment_total) if payment_total is not None else (float(tx_total) if tx_total is not None else None),
            "customer_name": getattr(p, "customer_name", None),
            "service_name": getattr(svc, "name", None) if svc is not None else None,
            "service_logo_url": getattr(svc, "logo_url", None) if svc is not None else None,
            "direction": g("direction"),
            # currency and invoice_currency come from payment first
            "currency": getattr(p, "currency", None) or g("currency"),
            "invoice_currency": getattr(p, "invoice_currency", None),
            # status comes from payment
            "status": getattr(p, "status", None),
        })
    else:
        # no payment linked — show transaction values
        base.update({
            "reference_number": g("reference_number"),
            "description": g("description"),
            "amount": float(tx_amount) if tx_amount is not None else None,
            "fee": float(tx_fee) if tx_fee is not None else None,
            "total_amount": float(tx_total) if tx_total is not None else None,
            "customer_name": None,
            "service_name": None,
            "service_logo_url": None,
            "currency": g("currency"),
            "invoice_currency": g("invoice_currency", None),
            "status": g("status", None),
        })

    return base


@router.get(
    "/",
    summary="List transactions (admin)",
    response_model=PaginatedAdminTransactions,
)
def list_transactions(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    offset: int = 0,
):
    """
    Returns paginated transactions serialized for admin UI.
    Preloads payment, payment.service, account and account.user to avoid N+1.
    """
    q = (
        db.query(Transaction)
        .options(
            # load related payment -> service
            joinedload(Transaction.payment).joinedload(Payment.service),
            # load transaction.account -> account.user
            joinedload(Transaction.account).joinedload(Account.user),
        )
    )

    total = q.count()
    txs = q.order_by(Transaction.created_at.asc()).offset(offset).limit(limit).all()
    items = [AdminTransactionOut(**serialize_tx(t)) for t in txs]

    return PaginatedAdminTransactions(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{tx_id}",
    summary="Get transaction by DB id",
    response_model=AdminTransactionOut,
)
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = (
        db.query(Transaction)
        .options(
            joinedload(Transaction.payment).joinedload(Payment.service),
            joinedload(Transaction.account).joinedload(Account.user),
        )
        .filter(Transaction.id == tx_id)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return AdminTransactionOut(**serialize_tx(tx))


@router.delete(
    "/{tx_id}",
    summary="Delete transaction",
    response_model=AdminTransactionDeleteOut,
)
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(tx)
    db.commit()
    return AdminTransactionDeleteOut(message=f"Transaction {tx_id} deleted")


@router.get(
    "/by-tid/{tid}",
    summary="Get transaction by transaction_id (admin)",
    response_model=AdminTransactionOut,
)
def get_transaction_by_tid(tid: str, db: Session = Depends(get_db)):
    tx = (
        db.query(Transaction)
        .options(
            joinedload(Transaction.payment).joinedload(Payment.service),
            joinedload(Transaction.account).joinedload(Account.user),
        )
        .filter(Transaction.transaction_id == tid)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return AdminTransactionOut(**serialize_tx(tx))
