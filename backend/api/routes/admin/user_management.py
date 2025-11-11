# backend/api/routes/admin/user_management.py
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session, joinedload, aliased
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from core.security import hash_password
from core.permissions import require_admin
from db.session import SessionLocal

# Models
from models.user import User
from models.account import Account
from models.transaction import Transaction
from models.payment import Payment
from models.service import Service

# Schemas (keep these as-is in your codebase)
from schemas.user import UserCreate, UserOut, UserUpdate as UserUpdateSchema
from schemas.account import AccountOut
from schemas.transaction import TransactionOut
from schemas.payment import PaymentConfirmOut

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin: User Management"],
    dependencies=[Depends(require_admin)],
)


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
    """Paginated list of users for admin UI."""
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
    query = query.order_by(sort_column.asc() if dir == "asc" else sort_column.desc())

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
    """
    Return user basic info and optionally accounts, transactions and payments.
    Note: response is a dict (not UserOut) to include nested lists.
    """
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
                # some models use `number` or `account_number` — adapt to your model
                "account_number": getattr(a, "number", getattr(a, "account_number", None)),
                "balance": float(a.balance) if a.balance is not None else 0.0,
                "currency": a.currency,
                "status": getattr(a, "status", "active"),
            }
            for a in accounts
        ]

    # transactions (paginated)
    if "transactions" in includes:
        offset = (page - 1) * limit
        # use joinedload for eager loading of payment->service for efficiency
        tx_q = (
            db.query(Transaction)
            .options(joinedload(Transaction.payment).joinedload(Payment.service))
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
        )
        total_tx = tx_q.count()
        txs = tx_q.offset(offset).limit(limit).all()

        result["transactions"] = {
            "page": page,
            "limit": limit,
            "total": total_tx,
            "items": [
                {
                    "id": t.id,
                    "reference_number": getattr(t, "reference_number", None),
                    "amount": float(t.amount) if t.amount is not None else 0.0,
                    "currency": t.currency,
                    "direction": t.direction,
                    "description": t.description or "",
                    "service_name": (t.payment.service.name if t.payment and t.payment.service else None),
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in txs
            ],
        }

    # payments (paginated)
    if "payments" in includes:
        offset = (page - 1) * limit
        pay_q = (
            db.query(Payment)
            .options(joinedload(Payment.service))
            .filter(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
        )
        total_pay = pay_q.count()
        pays = pay_q.offset(offset).limit(limit).all()

        result["payments"] = {
            "page": page,
            "limit": limit,
            "total": total_pay,
            "items": [
                {
                    "id": p.id,
                    "reference_number": p.reference_number,
                    "amount": float(p.amount) if p.amount is not None else 0.0,
                    "currency": p.currency,
                    "status": p.status,
                    "service_name": p.service.name if p.service else None,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
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
    """
    Update user fields. Accepts JSON body with any of:
    { "name": "...", "phone": "...", "role": "...", "password": "...", "pin": "..." }
    """
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
    return db.query(Account).filter(Account.user_id == user_id).all()


@router.put("/{user_id}/accounts/{account_id}")
def update_account_balance(
    user_id: int,
    account_id: int,
    balance: Decimal = Body(...),
    db: Session = Depends(get_db),
):
    """Admin: Update user's account balance."""
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == user_id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.balance = balance
    db.commit()
    db.refresh(account)
    return {
        "id": account.id,
        "user_id": account.user_id,
        "balance": float(account.balance),
        "currency": account.currency,
        "message": "Balance updated successfully",
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
    """
    Get user's transactions. Returns TransactionOut list.
    When filtering by service_name we join Payment->Service safely via aliases.
    """
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

    # if service_name filter requested, safely join payment and service using aliased Payment
    if service_name:
        pay_alias = aliased(Payment)
        q = q.join(pay_alias, pay_alias.id == Transaction.payment_id).join(Service, Service.id == pay_alias.service_id)
        q = q.filter(Service.name.ilike(f"%{service_name}%"))

    txs = q.order_by(Transaction.created_at.desc()).limit(limit).all()

    results = []
    for t in txs:
        p = getattr(t, "payment", None)
        s = p.service if p and getattr(p, "service", None) else None
        results.append(
            TransactionOut(
                id=t.id,
                transaction_id=t.id,
                reference_number=getattr(p, "reference_number", None) if p else getattr(t, "reference_number", None),
                description=t.description or "",
                amount=(p.amount if p and p.amount is not None else t.amount),
                fee=(p.fee if p and p.fee is not None else Decimal("0.00")),
                total_amount=(p.total_amount if p and p.total_amount is not None else (t.amount or Decimal("0.00"))),
                customer_name=(p.customer_name if p else None),
                service_name=(s.name if s else None),
                service_logo_url=(s.logo_url if s else None),
                direction=t.direction,
                currency=t.currency,
                created_at=(t.created_at.isoformat() if t.created_at else None),
            )
        )
    return results


# --- Payments (with filters) ---
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
    q = db.query(Payment).options(joinedload(Payment.service)).filter(Payment.user_id == user_id)

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
        # safe join for filter (aliased optional)
        pay_alias = aliased(Payment)
        # join service via payment alias
        q = q.join(Service, Service.id == Payment.service_id).filter(Service.name.ilike(f"%{service_name}%"))
    if status:
        q = q.filter(Payment.status.ilike(status))

    payments = q.order_by(Payment.created_at.desc()).limit(limit).all()

    results = []
    for p in payments:
        results.append(
            PaymentConfirmOut(
                status=p.status,
                transaction_id=(p.transaction.id if getattr(p, "transaction", None) else 0),
                account_id=p.account_id,
                new_balance=Decimal("0.00"),
                reference_number=p.reference_number,
                customer_name=p.customer_name,
                amount=p.amount,
                fee=p.fee,
                total_amount=p.total_amount,
                currency=p.currency,
                service={
                    "id": p.service.id if p.service else None,
                    "name": p.service.name if p.service else None,
                    "logo_url": p.service.logo_url if p.service else None,
                },
                cdc_transaction_datetime=p.cdc_transaction_datetime,
            )
        )
    return results
