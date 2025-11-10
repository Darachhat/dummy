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
import httpx 
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
from core.utils.timezone import to_local_time  


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


# Lookup Invoice (Query Payment)
@router.get("/lookup")
async def lookup(reference_number: str):
    """Query OSP for payment info"""
    try:
        result = await osp_lookup(reference_number)
        return result
    except httpx.HTTPStatusError as e:
        # Handle specific 423 Locked status from OSP
        if e.response.status_code == 423:
            return JSONResponse(
                status_code=423,
                content={
                    "detail": "This invoice has already been paid.",
                    "reference_number": reference_number,
                },
            )
        # Handle all other HTTP errors
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"OSP Error: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#  Start Payment
@router.post("/start", response_model=PaymentStartOut)
async def start_payment(
    account_id: int,
    reference_number: str,
    service_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """Start payment process by verifying and reserving funds"""
    account = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    service = db.query(Service).filter_by(id=service_id).first()

    if not account or not service:
        raise HTTPException(status_code=404, detail="Account or service not found")

    # Re-verify invoice from OSP
    osp_data = await osp_lookup(reference_number)
    if not osp_data or osp_data.get("response_code") != 200:
        raise HTTPException(status_code=400, detail="Invalid invoice from OSP")

    # Convert and calculate totals
    invoice_amount_khr = Decimal(str(osp_data.get("amount", "0"))) 
    invoice_currency = osp_data.get("currency", "KHR")

    # --- Currency handling ---
    USD_TO_KHR_RATE = Decimal("4000")
    if invoice_currency == "KHR":
        amount_usd = (invoice_amount_khr / USD_TO_KHR_RATE)
    else:
        amount_usd = invoice_amount_khr

    fee_usd = Decimal(settings.FEE_AMOUNT or "0.00")
    total_usd = amount_usd + fee_usd

    if account.balance < total_usd:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    osp_session_id = osp_data.get("session_id") or str(uuid.uuid4())

    # Store as USD in database
    payment = Payment(
        user_id=user_id,
        account_id=account.id,
        service_id=service.id,
        reference_number=reference_number,
        customer_name=osp_data.get("customer_name"),
        amount=amount_usd,
        fee=fee_usd,
        total_amount=total_usd,
        currency="USD",
        session_id=osp_session_id,
        status="started",
        created_at=datetime.utcnow(),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Return both KHR + USD for frontend display
    return {
        "payment_id": payment.id,
        "reference_number": payment.reference_number,
        "customer_name": payment.customer_name,
        "amount": str(amount_usd),
        "fee": str(fee_usd),
        "total_amount": str(total_usd),
        "currency": "USD",
        "invoice_amount": str(invoice_amount_khr),
        "invoice_currency": invoice_currency,
        "usd_to_khr_rate": str(USD_TO_KHR_RATE),
        "service": {
            "id": service.id,
            "name": service.name,
            "logo_url": service.logo_url,
        },
    }



# Confirm Payment (Commit + Confirm)
@router.post("/{payment_id}/confirm", response_model=PaymentConfirmOut)
async def confirm_payment(
    payment_id: int,
    pin: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """Finalize payment by calling OSP commit and confirm endpoints."""
    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    account = db.query(Account).filter_by(id=payment.account_id, user_id=user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.balance < payment.total_amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    try:
        import uuid
        transaction_id = f"TID{payment.id:06d}{uuid.uuid4().hex[:2]}"
        logger.info(f"[Payment Confirm] Start Ref={payment.reference_number}, Txn={transaction_id}")

        # 🔁 Always refresh session before commit
        lookup_res = await osp_lookup(payment.reference_number)
        if lookup_res.get("response_code") == 200:
            payment.session_id = lookup_res.get("session_id")
            db.commit()
            logger.info(f"[Payment Confirm] Refreshed session_id={payment.session_id}")
        else:
            raise HTTPException(status_code=400, detail="Invalid invoice or expired session from OSP")

        # --- Commit Payment ---
        commit_res = await osp_commit(payment.reference_number, payment.session_id, transaction_id)
        logger.info(f"[OSP Commit Response] {commit_res}")

        if commit_res.get("response_code") != 200:
            raise HTTPException(status_code=400, detail="OSP commit failed")

        # --- Convert CDC Datetime (UTC+7 and UTC) ---
        cdc_dt_str = commit_res.get("cdc_transaction_datetime")
        cdc_local = cdc_utc = None
        if cdc_dt_str:
            try:
                cdc_local = datetime.strptime(cdc_dt_str, "%Y-%m-%d %H:%M:%S")
                cdc_utc = (cdc_local - timedelta(hours=7)).replace(tzinfo=timezone.utc)
            except Exception as e:
                logger.warning(f"[CDC Time Parse Error] {cdc_dt_str}: {e}")

        # --- Update DB ---
        payment.acknowledgement_id = commit_res.get("acknowledgement_id")
        payment.cdc_transaction_datetime = cdc_local
        payment.cdc_transaction_datetime_utc = cdc_utc
        payment.status = "committed"
        db.commit()
        db.refresh(payment)

        # --- Record Transaction ---
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
        account.balance -= payment.total_amount
        db.commit()
        db.refresh(tx)

        # --- Confirm Payment ---
        ack_id = payment.acknowledgement_id
        confirm_res = await osp_confirm(payment.reference_number, transaction_id, ack_id)
        logger.info(f"[OSP Confirm Response] {confirm_res}")

        if confirm_res.get("response_code") != 200:
            raise HTTPException(status_code=400, detail="OSP confirm failed")

        payment.status = "confirmed"
        db.commit()

        # --- Prepare local time for UI ---
        local_cdc_time = to_local_time(payment.cdc_transaction_datetime)

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
            "new_balance": float(account.balance),
            "cdc_transaction_datetime": payment.cdc_transaction_datetime.strftime("%Y-%m-%d %H:%M:%S") if payment.cdc_transaction_datetime else None,
            "cdc_transaction_datetime_utc": payment.cdc_transaction_datetime_utc.strftime("%Y-%m-%d %H:%M:%S") if payment.cdc_transaction_datetime_utc else None,
            "cdc_transaction_datetime_local": local_cdc_time,
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


# Reverse Payment
@router.post("/{payment_id}/reverse")
async def reverse_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """Reverse a previously started or failed payment"""
    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    try:
        res = await osp_reverse(payment.reference_number, payment.session_id)
        logger.info(f"[OSP Reverse Response] {res}")

        payment.status = "reversed"
        db.commit()
        return {"status": "reversed", "osp_response": res}

    except Exception as e:
        db.rollback()
        logger.exception(f"Reverse failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
