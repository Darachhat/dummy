from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from api.deps import get_db, get_user_id
from models import Payment, Account, Transaction, User
from core.security import verify_password
from core.config import settings
from services.osp_client import osp_lookup, osp_commit, osp_confirm, osp_reverse

router = APIRouter(prefix="/payments", tags=["Payments"])

RATE_KHR = Decimal("4000.00") 


# --- Lookup ---
@router.get("/lookup")
async def lookup(reference_number: str):
    """Verify bill with OSP."""
    result = await osp_lookup(reference_number)

    if result.get("response_code") != 200:
        raise HTTPException(status_code=400, detail="OSP lookup failed")

    return result


# --- Start Payment ---
@router.post("/start")
async def start(
    account_id: int,
    reference_number: str,
    service_id: int,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    osp_data = await osp_lookup(reference_number)
    if osp_data.get("response_code") != 200:
        raise HTTPException(status_code=400, detail="Invalid bill or OSP error")

    amount = Decimal(str(osp_data.get("amount", "0")))
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount from OSP")

    currency = osp_data.get("currency", "USD")
    customer_name = osp_data.get("customer_name", "Unknown Customer")
    session_id = osp_data.get("session_id") or f"SESS{reference_number[-4:]}"
    fee = settings.FEE_AMOUNT
    total_amount = amount + fee

    # Create payment
    payment = Payment(
        user_id=user_id,
        account_id=account_id,
        reference_number=reference_number,
        session_id=session_id,
        customer_name=customer_name,
        amount=amount,
        fee=fee,
        total_amount=total_amount,
        currency=currency,
        service_id=service_id,
        status="started",
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "response_code": 200,
        "response_msg": "Bill verified successfully",
        "payment_id": payment.id,
        "reference_number": reference_number,
        "customer_name": customer_name,
        "amount": float(amount),
        "fee": float(fee),
        "total_amount": float(total_amount),
        "currency": currency,
        "session_id": session_id,
    }


# --- Confirm Payment ---
@router.post("/{payment_id}/confirm")
async def confirm(
    payment_id: int,
    pin: str = Query(...),
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment:
        raise HTTPException(404, "Payment not found")

    user = db.query(User).get(user_id)
    if not verify_password(pin, user.pin_hash):
        raise HTTPException(401, "Invalid PIN")

    account = db.query(Account).filter_by(id=payment.account_id, user_id=user_id).first()
    if not account:
        raise HTTPException(404, "Account not found")

    if account.balance < payment.total_amount:
        raise HTTPException(402, "Insufficient funds")

    # --- Commit payment to OSP ---
    osp_commit_resp = await osp_commit(
        payment.reference_number, payment.session_id, f"TID{payment.id:06d}"
    )
    if osp_commit_resp.get("response_code") != 200:
        raise HTTPException(502, "OSP Commit Failed")

    # --- Confirm at OSP ---
    osp_confirm_resp = await osp_confirm(
        payment.reference_number,
        f"TID{payment.id:06d}",
        osp_commit_resp["acknowledgement_id"],
    )
    if osp_confirm_resp.get("response_code") != 200:
        raise HTTPException(502, "OSP Confirm Failed")

    # --- Deduct balance and log transaction ---
    account.balance -= payment.total_amount
    tx = Transaction(
        user_id=user_id,
        account_id=account.id,
        payment_id=payment.id,
        reference_number=payment.reference_number,
        amount=payment.total_amount,
        currency=payment.currency,
        direction="debit",
        description=f"Payment to {payment.customer_name} via OSP",
    )

    db.add(tx)
    db.flush()

    payment.transaction_id = tx.id
    payment.status = "confirmed"
    db.commit()

    return {
        "response_code": 200,
        "response_msg": "Payment confirmed successfully",
        "acknowledgement_id": osp_confirm_resp["acknowledgement_id"],
        "reference_number": payment.reference_number,
        "transaction_id": f"TID{payment.id:06d}",
        "customer_name": payment.customer_name,
        "amount": float(payment.amount),
        "fee": float(payment.fee),
        "total_amount": float(payment.total_amount),
        "currency": payment.currency,
    }


# --- Reverse Payment ---
@router.post("/{payment_id}/reverse")
async def reverse_payment(payment_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment or payment.status != "confirmed":
        raise HTTPException(404, "Payment not eligible for reversal")

    osp_reverse_resp = await osp_reverse(
        payment.reference_number,
        f"TID{payment.id:06d}",
        f"RTID{payment.id:06d}",
    )
    if osp_reverse_resp.get("response_code") != 200:
        raise HTTPException(502, "OSP Reverse Failed")

    account = db.query(Account).filter_by(id=payment.account_id, user_id=user_id).first()
    account.balance += payment.total_amount

    payment.status = "reversed"
    db.commit()

    return {
        "response_code": 200,
        "response_msg": "Reversal completed successfully",
        "reference_number": payment.reference_number,
        "reversal_transaction_id": f"RTID{payment.id:06d}",
        "reversal_acknowledgement_id": osp_reverse_resp["reversal_acknowledgement_id"],
    }
