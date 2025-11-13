# backend/api/routes/admin/payment_management.py

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session, joinedload
from typing import Dict, Any
from decimal import Decimal

from api.deps import get_db
from core.permissions import require_admin
from models.payment import Payment

router = APIRouter(prefix="/adm/payments", tags=["Admin - Payments"])


def serialize_payment(p: Payment) -> Dict[str, Any]:
    """
    Serialize Payment ORM object into stable, snake_case JSON keys
    suitable for the frontend. Converts Decimal -> float and datetimes -> ISO strings.
    """
    def g(attr, default=None):
        val = getattr(p, attr, default)
        # convert Decimal to float for JSON
        if isinstance(val, Decimal):
            return float(val)
        return val

    svc = getattr(p, "service", None)
    service_name = getattr(svc, "name", None) if svc else None
    service_code = getattr(svc, "code", None) if svc else getattr(p, "service_code", None)

    def date_to_iso(v):
        if v is None:
            return None
        try:
            if hasattr(v, "isoformat"):
                return v.isoformat()
        except Exception:
            pass
        return v

    return {
        "id": g("id"),
        "customer_name": g("customer_name"),

        "service_id": g("service_id"),
        "service_name": service_name,
        "service_code": service_code,

        "status": g("status"),

        "confirmed_at": date_to_iso(g("confirmed_at")),
        "created_at": date_to_iso(g("created_at")),

        "amount": float(g("amount")) if g("amount") is not None else None,
        "fee": float(g("fee")) if g("fee") is not None else None,
        "total_amount": float(g("total_amount")) if g("total_amount") is not None else None,

        "currency": g("currency"),
        "invoice_currency": g("invoice_currency"),

        "reference_number": g("reference_number"),

        "session_id": g("session_id"),
        "acknowledgement_id": g("acknowledgement_id"),

        "cdc_transaction_datetime": date_to_iso(g("cdc_transaction_datetime")),
        "cdc_transaction_datetime_utc": date_to_iso(g("cdc_transaction_datetime_utc")),

        "reversal_transaction_id": g("reversal_transaction_id"),
        "reversal_acknowledgement_id": g("reversal_acknowledgement_id"),

        "account_id": g("account_id"),
    }


@router.get("/", dependencies=[Depends(require_admin)])
def list_payments(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = 0
):
    q = db.query(Payment).options(joinedload(Payment.service))

    total = q.count()
    payments = q.order_by(Payment.created_at.asc()).offset(offset).limit(limit).all()

    results = [serialize_payment(p) for p in payments]

    return {
        "items": results,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{payment_id}", dependencies=[Depends(require_admin)])
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).options(joinedload(Payment.service)).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(404, "Payment not found")

    return serialize_payment(payment)


@router.put("/{payment_id}/status", dependencies=[Depends(require_admin)])
def update_status(payment_id: int, status: str = Body(...), db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(404, "Payment not found")

    valid_status = {"pending", "success", "failed", "canceled", "started", "confirmed"}
    if status not in valid_status:
        raise HTTPException(400, "Invalid status")

    payment.status = status
    db.commit()
    db.refresh(payment)

    payment = db.query(Payment).options(joinedload(Payment.service)).filter(Payment.id == payment_id).first()
    return {"message": "Updated", "payment": serialize_payment(payment)}


@router.delete("/{payment_id}", dependencies=[Depends(require_admin)])
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(404, "Payment not found")

    db.delete(payment)
    db.commit()

    return {"message": "Payment deleted"}
