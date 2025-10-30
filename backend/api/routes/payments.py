from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_user_id
from services.payments import start_payment
from services.invoices import cdc_lookup
from models import Payment, Account, Transaction, User
from core.security import verify_password

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/lookup")
def lookup(reference_number: str, partner: str = "DUMMYBANK", user_id: int = Depends(get_user_id)):
    return cdc_lookup(reference_number, partner)


@router.post("/start")
def start(account_id: int, reference_number: str, service_id: int,
          user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    p = start_payment(db, user_id, account_id, reference_number, service_id)
    return {
        "response_code": 200,
        "response_msg": "Commit success",
        "payment_id": p.id,
        "reference_number": p.reference_number,
        "customer_name": p.customer_name,
        "amount": p.amount_cents,
        "currency": p.currency,
        "acknowledgement_id": f"AID{p.id:06d}",
        "session_id": f"SESS{p.id:06d}"
    }


@router.post("/{payment_id}/confirm")
def confirm(payment_id: int, pin: str = Query(...),
            user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment or payment.status not in ["started", "committed"]:
        raise HTTPException(404, "Payment not found or invalid")

    user = db.query(User).get(user_id)
    if not verify_password(pin, user.pin_hash):
        raise HTTPException(401, "Invalid PIN")

    account = db.query(Account).filter_by(id=payment.account_id, user_id=user_id).first()
    if not account:
        raise HTTPException(404, "Account not found")
    if account.balance_cents < payment.total_amount_cents:
        raise HTTPException(402, "Insufficient funds")

    account.balance_cents -= payment.total_amount_cents
    tx = Transaction(
        user_id=user_id,
        account_id=account.id,
        reference_number=payment.reference_number,
        amount_cents=payment.total_amount_cents,
        currency=payment.currency,
        direction="debit",
        description=f"Payment to {payment.customer_name or (payment.service.name if payment.service else '')}"
    )
    db.add(tx)
    db.flush()

    payment.status = "confirmed"
    payment.transaction_id = tx.id
    db.commit()

    return {
        "response_code": 200,
        "response_msg": "Confirmed",
        "reference_number": payment.reference_number,
        "acknowledgement_id": f"AID{payment.id:06d}",
        "transaction_id": f"TID{payment.id:06d}",
        "customer_name": payment.customer_name,
        "amount": payment.amount_cents,
        "currency": payment.currency
    }

@router.post("/{payment_id}/reverse")
def reverse(payment_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment or payment.status != "confirmed":
        raise HTTPException(404, "Only confirmed payments can be reversed")

    account = db.query(Account).filter_by(id=payment.account_id, user_id=user_id).first()
    if not account:
        raise HTTPException(404, "Account not found")

    account.balance_cents += payment.amount_cents
    payment.status = "reversed"
    db.commit()

    return {
        "response_code": 200,
        "response_msg": "Reversed successfully",
        "reference_number": payment.reference_number,
        "reversal_transaction_id": f"RTID{payment.id:06d}"
    }
