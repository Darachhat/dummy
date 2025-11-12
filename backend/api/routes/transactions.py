from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_user_id
from models import Transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/")
def list_transactions(user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    """Return all user transactions with linked payment and service info."""
    txs = (
        db.query(Transaction)
        .filter_by(user_id=user_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    results = []
    for t in txs:
        p = t.payment 
        results.append({
            "id": t.id,
            "transaction_id": t.transaction_id,
            "reference_number": p.reference_number if p else t.reference_number,
            "description": t.description,
            "amount": float(p.amount if p else t.amount),
            "fee": float(p.fee if p else 0),
            "total_amount": float(p.total_amount if p else t.amount),
            "customer_name": p.customer_name if p else None,
            "service_name": p.service.name if p and p.service else None,
            "service_logo_url": p.service.logo_url if p and p.service else None,
            "direction": t.direction,
            "currency": t.currency,
            "created_at": t.created_at,
        })
    return results


@router.get("/{transaction_id}")
def get_transaction(transaction_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    """Get a single transaction, with payment + service details if available."""
    tx = db.query(Transaction).filter_by(id=transaction_id, user_id=user_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    p = tx.payment
    if not p:
        return {
            "transaction_id": tx.transaction_id,
            "reference_number": tx.reference_number,
            "description": tx.description,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "direction": tx.direction,
            "created_at": tx.created_at,
        }

    return {
        "transaction_id": tx.transaction_id,
        "reference_number": p.reference_number,
        "customer_name": p.customer_name,
        "amount": float(p.amount),
        "fee": float(p.fee),
        "total_amount": float(p.total_amount),
        "service_name": p.service.name if p.service else None,
        "service_logo_url": p.service.logo_url if p.service else None,
        "account_id": p.account_id,
        "currency": p.currency,
        "direction": tx.direction,
        "created_at": tx.created_at,
    }
