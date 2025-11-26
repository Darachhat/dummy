# backend/api/routes/payments.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from decimal import Decimal, InvalidOperation
from api.deps import get_db, get_user_id
from core.logging import logger


from models import Payment, Transaction, Account, Service
from models.user import User
import re

from schemas.payment import PaymentStartOut, PaymentConfirmOut

import uuid
import logging
import httpx
from datetime import datetime, timedelta, timezone

from core.utils.timezone import to_local_time
from core.utils.payments import mark_confirmed
from core.utils.txid import generate_transaction_id_from_id
from core.utils.currency import convert_amount
from core.config import settings
from core.security import verify_password

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
logger = logger.bind(module="api.routes.payments")


def log_osp_response(ctx: dict, op: str, response: dict | None):
    logger.bind(**ctx).info(
        f"osp_{op}_response",
        response=response if isinstance(response, dict) else str(response)
    )



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


# Start Payment
@router.post("/start", response_model=PaymentStartOut)
async def start_payment(
    account_id: int,
    reference_number: str,
    service_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    start_ts = datetime.utcnow()
    ctx = {"user_id": user_id, "account_id": account_id, "reference_number": reference_number, "service_id": service_id}
    logger.bind(**ctx).info("start_payment requested")

    account = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    service = db.query(Service).filter_by(id=service_id).first()

    if not account or not service:
        logger.bind(**ctx).warning("account or service not found")
        raise HTTPException(status_code=404, detail="Account or service not found")

    # Re-verify invoice from OSP
    try:
        osp_data = await osp_lookup(reference_number)
        log_osp_response(ctx, "lookup", osp_data)
    except Exception as e:
        logger.bind(**ctx).exception("osp_lookup failed")
        raise HTTPException(status_code=500, detail="OSP lookup failed")

    if not osp_data or osp_data.get("response_code") != 200:
        logger.bind(**ctx).warning("invalid invoice from osp", osp_response_code=osp_data.get("response_code") if osp_data else None)
        raise HTTPException(status_code=400, detail="Invalid invoice from OSP")

    # Invoice details from OSP
    invoice_amount = _to_decimal(osp_data.get("amount", "0"))
    invoice_currency = (osp_data.get("currency") or "KHR").upper()
    account_currency = (getattr(account, "currency", "USD") or "USD").upper()

    # Fee conversion
    fee_usd = _to_decimal(settings.FEE_AMOUNT or "0.00")
    fee_in_account_currency = convert_amount(fee_usd, "USD", account_currency)
    invoice_converted_to_account = convert_amount(invoice_amount, invoice_currency, account_currency)

    total_debit = (invoice_converted_to_account + fee_in_account_currency).quantize(Decimal("0.01"))

    try:
        acct_balance = Decimal(account.balance or 0).quantize(Decimal("0.01"))
    except Exception:
        acct_balance = Decimal("0.00")

    logger.bind(**ctx).debug(
        "balance_check",
        invoice_amount=str(invoice_amount),
        invoice_currency=invoice_currency,
        invoice_converted=str(invoice_converted_to_account),
        fee=str(fee_in_account_currency),
        total_debit=str(total_debit),
        acct_balance=str(acct_balance),
    )

    if acct_balance < total_debit:
        logger.bind(**ctx).warning("insufficient balance", acct_balance=str(acct_balance), required=str(total_debit))
        raise HTTPException(status_code=400, detail="Insufficient balance")

    osp_session_id = osp_data.get("session_id") or str(uuid.uuid4())

    # Store payment record
    payment = Payment(
        user_id=user_id,
        account_id=account.id,
        service_id=service.id,
        reference_number=reference_number,
        customer_name=osp_data.get("customer_name"),
        amount=float(invoice_amount.quantize(Decimal("0.01"))),
        fee=float(fee_in_account_currency.quantize(Decimal("0.01"))),
        total_amount=float(total_debit),
        currency=account_currency,
        invoice_currency=invoice_currency,
        session_id=osp_session_id,
        status="started",
        created_at=datetime.utcnow(),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    logger.bind(payment_id=payment.id, **ctx).info("payment_started", payment_id=payment.id, session_id=osp_session_id)

    elapsed = (datetime.utcnow() - start_ts).total_seconds()
    logger.bind(payment_id=payment.id, **ctx).info("start_payment completed", elapsed_s=elapsed)

    return PaymentStartOut(
        payment_id=payment.id,
        reference_number=payment.reference_number,
        customer_name=payment.customer_name,
        invoice_amount=str(invoice_amount.quantize(Decimal("0.01"))),
        invoice_currency=invoice_currency,
        amount=str(invoice_converted_to_account.quantize(Decimal("0.01"))),
        fee=str(fee_in_account_currency.quantize(Decimal("0.01"))),
        total_amount=str(total_debit),
        currency=account_currency,
        usd_to_khr_rate=str(settings.USD_TO_KHR_RATE),
        service={
            "id": service.id,
            "name": service.name,
            "logo_url": service.logo_url,
        },
    )



# Confirm Payment (Commit + Confirm)
@router.post("/{payment_id}/confirm", response_model=PaymentConfirmOut)
async def confirm_payment(
    payment_id: int,
    pin: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    start_ts = datetime.utcnow()
    ctx = {"user_id": user_id, "payment_id": payment_id}
    logger.bind(**ctx).info("confirm_payment requested")

    payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not payment:
        logger.bind(**ctx).warning("payment not found")
        raise HTTPException(status_code=404, detail="Payment not found")

    account = db.query(Account).filter_by(id=payment.account_id, user_id=user_id).first()
    if not account:
        logger.bind(**ctx).warning("account not found for payment", account_id=payment.account_id)
        raise HTTPException(status_code=404, detail="Account not found")

    # PIN validation
    if not isinstance(pin, str) or not re.fullmatch(r"\d{4}", pin):
        logger.bind(**ctx).warning("invalid_pin_format")
        raise HTTPException(status_code=400, detail="PIN must be exactly 4 numeric digits")

    user = db.query(User).filter_by(id=user_id).first()
    if not user or not getattr(user, "pin_hash", None):
        logger.bind(**ctx).warning("pin_not_set_for_user")
        raise HTTPException(status_code=401, detail="PIN not set for user")

    if not verify_password(pin, user.pin_hash):
        logger.bind(**ctx).warning("invalid_pin_attempt")
        raise HTTPException(status_code=402, detail="Invalid PIN")

    try:
        #commit transaction id sent to OSP commit
        commit_tid = generate_transaction_id_from_id(payment.id, datetime.utcnow())
        logger.bind(commit_tid=commit_tid, **ctx).info("payment_confirm_flow_start")

        # Refresh invoice/session from OSP
        lookup_res = await osp_lookup(payment.reference_number)
        if lookup_res.get("response_code") == 200:
            payment.session_id = lookup_res.get("session_id")
            db.commit()
            logger.bind(**ctx).info("session_refreshed", session_id=payment.session_id)
        else:
            logger.bind(**ctx).warning("osp_lookup_on_confirm_failed", osp_code=lookup_res.get("response_code"))
            raise HTTPException(status_code=400, detail="Invalid invoice or expired session from OSP")

        # Commit payment to OSP 
        commit_res = await osp_commit(payment.reference_number, payment.session_id, commit_tid)
        log_osp_response(ctx, "commit", commit_res)
        logger.bind(**ctx).debug(
            "osp_commit",
            response_code=commit_res.get("response_code"),
            commit_tid=commit_tid,
            osp_transaction_id=commit_res.get("transaction_id")
        )

        if commit_res.get("response_code") != 200:
            logger.bind(**ctx).error("osp_commit_failed", osp_response=commit_res)
            raise HTTPException(status_code=400, detail="OSP commit failed")

        # OSP's definitive transaction ID
        osp_tid = commit_res.get("transaction_id")

        # Parse CDC datetime
        cdc_dt_str = commit_res.get("cdc_transaction_datetime")
        cdc_local = cdc_utc = None
        if cdc_dt_str:
            try:
                cdc_local = datetime.strptime(cdc_dt_str, "%Y-%m-%d %H:%M:%S")
                cdc_utc = (cdc_local - timedelta(hours=7)).replace(tzinfo=timezone.utc)
            except Exception as e:
                logger.bind(**ctx).warning("cdc_parse_error", value=cdc_dt_str, error=str(e))

        # Update payment record
        payment.acknowledgement_id = commit_res.get("acknowledgement_id")
        payment.cdc_transaction_datetime = cdc_local
        payment.cdc_transaction_datetime_utc = cdc_utc
        payment.status = "committed"
        db.commit()
        db.refresh(payment)

        logger.bind(**ctx).info("payment_marked_committed", ack_id=payment.acknowledgement_id)

        # Record transaction
        debited_amount = _to_decimal(payment.total_amount).quantize(Decimal("0.01"))
        tx = Transaction(
            user_id=user_id,
            account_id=account.id,
            payment_id=payment.id,
            reference_number=payment.reference_number,
            amount=float(debited_amount),
            currency=payment.currency or account.currency or "USD",
            direction="debit",
            description=f"Payment to {payment.service.name if payment.service else ''}",
            created_at=datetime.utcnow(),
        )
        db.add(tx)

        account.balance = (Decimal(account.balance or 0).quantize(Decimal("0.01")) - debited_amount)
        db.commit()
        db.refresh(tx)

        # Store transaction id
        tx.transaction_id = commit_tid

        db.add(tx)
        db.commit()
        db.refresh(tx)

        logger.bind(transaction_db_id=tx.id, transaction_id=tx.transaction_id, osp_transaction_id=osp_tid, **ctx)\
              .info("transaction_recorded")

        # -----------------------------
        # OSP CONFIRM (must use osp_tid)
        # -----------------------------
        confirm_tid = osp_tid or tx.transaction_id

        confirm_res = await osp_confirm(payment.reference_number, confirm_tid, payment.acknowledgement_id)
        log_osp_response(ctx, "confirm", confirm_res)
        logger.bind(**ctx).debug(
            "osp_confirm",
            response_code=confirm_res.get("response_code"),
            confirm_tid=confirm_tid
        )

        if confirm_res.get("response_code") != 200:
            logger.bind(**ctx).error("osp_confirm_failed", osp_response=confirm_res)
            raise HTTPException(status_code=400, detail="OSP confirm failed")

        # Mark payment confirmed
        mark_confirmed(payment, db)
        local_cdc_time = to_local_time(payment.cdc_transaction_datetime)

        elapsed = (datetime.utcnow() - start_ts).total_seconds()

        fields = dict(ctx)
        fields["payment_id"] = payment.id
        fields["transaction_id"] = tx.transaction_id

        logger.bind(**fields).info("confirm_payment completed", elapsed_s=elapsed)

        return PaymentConfirmOut(
            status=payment.status,
            transaction_id=tx.transaction_id or str(tx.id),
            account_id=account.id,
            reference_number=payment.reference_number,
            customer_name=payment.customer_name,
            invoice_amount=float(_to_decimal(payment.amount).quantize(Decimal("0.01"))),
            invoice_currency=payment.invoice_currency,
            amount=float(debited_amount),
            amount_debited=float(debited_amount),
            fee=float(_to_decimal(payment.fee).quantize(Decimal("0.01"))),
            total_amount=float(debited_amount),
            currency=(payment.currency or payment.invoice_currency),
            new_balance=float(account.balance),
            cdc_transaction_datetime=payment.cdc_transaction_datetime.strftime("%Y-%m-%d %H:%M:%S") if payment.cdc_transaction_datetime else None,
            cdc_transaction_datetime_utc=payment.cdc_transaction_datetime_utc.strftime("%Y-%m-%d %H:%M:%S") if payment.cdc_transaction_datetime_utc else None,
            cdc_transaction_datetime_local=local_cdc_time,
            service={
                "id": payment.service.id if payment.service else None,
                "name": payment.service.name if payment.service else None,
                "logo_url": payment.service.logo_url if payment.service else None,
            },
        )

    except HTTPException as e:
        db.rollback()
        try:
            p = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
            if p:
                p.status = "failed"
                db.commit()
        except Exception:
            db.rollback()
        logger.bind(**ctx).warning("confirm_payment_http_exception", detail=str(e.detail))
        raise e

    except Exception as e:
        db.rollback()
        try:
            p = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
            if p:
                p.status = "failed"
                db.commit()
        except Exception:
            db.rollback()
        logger.bind(**ctx).exception("confirm_payment_unexpected_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Confirm failed: {e}")


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
        log_osp_response({"user_id": user_id, "payment_id": payment_id}, "reverse", res)
        logger.info(f"[OSP Reverse Response] {res}")

        payment.status = "reversed"
        db.commit()
        return {"status": payment.status, "osp_response": res}

    except Exception as e:
        db.rollback()
        logger.exception(f"Reverse failed: {e}")
        payment = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
        if payment: payment.status = "failed"; db.commit()
        raise HTTPException(status_code=500, detail=str(e))
