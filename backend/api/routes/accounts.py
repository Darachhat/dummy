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

    # ✅ One joined query to fetch everything efficiently
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
