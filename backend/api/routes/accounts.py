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
    total = sum(a.balance for a in accounts)  

    return {
        "user": {"id": user.id, "phone": user.phone},
        "total_balance": float(total), 
        "accounts": [AccountOut.model_validate(a).model_dump() for a in accounts],
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
