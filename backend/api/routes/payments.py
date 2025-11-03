from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from api.deps import get_db, get_user_id
from models import Payment, Transaction, Account, Service
from schemas.payment import PaymentStartOut, PaymentConfirmOut
from core.config import settings
import uuid
import logging

# Dynamic import for mock or real OSP client
if settings.USE_MOCK_OSP is True:
    from services.osp_client_mockup import (
        osp_lookup,
        osp_commit,
        osp_confirm,
        osp_reverse,
    )
else:
    from services.osp_client import (
        osp_lookup,
        osp_commit,
        osp_confirm,
        osp_reverse,
    )

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)


# 1. Lookup Invoice (Query Payment)
@router.get("/lookup")
async def lookup(reference_number: str):
    try:
        logger.info(f"[OSP] Looking up ref {reference_number}")
        result = await osp_lookup(reference_number)
        if not result or result.get("response_code") != 200:
            raise HTTPException(status_code=400, detail=result or "Invalid response from OSP")
        return result
    except Exception as e:
        logger.exception(f"Lookup failed for {reference_number}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 2. Start Payment
@router.post("/start", response_model=PaymentStartOut)
async def start_payment(
    account_id: int,
    reference_number: str,
    service_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    account = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    service = db.query(Service).filter_by(id=service_id).first()
    if not account or not service:
        raise HTTPException(status_code=404, detail="Account or service not found")

    # Re-verify the invoice from OSP
    osp_data = await osp_lookup(reference_number)
    if not osp_data or osp_data.get("response_code") != 200:
        raise HTTPException(status_code=400, detail="Invalid invoice from OSP")

    amount = Decimal(str(osp_data.get("amount", "0"))) / Decimal("100")  # KHR -> proper decimal
    fee = Decimal(settings.DEFAULT_FEE or "0.00")
    total_amount = amount + fee

    if account.balance < total_amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Create payment record
    payment = Payment(
        user_id=user_id,
        account_id=account.id,
        service_id=service.id,
        reference_number=reference_number,
        customer_name=osp_data.get("customer_name"),
        amount=amount,
        fee=fee,
        total_amount=total_amount,
        currency=osp_data.get("currency", "KHR"),
        session_id=str(uuid.uuid4()),
        status="started",
        created_at=datetime.utcnow(),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "reference_number": payment.reference_number,
        "customer_name": payment.customer_name,
        "amount": amount,
        "fee": fee,
        "total_amount": total_amount,
        "currency": payment.currency,
        "service": {
            "id": service.id,
            "name": service.name,
            "logo_url": service.logo_url,
        },
    }


# 3. Confirm Payment (commit + confirm OSP)
@router.post("/{payment_id}/confirm", response_model=PaymentConfirmOut)
async def confirm_payment(
    payment_id: int,
    pin: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    account = db.query(Account).filter_by(id=payment.account_id, user_id=user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.balance < payment.total_amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    try:
        # Commit payment with OSP
        commit_res = await osp_commit(payment.reference_number, payment.session_id)
        if commit_res.get("response_code") != 200:
            raise HTTPException(status_code=400, detail="OSP commit failed")

        # Create transaction record
        tx = Transaction(
            user_id=user_id,
            account_id=account.id,
            payment_id=payment.id,
            reference_number=payment.reference_number,
            amount=payment.total_amount,
            currency=payment.currency,
            direction="debit",
            description=f"Payment to {payment.service.name}",
            created_at=datetime.utcnow(),
        )
        db.add(tx)

        # Deduct balance
        account.balance -= payment.total_amount

        payment.status = "committed"
        db.commit()
        db.refresh(tx)

        # Confirm with OSP
        confirm_res = await osp_confirm(payment.reference_number, tx.id)
        if confirm_res.get("response_code") != 200:
            raise HTTPException(status_code=400, detail="OSP confirm failed")

        payment.status = "confirmed"
        db.commit()

        return {
            "status": "confirmed",
            "transaction_id": tx.id,
            "account_id": account.id,
            "reference_number": payment.reference_number,
            "customer_name": payment.customer_name,
            "amount": payment.amount,
            "fee": payment.fee,
            "total_amount": payment.total_amount,
            "currency": payment.currency,
            "service": {
                "id": payment.service.id,
                "name": payment.service.name,
                "logo_url": payment.service.logo_url,
            },
        }

    except Exception as e:
        db.rollback()
        logger.exception(f"Payment confirm failed: {e}")
        raise HTTPException(status_code=500, detail=f"Confirm failed: {e}")


# 4. Reverse Payment
@router.post("/{payment_id}/reverse")
async def reverse_payment(payment_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_user_id)):
    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    try:
        res = await osp_reverse(payment.reference_number, payment.session_id)
        payment.status = "reversed"
        db.commit()
        return {"status": "reversed", "osp_response": res}
    except Exception as e:
        db.rollback()
        logger.exception(f"Reverse failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
