# backend/api/routes/admin/accounts.py
from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Optional
from db.session import SessionLocal
from core.permissions import require_admin
from models.account import Account
from models.transaction import Transaction
from models.payment import Payment
from os import getenv

try:
    _raw = getenv("USD_TO_KHR_RATE", None)
    USD_TO_KHR_RATE = Decimal(str(_raw)) if _raw is not None else Decimal("4000")
except Exception:
    USD_TO_KHR_RATE = Decimal("4000")

def get_khr_per_usd() -> Decimal:
    try:
        return USD_TO_KHR_RATE
    except Exception:
        return Decimal("4000")

accounts_router = APIRouter(prefix="/admin/accounts", tags=["Admin: Accounts"], dependencies=[Depends(require_admin)])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@accounts_router.get("/{account_id}")
def get_account(account_id: int = Path(...), db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return {
        "id": acc.id,
        "user_id": acc.user_id,
        "name": acc.name,
        "number": getattr(acc, "number", getattr(acc, "account_number", None)),
        "balance": float(acc.balance if acc.balance is not None else 0),
        "currency": (acc.currency or "USD").upper(),
        "status": getattr(acc, "status", "active"),
    }


@accounts_router.patch("/{account_id}")
def patch_account(
    account_id: int = Path(...),
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    if "name" in payload and payload["name"] is not None:
        acc.name = str(payload["name"]).strip()
    if "number" in payload and payload["number"] is not None:
        acc.number = str(payload["number"]).strip()

    if "balance" in payload:
        raw = payload.get("balance")
        try:
            raw_dec = Decimal(str(raw))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid balance value")

        input_currency = (payload.get("currency") or acc.currency or "USD").upper()
        if input_currency == "KHR":
            khr_per_usd = get_khr_per_usd()
            if not khr_per_usd or khr_per_usd == 0:
                raise HTTPException(status_code=500, detail="Exchange rate unavailable")
            balance_usd = (raw_dec / khr_per_usd).quantize(Decimal("0.01"))
            acc.balance = balance_usd
            acc.currency = "KHR"
        else:
            acc.balance = raw_dec.quantize(Decimal("0.01"))
            acc.currency = "USD"

    db.commit()
    db.refresh(acc)

    return {
        "id": acc.id,
        "user_id": acc.user_id,
        "name": acc.name,
        "number": acc.number,
        "balance": float(acc.balance if acc.balance is not None else 0),
        "currency": (acc.currency or "USD").upper(),
        "message": "Account updated",
    }


@accounts_router.delete("/{account_id}")
def delete_account(account_id: int = Path(...), db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    tx_count = db.query(Transaction).filter(Transaction.account_id == account_id).count()
    pay_count = db.query(Payment).filter(Payment.account_id == account_id).count()
    if tx_count or pay_count:
        raise HTTPException(status_code=400, detail=f"Cannot delete account with {tx_count} transactions and {pay_count} payments")

    db.delete(acc)
    db.commit()
    return {"message": "Account deleted", "id": account_id}
