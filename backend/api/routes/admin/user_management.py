# backend/api/routes/admin/user_management.py
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from sqlalchemy.orm import Session, joinedload, aliased
from typing import List, Optional
from decimal import Decimal, InvalidOperation
from datetime import datetime

from core.security import hash_password
from core.permissions import require_admin
from db.session import SessionLocal

# helper
from os import getenv

# Models
from models.user import User
from models.account import Account
from models.transaction import Transaction
from models.payment import Payment
from models.service import Service

# Schemas (keep these as-is in your codebase)
from schemas.user import UserCreate, UserOut, UserUpdate as UserUpdateSchema
from schemas.account import AccountOut, AccountCreate
from schemas.transaction import TransactionOut
from schemas.payment import PaymentConfirmOut

router = APIRouter(
    prefix="/adm/users",
    tags=["Admin: User Management"],
    dependencies=[Depends(require_admin)],
)

SUPPORTED_CURRENCIES = ["USD", "KHR"]
try:
    USD_TO_KHR_RATE = Decimal(getenv("USD_TO_KHR_RATE"))
except (InvalidOperation, TypeError):
    USD_TO_KHR_RATE = Decimal("4000")


def get_khr_per_usd() -> Decimal:
    try:
        if USD_TO_KHR_RATE is None:
            return Decimal("4000")
        return Decimal(USD_TO_KHR_RATE)
    except (InvalidOperation, TypeError):
        return Decimal("4000")


