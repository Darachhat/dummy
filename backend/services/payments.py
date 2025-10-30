from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Account, Payment, Transaction, Service
from services.invoices import mock_lookup

FEE_CENTS = 500

def ensure_positive_amount(amount_cents: int):
    if amount_cents is None or amount_cents <= 0:
        raise HTTPException(400, "Amount must be positive")



def start_payment(db: Session, user_id: int, account_id: int, reference_number: str, service_id: int) -> Payment:
    inv = mock_lookup(reference_number)
    ensure_positive_amount(inv["amount_cents"])


    account = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    service = db.query(Service).filter_by(id=service_id).first()


    if not account:
        raise HTTPException(404, "Account not found")
    if not service:
        raise HTTPException(404, "Service not found")


    payment = Payment(
        user_id=user_id,
        account_id=account.id,
        reference_number=reference_number,
        session_id=inv["session_id"],
        amount_cents=inv["amount_cents"],
        fee_cents=FEE_CENTS,
        total_amount_cents=inv["amount_cents"] + FEE_CENTS,
        currency=inv["currency"],
        customer_name=inv["customer_name"],
        service_id=service.id,
        status="started",
    )


    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def commit_payment(db: Session, user_id: int, reference_number: str, session_id: str, transaction_id: str):
    payment = db.query(Payment).filter_by(reference_number=reference_number, user_id=user_id).first()
    if not payment:
        raise HTTPException(404, "Payment not found")

    payment.status = "committed"
    db.commit()

    return {
        "response_code": 200,
        "response_msg": "Commit success",
        "reference_number": reference_number,
        "customer_name": payment.customer_name,
        "amount": payment.amount_cents,
        "currency": payment.currency,
        "acknowledgement_id": f"AID{transaction_id[-4:]}"
    }

