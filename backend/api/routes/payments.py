# backend/api/routes/payments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal, InvalidOperation
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
from core.utils.txid import generate_transaction_id_from_id
from core.utils.currency import convert_amount
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


def _to_decimal(v, default="0.00"):
    try:
        return Decimal(str(v))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


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
    """Start payment process by verifying invoice and reserving funds on the selected account.

    Behavior (currency-aware):
      - If invoice currency == account.currency -> debit invoice amount (no conversion)
      - Else -> convert invoice amount -> account.currency and debit converted amount
      - Fee (settings.FEE_AMOUNT) is assumed USD and converted into account.currency before summing
    """
    account = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    service = db.query(Service).filter_by(id=service_id).first()

    if not account or not service:
        raise HTTPException(status_code=404, detail="Account or service not found")

    # Re-verify invoice from OSP
    osp_data = await osp_lookup(reference_number)
    if not osp_data or osp_data.get("response_code") != 200:
        raise HTTPException(status_code=400, detail="Invalid invoice from OSP")

    # Invoice details from OSP
    invoice_amount = _to_decimal(osp_data.get("amount", "0"))
    invoice_currency = (osp_data.get("currency") or "KHR").upper()

    # Account currency (what will be debited)
    account_currency = (getattr(account, "currency", "USD") or "USD").upper()

    # Fee is configured in settings (assume USD). Convert fee into account currency.
    fee_usd = _to_decimal(settings.FEE_AMOUNT or "0.00")
    fee_in_account_currency = convert_amount(fee_usd, "USD", account_currency)

    # Convert invoice -> account currency (no-op if same currency)
    invoice_converted_to_account = convert_amount(invoice_amount, invoice_currency, account_currency)

    # Total to reserve / debit from the account (in account currency)
    total_debit = (invoice_converted_to_account + fee_in_account_currency).quantize(Decimal("0.01"))

    # Check account balance (account.balance is stored as whatever currency was chosen when admin created the account)
    try:
        acct_balance = Decimal(account.balance or 0).quantize(Decimal("0.01"))
    except Exception:
        acct_balance = Decimal("0.00")

    if acct_balance < total_debit:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    osp_session_id = osp_data.get("session_id") or str(uuid.uuid4())

    # Store payment record:
    # - payment.amount kept as the original invoice amount (for front-end display we also return invoice_amount)
    # - payment.currency: set to the account currency because payment.total_amount will be stored in account-currency
    # - payment.total_amount: the actual amount that will be debited from the selected account (in account_currency)
    # - payment.fee: stored in account currency
    payment = Payment(
        user_id=user_id,
        account_id=account.id,
        service_id=service.id,
        reference_number=reference_number,
        customer_name=osp_data.get("customer_name"),
        amount=float(invoice_amount.quantize(Decimal("0.01"))),  # original invoice amount (invoice currency)
        fee=float(fee_in_account_currency.quantize(Decimal("0.01"))),
        total_amount=float(total_debit),  # amount that will be debited from account (in account_currency)
        currency=account_currency,  # currency of what will be debited (account currency)
        invoice_currency=invoice_currency,  # currency of the original invoice
        session_id=osp_session_id,
        status="started",
        created_at=datetime.utcnow(),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Return both invoice (original) and debit (account) information so frontend can present both
    return {
        "payment_id": payment.id,
        "reference_number": payment.reference_number,
        "customer_name": payment.customer_name,
        "invoice_amount": str(invoice_amount.quantize(Decimal("0.01"))),
        "invoice_currency": invoice_currency,
        "amount": str(invoice_converted_to_account),  # amount converted to account currency (what will be debited before fee)
        "fee": str(fee_in_account_currency.quantize(Decimal("0.01"))),
        "total_amount": str(total_debit),
        "currency": account_currency,  # currency of total_amount
        "usd_to_khr_rate": str(settings.USD_TO_KHR_RATE),
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
    """Finalize payment by calling OSP commit and confirm endpoints.

    Note: This endpoint expects that `payment.total_amount` is the amount (in `payment.currency`)
    that should be deducted from the selected account (this is set in /start).
    """
    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    account = db.query(Account).filter_by(id=payment.account_id, user_id=user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Ensure account has still enough balance (in case something changed between /start and /confirm)
    try:
        acct_balance = Decimal(account.balance or 0).quantize(Decimal("0.01"))
    except Exception:
        acct_balance = Decimal("0.00")

    payment_total = _to_decimal(payment.total_amount).quantize(Decimal("0.01"))
    payment_currency = (payment.currency or "USD").upper()
    account_currency = (getattr(account, "currency", "USD") or "USD").upper()

    # Defensive check: payment_currency should match account_currency (because /start stored it that way)
    if payment_currency != account_currency:
        # If mismatch, convert payment_total into account currency for comparison
        payment_total = convert_amount(payment_total, payment_currency, account_currency)

    if acct_balance < payment_total:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    try:
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

        # --- Commit Payment to OSP ---
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

        # --- Update DB (mark payment committed) ---
        payment.acknowledgement_id = commit_res.get("acknowledgement_id")
        payment.cdc_transaction_datetime = cdc_local
        payment.cdc_transaction_datetime_utc = cdc_utc
        payment.status = "committed"
        db.commit()
        db.refresh(payment)

        # --- Record Transaction (use the amount actually debited from account) ---
        # payment.total_amount is stored as a float string in account currency; ensure Decimal
        debited_amount = _to_decimal(payment.total_amount).quantize(Decimal("0.01"))

        tx = Transaction(
            user_id=user_id,
            account_id=account.id,
            payment_id=payment.id,
            reference_number=payment.reference_number,
            amount=float(debited_amount),  # amount debited from account
            currency=(payment.invoice_currency or payment.currency),     # currency of the debited amount (account currency)
            direction="debit",
            description=f"Payment to {payment.service.name if payment.service else ''}",
            created_at=datetime.utcnow(),
        )
        db.add(tx)

        # Deduct from account balance
        account.balance = (acct_balance - debited_amount).quantize(Decimal("0.01"))
        db.commit()
        db.refresh(tx)

        try:
            tx.transaction_id = generate_transaction_id_from_id(tx.id, tx.created_at or datetime.utcnow())
            db.add(tx)
            db.commit()
            db.refresh(tx)
        except Exception:
            db.rollback()

        # --- Confirm Payment with OSP ---
        ack_id = payment.acknowledgement_id
        confirm_res = await osp_confirm(payment.reference_number, tx.transaction_id, ack_id)
        logger.info(f"[OSP Confirm Response] {confirm_res}")

        if confirm_res.get("response_code") != 200:
            raise HTTPException(status_code=400, detail="OSP confirm failed")

        payment.status = "confirmed"
        payment.confirmed_at = datetime.utcnow()
        db.commit()

        # --- Prepare local time for UI ---
        local_cdc_time = to_local_time(payment.cdc_transaction_datetime)

        return {
            "status": "confirmed",
            "transaction_id": tx.transaction_id or str(tx.id),
            "account_id": account.id,
            "reference_number": payment.reference_number,
            "customer_name": payment.customer_name,
            "amount": float(_to_decimal(payment.amount).quantize(Decimal("0.01"))),
            "invoice_amount": float(_to_decimal(payment.amount).quantize(Decimal("0.01"))),
            "amount_debited": float(debited_amount),
            "fee": float(_to_decimal(payment.fee).quantize(Decimal("0.01"))),
            "total_amount": float(debited_amount), 
            "currency": payment.currency,
            "invoice_currency": payment.invoice_currency,
            "new_balance": float(account.balance),
            "cdc_transaction_datetime": payment.cdc_transaction_datetime.strftime("%Y-%m-%d %H:%M:%S") if payment.cdc_transaction_datetime else None,
            "cdc_transaction_datetime_utc": payment.cdc_transaction_datetime_utc.strftime("%Y-%m-%d %H:%M:%S") if payment.cdc_transaction_datetime_utc else None,
            "cdc_transaction_datetime_local": local_cdc_time,
            "service": {
                "id": payment.service.id if payment.service else None,
                "name": payment.service.name if payment.service else None,
                "logo_url": payment.service.logo_url if payment.service else None,
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
