from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from api.deps import get_db, get_user_id
from models import Payment, Transaction, Account, Service, User
from schemas.payment import PaymentStartOut
from core.config import settings
import uuid
import logging
from core.security import verify_password

# Auto-select mock or real OSP client
if settings.USE_MOCK_OSP:
    from services.osp_client_mockup import osp_lookup, osp_commit, osp_confirm, osp_reverse
else:
    from services.osp_client import osp_lookup, osp_commit, osp_confirm, osp_reverse

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)


# ---------- LOOKUP ----------
@router.get("/lookup")
async def lookup(reference_number: str):
    try:
        result = await osp_lookup(reference_number)
        if not result or result.get("response_code") != 200:
            raise HTTPException(status_code=400, detail=result or "Invalid response from OSP")
        return result
    except Exception as e:
        logger.exception(f"Lookup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------- START ----------
@router.post("/start", response_model=PaymentStartOut)
async def start_payment(account_id: int, reference_number: str, service_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_user_id)):
    account = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    service = db.query(Service).filter_by(id=service_id).first()
    if not account or not service:
        raise HTTPException(status_code=404, detail="Account or service not found")

    osp_data = await osp_lookup(reference_number)
    if not osp_data or osp_data.get("response_code") != 200:
        raise HTTPException(status_code=400, detail="Invalid invoice from OSP")

    currency = osp_data.get("currency", "KHR").upper()
    amount_minor = osp_data.get("amount", 0)
    amount_invoice = Decimal(str(amount_minor)) / Decimal("100")  # e.g. 200000 → 2000.00 KHR

    fee = Decimal(settings.FEE_AMOUNT)
    usd_to_khr = Decimal(settings.USD_TO_KHR_RATE)

    if currency == "KHR":
        amount_usd = (amount_invoice / usd_to_khr).quantize(Decimal("0.01"))
    else:
        amount_usd = amount_invoice

    total_usd = amount_usd + fee

    if account.balance < total_usd:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    payment = Payment(
        user_id=user_id,
        account_id=account.id,
        service_id=service.id,
        reference_number=reference_number,
        customer_name=osp_data.get("customer_name"),
        amount=amount_usd,
        fee=fee,
        total_amount=total_usd,
        currency="USD",
        invoice_currency=currency,
        invoice_amount=amount_invoice,
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
        "amount": amount_usd,
        "fee": fee,
        "total_amount": total_usd,
        "currency": "USD",
        "invoice_currency": currency,
        "invoice_amount": amount_invoice,
        "exchange_rate": usd_to_khr,
        "service": {"id": service.id, "name": service.name, "logo_url": service.logo_url},
    }


# ---------- CONFIRM ----------
@router.post("/{payment_id}/confirm")
async def confirm_payment(payment_id: int, pin: str = Query(...), user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    user = db.query(User).get(user_id)
    if not verify_password(pin, user.pin_hash):
        raise HTTPException(status_code=401, detail="Invalid PIN")

    account = db.query(Account).filter_by(id=payment.account_id, user_id=user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.balance < payment.total_amount:
        raise HTTPException(status_code=402, detail="Insufficient funds")

    session_id = payment.session_id or f"SESS{payment.id:06d}"
    transaction_id = f"TID{payment.id:06d}"

    # Commit + Confirm
    osp_commit_resp = await osp_commit(payment.reference_number, session_id=session_id, transaction_id=transaction_id)
    if osp_commit_resp.get("response_code") != 200:
        raise HTTPException(status_code=502, detail="OSP Commit Failed")

    osp_confirm_resp = await osp_confirm(payment.reference_number, transaction_id=transaction_id)
    if osp_confirm_resp.get("response_code") != 200:
        raise HTTPException(status_code=502, detail="OSP Confirm Failed")

    account.balance -= payment.total_amount

    tx = Transaction(
        user_id=user_id,
        account_id=account.id,
        payment_id=payment.id,
        reference_number=payment.reference_number,
        amount=payment.amount,
        currency="USD",
        direction="debit",
        description=f"OSP Payment for {payment.customer_name or 'Customer'} ({payment.invoice_currency})",
        created_at=datetime.utcnow(),
    )

    db.add(tx)
    payment.status = "confirmed"
    payment.transaction = tx
    db.commit()
    db.refresh(payment)
    db.refresh(tx)

    return {
        "response_code": 200,
        "response_msg": "Payment confirmed successfully",
        "reference_number": payment.reference_number,
        "transaction_id": tx.id,
        "acknowledgement_id": osp_confirm_resp.get("acknowledgement_id"),
        "customer_name": payment.customer_name,
        "invoice_currency": payment.invoice_currency,
        "invoice_amount": float(payment.invoice_amount),
        "exchange_rate": float(settings.USD_TO_KHR_RATE),
        "ledger_currency": "USD",
        "ledger_amount": float(payment.amount),
        "fee": float(payment.fee),
        "total_amount": float(payment.total_amount),
        "service_name": payment.service.name if payment.service else None,
    }


# ---------- REVERSE ----------
@router.post("/{payment_id}/reverse")
async def reverse_payment(payment_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_user_id)):
    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    res = await osp_reverse(payment.reference_number, payment.session_id)
    payment.status = "reversed"
    db.commit()
    return {"status": "reversed", "osp_response": res}
