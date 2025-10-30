from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_user_id
from models import Transaction, Payment


router = APIRouter(prefix="/transactions", tags=["transactions"])
@router.get("")
def list_transactions(user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    txs = db.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()


    results = []
    for t in txs:
        payment = db.query(Payment).filter_by(transaction_id=t.id).first()
        results.append({
            "id": t.id,
            "transaction_id": t.id,
            "reference_number": payment.reference_number if payment else t.reference_number,
            "description": t.description,
            "amount_cents": payment.amount_cents if payment else t.amount_cents,
            "fee_cents": payment.fee_cents if payment else 0,
            "total_amount_cents": payment.total_amount_cents if payment else t.amount_cents,
            "customer_name": payment.customer_name if payment else None,
            "service_name": payment.service.name if payment and payment.service else None,
            "service_logo_url": payment.service.logo_url if payment and payment.service else None,
            "direction": t.direction,
            "created_at": t.created_at,
        })
    return results


@router.get("/{transaction_id}")
def get_transaction(transaction_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter_by(id=transaction_id, user_id=user_id).first()
    if not tx:
        raise HTTPException(404, "Transaction not found")


    payment = db.query(Payment).filter_by(transaction_id=tx.id).first()
    if not payment:
        return {
            "transaction_id": tx.id,
            "reference_number": tx.reference_number,
            "description": tx.description,
            "amount_cents": tx.amount_cents,
            "currency": tx.currency,
            "direction": tx.direction,
            "created_at": tx.created_at,
        }


    return {
        "transaction_id": tx.id,
        "reference_number": payment.reference_number,
        "customer_name": payment.customer_name,
        "amount_cents": payment.amount_cents,
        "fee_cents": payment.fee_cents,
        "total_amount_cents": payment.total_amount_cents,
        "service_name": payment.service.name if payment.service else None,
        "service_logo_url": payment.service.logo_url if payment.service else None,
        "account_id": payment.account_id,
        "currency": payment.currency,
        "direction": tx.direction,
        "created_at": tx.created_at,
    }