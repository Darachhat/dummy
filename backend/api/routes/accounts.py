# backend/api/routes/accounts.py
from core.utils.currency import convert_amount
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from decimal import Decimal
from api.deps import get_db, get_user_id
from models import User, Account
from schemas.account import AccountOut
from decimal import Decimal
from models import Transaction, Payment, Account, Service
from typing import List

router = APIRouter(tags=["accounts"])


@router.get("/me")
def me(user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    accounts = db.query(Account).filter_by(user_id=user_id).all()

    out_accounts = []
    total_display = Decimal("0.00")

    for a in accounts:
        try:
            stored_amount = Decimal(a.balance or 0).quantize(Decimal("0.01"))
        except Exception:
            stored_amount = Decimal("0.00")

        stored_currency = (getattr(a, "currency", "USD") or "USD").upper()

        out_accounts.append({
            "id": a.id,
            "name": getattr(a, "name", None),
            "number": getattr(a, "number", getattr(a, "account_number", None)),
        
            "balance": float(stored_amount),
            "currency": stored_currency,
            "stored_balance": float(stored_amount),
            "stored_currency": stored_currency,
            "status": getattr(a, "status", "active"),
        })
        total_display += stored_amount

    return {
        "user": {"id": user.id, "phone": user.phone},
        "total_balance": float(total_display.quantize(Decimal("0.01"))),
        "accounts": out_accounts,
    }


@router.get("/accounts/{account_id}")
def account_detail(account_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    a = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountOut.model_validate(a)

@router.get("/accounts/{account_id}/transactions")
def account_transactions(
    account_id: int,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    """
    Return all transactions for an account, with related payment + service info
    in a single optimized query (no N+1 queries).
    """
    account = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # One joined query to fetch everything efficiently
    txs = (
        db.query(Transaction)
        .outerjoin(Payment, Payment.id == Transaction.payment_id)
        .outerjoin(Service, Service.id == Payment.service_id)
        .filter(Transaction.account_id == account.id, Transaction.user_id == user_id)
        .options(
            joinedload(Transaction.payment).joinedload(Payment.service)
        )
        .order_by(Transaction.created_at.desc())
        .all()
    )

    # Construct results
    result = [
        {
            "id": t.id,
            'transaction_id': t.transaction_id,
            "reference_number": t.reference_number,
            "description": t.description or "",
            "amount": float(t.amount),
            "currency": t.currency,
            "direction": t.direction,
            "customer_name": getattr(t.payment, "customer_name", None),
            "service_name": getattr(t.payment.service, "name", None)
                if t.payment and t.payment.service else None,
            "service_logo_url": getattr(t.payment.service, "logo_url", None)
                if t.payment and t.payment.service else None,
            "created_at": t.created_at,
        }
        for t in txs
    ]

    return result

@router.get("/accounts/{account_id}/transactions/{transaction_id}")
def get_transaction_detail(
    account_id: int,
    transaction_id: int,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    """
    Return a single transaction for an account, including payment + service info.
    """
    tx = (
        db.query(Transaction)
        .filter_by(id=transaction_id, account_id=account_id, user_id=user_id)
        .options(joinedload(Transaction.payment).joinedload(Payment.service))
        .first()
    )

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    payment = tx.payment
    service = payment.service if payment and payment.service else None

    return {
        "id": tx.id,
        "transaction_id": tx.transaction_id,
        "reference_number": tx.reference_number,
        "description": tx.description or "",
        "amount": float(tx.amount),
        "currency": tx.currency,
        "direction": tx.direction,
        "customer_name": getattr(payment, "customer_name", None),
        "service": {
            "name": getattr(service, "name", None),
            "logo_url": getattr(service, "logo_url", None),
        } if service else None,
        "account": {
            "id": tx.account.id,
            "number": tx.account.number,
            "name": tx.account.name,
        } if tx.account else None,
        "created_at": tx.created_at,
    }
