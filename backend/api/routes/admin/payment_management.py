# backend\api\routes\admin\payment_management.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.payment import Payment

router = APIRouter(prefix="/admin/payments", tags=["Admin: Payment Management"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all payments
@router.get("/")
def get_all_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()

# Get single payment
@router.get("/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

# Delete payment
@router.delete("/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    db.delete(payment)
    db.commit()
    return {"message": f"Payment ID {payment_id} deleted successfully"}
