from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.transaction import Transaction

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