# --- Database session dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- List users with pagination and simple search ---
@router.get("/", response_model=dict)
def list_users(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    q: Optional[str] = None,
    sort: Optional[str] = "created_at",
    dir: Optional[str] = "desc",
):
    query = db.query(User)

    # --- Search ---
    if q:
        query = query.filter(
            (User.name.ilike(f"%{q}%")) | (User.phone.ilike(f"%{q}%"))
        )

    # --- Sort ---
    valid_sort_fields = {
        "id": User.id,
        "name": User.name,
        "phone": User.phone,
        "role": User.role,
        "created_at": User.created_at,
    }
    sort_column = valid_sort_fields.get(sort, User.created_at)
    query = query.order_by(sort_column.asc())

    # --- Pagination ---
    total = query.count()
    offset = (page - 1) * page_size
    users = query.offset(offset).limit(page_size).all()

    # --- Return consistent structure ---
    return {
        "items": [
            {
                "id": u.id,
                "name": u.name,
                "phone": u.phone,
                "role": u.role,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# --- Get user detail (with optional relations) ---
@router.get("/{user_id}")
def get_user(
    user_id: int,
    include: Optional[str] = Query(None, description="Comma-separated: accounts,transactions,payments"),
    limit: int = Query(10, ge=1),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    includes = (include or "accounts,transactions,payments").split(",")
    result = {
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }

    # accounts
    if "accounts" in includes:
        accounts = db.query(Account).filter(Account.user_id == user_id).all()
        result["accounts"] = [
            {
                "id": a.id,
                "account_number": getattr(a, "number", getattr(a, "account_number", None)),
                "balance": float(a.balance) if a.balance is not None else 0.0,
                "currency": a.currency,
                "status": getattr(a, "status", "active"),
            }
            for a in accounts
        ]

    if "transactions" in includes:
        offset = (page - 1) * limit
        tx_q = (
            db.query(Transaction)
            .options(joinedload(Transaction.payment).joinedload(Payment.service))
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
        )
        total_tx = tx_q.count()
        txs = tx_q.offset(offset).limit(limit).all()

        # When a transaction is tied to a payment, prefer the payment's invoice_amount + invoice_currency for display
        result["transactions"] = {
            "page": page,
            "limit": limit,
            "total": total_tx,
            "items": [
                {
                    "id": t.id,
                    "reference_number": getattr(t, "reference_number", None),
                    # Prefer payment.invoice_amount (original invoice) when present, otherwise transaction amount
                    "amount": float(
                        (t.payment.invoice_amount if getattr(t, "payment", None) and getattr(t.payment, "invoice_amount", None) is not None
                         else (t.amount if t.amount is not None else 0.0))
                    ),
                    # currency: prefer payment.invoice_currency, then payment.currency, then transaction currency, fallback USD
                    "currency": (
                        (t.payment.invoice_currency if getattr(t, "payment", None) and getattr(t.payment, "invoice_currency", None) else None)
                        or (t.payment.currency if getattr(t, "payment", None) and getattr(t.payment, "currency", None) else None)
                        or (t.currency if getattr(t, "currency", None) else "USD")
                    ),
                    "direction": t.direction,
                    "description": t.description or "",
                    "service_name": (t.payment.service.name if t.payment and t.payment.service else None),
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    # expose raw payment object so UI can decide if anything else needed
                    "original_payment": {
                        "id": getattr(t.payment, "id", None),
                        "amount": float(t.payment.amount) if getattr(t, "payment", None) and getattr(t.payment, "amount", None) is not None else None,
                        "total_amount": float(t.payment.total_amount) if getattr(t, "payment", None) and getattr(t.payment, "total_amount", None) is not None else None,
                        "currency": getattr(t.payment, "currency", None),
                        "invoice_amount": float(t.payment.invoice_amount) if getattr(t, "payment", None) and getattr(t.payment, "invoice_amount", None) is not None else None,
                        "invoice_currency": getattr(t.payment, "invoice_currency", None) if getattr(t, "payment", None) else None,
                        "status": getattr(t.payment, "status", None),
                    },
                }
                for t in txs
            ],
        }

    # payments (paginated)
    if "payments" in includes:
        offset = (page - 1) * limit
        pay_q = (
            db.query(Payment)
            .options(joinedload(Payment.service), joinedload(Payment.transaction))
            .filter(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
        )
        total_pay = pay_q.count()
        pays = pay_q.offset(offset).limit(limit).all()

        # Build items with clear invoice_amount/invoice_currency fields and a display pair (amount + currency)
        result["payments"] = {
            "page": page,
            "limit": limit,
            "total": total_pay,
            "items": [
                {
                    "id": p.id,
                    "reference_number": p.reference_number,
                    # explicit invoice fields (original invoice that user was billed)
                    "invoice_amount": float(p.invoice_amount) if getattr(p, "invoice_amount", None) is not None else None,
                    "invoice_currency": (p.invoice_currency if getattr(p, "invoice_currency", None) else None),
                    # amount: prefer invoice_amount when present; otherwise fall back to stored amount or total_amount
                    "amount": float(p.invoice_amount) if getattr(p, "invoice_amount", None) is not None
                              else (float(p.amount) if getattr(p, "amount", None) is not None else (float(p.total_amount) if getattr(p, "total_amount", None) is not None else 0.0)),
                    "fee": float(p.fee) if p.fee is not None else 0.0,
                    "total_amount": float(p.total_amount) if p.total_amount is not None else None,
                    # currency: prefer invoice_currency (belongs to invoice), else payment.currency
                    "currency": (p.invoice_currency or p.currency or "USD"),
                    "status": p.status,
                    "service_name": p.service.name if p.service else None,
                    "transaction_id": getattr(p.transaction, "transaction_id", None),
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    # include raw/original representation for frontend debugging
                    "original_payment": {
                        "id": p.id,
                        "reference_number": p.reference_number,
                        "customer_name": p.customer_name,
                        "amount": float(p.amount) if p.amount is not None else None,
                        "fee": float(p.fee) if p.fee is not None else None,
                        "total_amount": float(p.total_amount) if p.total_amount is not None else None,
                        "currency": p.currency,
                        "invoice_currency": p.invoice_currency,
                        "invoice_amount": float(p.invoice_amount) if getattr(p, "invoice_amount", None) is not None else None,
                        "session_id": p.session_id,
                        "acknowledgement_id": p.acknowledgement_id,
                        "cdc_transaction_datetime": p.cdc_transaction_datetime,
                        "cdc_transaction_datetime_utc": p.cdc_transaction_datetime_utc,
                        "status": p.status,
                    },
                }
                for p in pays
            ],
        }

    return result


# --- Create user ---
@router.post("/", response_model=UserOut)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == user_data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this phone number already exists")

    new_user = User(
        name=user_data.name,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        pin_hash=hash_password("1234"),
        role=user_data.role or "user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# --- Update user info / password / PIN ---
@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # update allowed fields
    if "name" in payload and payload["name"]:
        user.name = payload["name"]
    if "phone" in payload and payload["phone"]:
        user.phone = payload["phone"]
    if "role" in payload and payload["role"]:
        user.role = payload["role"]
    if "password" in payload and payload["password"]:
        user.password_hash = hash_password(payload["password"])
    if "pin" in payload and payload["pin"]:
        user.pin_hash = hash_password(payload["pin"])

    db.commit()
    db.refresh(user)
    return user


# --- Delete user ---
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# --- Accounts ---
@router.get("/{user_id}/accounts", response_model=List[AccountOut])
def get_user_accounts(user_id: int, db: Session = Depends(get_db)):
    accounts_db = db.query(Account).filter(Account.user_id == user_id).all()

    out = []
    for a in accounts_db:
        # return stored balance and currency directly
        stored_amount = Decimal(a.balance or 0).quantize(Decimal("0.01"))
        stored_currency = (a.currency or "USD").upper()

        out.append({
            "id": a.id,
            "name": getattr(a, "name", None),
            "number": getattr(a, "number", getattr(a, "account_number", None)),
            "balance": float(stored_amount),
            "currency": stored_currency,
            "status": getattr(a, "status", "active"),
        })
    return out


@router.put("/{user_id}/accounts/{account_id}")
def update_account_balance(
    user_id: int,
    account_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        raw_balance = Decimal(payload.get("balance", 0))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid balance")

    input_currency = (payload.get("currency") or account.currency or "USD").upper()

    if input_currency == "KHR":
        khr_per_usd = get_khr_per_usd()
        if khr_per_usd == 0:
            raise HTTPException(status_code=500, detail="Exchange rate unavailable")
        balance_usd = (raw_balance / khr_per_usd).quantize(Decimal("0.01"))
    else:
        balance_usd = raw_balance.quantize(Decimal("0.01"))

    account.balance = balance_usd
    db.commit()
    db.refresh(account)
    return {
        "id": account.id,
        "user_id": account.user_id,
        "balance": float(account.balance),
        "currency": account.currency,
        "message": "Balance updated successfully",
    }


# --- Create account (conversion-aware) ---
@router.post("/{user_id}/accounts", response_model=AccountOut)
def create_user_account(
    user_id: int,
    data: AccountCreate,
    db: Session = Depends(get_db),
):
    # ensure user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # unique number check
    exists = db.query(Account).filter(Account.number == data.number).first()
    if exists:
        raise HTTPException(status_code=400, detail="Account number already exists")

    incoming_currency = (data.currency or "USD").upper()
    if incoming_currency not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=400, detail="Unsupported currency")

    try:
        input_balance = Decimal(str(data.balance or 0))
    except Exception:
        input_balance = Decimal("0")

    # NEW: store input_balance as-is (quantize to 2 decimals), and set currency exactly as admin selected
    acc = Account(
        user_id=user.id,
        name=data.name,
        number=data.number,
        balance=input_balance.quantize(Decimal("0.01")),
        currency=incoming_currency,
    )
    db.add(acc)
    db.commit()
    db.refresh(acc)

    # Return the stored values so frontend/admin will display the same numbers
    return {
        "id": acc.id,
        "name": acc.name,
        "number": acc.number,
        "balance": float(acc.balance),
        "currency": acc.currency,
        "status": getattr(acc, "status", "active"),
    }


# --- Transactions (with filters) ---
@router.get("/{user_id}/transactions", response_model=List[TransactionOut])
def user_transactions(
    user_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(20, description="Max number of transactions to return"),
    start_date: Optional[str] = Query(None, description="Filter from this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to this date (YYYY-MM-DD)"),
    direction: Optional[str] = Query(None, description="Transaction direction: debit or credit"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
):
    # base query with eager load for payment->service
    q = (
        db.query(Transaction)
        .options(joinedload(Transaction.payment).joinedload(Payment.service))
        .filter(Transaction.user_id == user_id)
    )
    # filtering by dates
    if start_date:
        try:
            q = q.filter(Transaction.created_at >= datetime.fromisoformat(start_date))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format, use YYYY-MM-DD")
    if end_date:
        try:
            q = q.filter(Transaction.created_at <= datetime.fromisoformat(end_date))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format, use YYYY-MM-DD")
    if direction:
        q = q.filter(Transaction.direction.ilike(direction))
    if service_name:
        pay_alias = aliased(Payment)
        q = q.join(pay_alias, pay_alias.id == Transaction.payment_id).join(Service, Service.id == pay_alias.service_id)
        q = q.filter(Service.name.ilike(f"%{service_name}%"))

    txs = q.order_by(Transaction.created_at).limit(limit).all()

    results = []
    for t in txs:
        p = getattr(t, "payment", None)
        s = p.service if p and getattr(p, "service", None) else None

        # prefer invoice_amount/currency for display when available
        display_amount = (p.invoice_amount if p and getattr(p, "invoice_amount", None) is not None else (p.amount if p and getattr(p, "amount", None) is not None else t.amount))
        display_currency = (p.invoice_currency if p and getattr(p, "invoice_currency", None) else (p.currency if p and getattr(p, "currency", None) else (t.currency or "USD")))

        results.append(
            TransactionOut(
                id=t.id,
                transaction_id=t.transaction_id,
                reference_number=getattr(p, "reference_number", None) if p else getattr(t, "reference_number", None),
                description=t.description or "",
                amount=display_amount,
                fee=(p.fee if p and p.fee is not None else Decimal("0.00")),
                total_amount=(p.total_amount if p and p.total_amount is not None else (t.amount or Decimal("0.00"))),
                customer_name=(p.customer_name if p else None),
                service_name=(s.name if s else None),
                service_logo_url=(s.logo_url if s else None),
                direction=t.direction,
                currency=display_currency,
                created_at=(t.created_at.isoformat() if t.created_at else None),
            )
        )
    return results


# --- Payments ---
@router.get("/{user_id}/payments", response_model=List[PaymentConfirmOut])
def user_payments(
    user_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(20, description="Max number of payments to return"),
    start_date: Optional[str] = Query(None, description="Filter from this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to this date (YYYY-MM-DD)"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    status: Optional[str] = Query(None, description="Filter by payment status"),
):
    """Get user's recent payments (joined with service info)."""
    q = db.query(Payment).options(joinedload(Payment.service), joinedload(Payment.transaction)).filter(Payment.user_id == user_id)

    if start_date:
        try:
            q = q.filter(Payment.created_at >= datetime.fromisoformat(start_date))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format, use YYYY-MM-DD")
    if end_date:
        try:
            q = q.filter(Payment.created_at <= datetime.fromisoformat(end_date))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format, use YYYY-MM-DD")
    if service_name:
        pay_alias = aliased(Payment)
        q = q.join(Service, Service.id == Payment.service_id).filter(Service.name.ilike(f"%{service_name}%"))
    if status:
        q = q.filter(Payment.status.ilike(status))

    payments = q.order_by(Payment.created_at).limit(limit).all()

    results = []
    for p in payments:
        # determine display amount/currency: prefer invoice_amount/invoice_currency if available
        invoice_amount_present = getattr(p, "invoice_amount", None) is not None
        invoice_amt = Decimal(p.invoice_amount) if invoice_amount_present else None

        display_amount = invoice_amt if invoice_amount_present else (p.amount if getattr(p, "amount", None) is not None else p.total_amount)
        display_currency = (p.invoice_currency or p.currency or "USD")

        results.append(
            PaymentConfirmOut(
                status=p.status,
                transaction_id=getattr(p.transaction, "transaction_id", None),
                account_id=p.account_id,
                new_balance=Decimal("0.00"),
                reference_number=p.reference_number,
                customer_name=p.customer_name,
                # Keep numeric fields as-is (schemas should accept Decimal/float)
                amount=display_amount,
                fee=p.fee,
                total_amount=p.total_amount,
                # Explicit currency for frontend to use with the display amount
                currency=display_currency,
                service={
                    "id": p.service.id if p.service else None,
                    "name": p.service.name if p.service else None,
                    "logo_url": p.service.logo_url if p.service else None,
                },
                session_id=p.session_id,
                acknowledgement_id=p.acknowledgement_id,
                cdc_transaction_datetime=p.cdc_transaction_datetime,
                cdc_transaction_datetime_utc=p.cdc_transaction_datetime_utc,
                reversal_transaction_id=p.reversal_transaction_id,
                reversal_acknowledgement_id=p.reversal_acknowledgement_id,
                created_at=p.created_at,
                confirmed_at=(p.confirmed_at.isoformat() if p.confirmed_at else None),
            )
        )
    return results


@router.get("/meta/currencies", response_model=list[str])
def list_currencies():
    return SUPPORTED_CURRENCIES
