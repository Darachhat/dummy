from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.transaction import Transaction
from api.deps import get_user_id
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/admin/transactions", tags=["Admin: Transaction Management"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all transactions
@router.get("/")
def get_all_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()

# Get single transaction
@router.get("/{transaction_id}")
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).get(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# Delete transaction
@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).get(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()
    return {"message": f"Transaction ID {transaction_id} deleted successfully"}

@router.get("/{tx_db_id}")
def get_transaction(tx_db_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).get(tx_db_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.delete("/{tx_db_id}")
def delete_transaction(tx_db_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).get(tx_db_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()
    return {"message": f"Transaction ID {tx_db_id} deleted successfully"}

@router.get("/by-tid/{tid}")
def get_transaction_by_tid(tid: str, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter_by(transaction_id=tid, user_id=user_id).options(joinedload(Transaction.payment)).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found by transaction_id")
    return tx
