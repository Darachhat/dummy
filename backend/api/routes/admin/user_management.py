from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from core.security import hash_password

from db.session import SessionLocal

from models.user import User
from models.account import Account
from models.transaction import Transaction
from models.payment import Payment
try:
    from models.service import Service 
except Exception:
    Service = None 

from schemas.user import UserCreate, UserOut
from core.permissions import require_admin

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin: User Management"],
    dependencies=[Depends(require_admin)] 
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Schemas ---
class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None

class AccountRowOut(BaseModel):
    id: int
    account_number: str
    balance: Decimal
    currency: str
    status: Optional[str] = "active"
    class Config:
        from_attributes = True

class TransactionRowOut(BaseModel):
    id: int
    type: Optional[str] = None
    amount: Decimal
    currency: str
    created_at: str
    class Config:
        from_attributes = True

class PaymentRowOut(BaseModel):
    id: int
    method: Optional[str] = None
    amount: Decimal
    currency: str
    created_at: str
    class Config:
        from_attributes = True

class AccountUpdate(BaseModel):
    balance: Decimal



# --- List/Create ---

@router.get("/", response_model=List[UserOut])
def get_user(db: Session = Depends(get_db)):
    """Return All Users."""
    return db.query(User).order_by(User.created_at.desc()).all()

@router.post("/", response_model=UserOut)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create new user (admin only)."""
    existing = db.query(User).filter(User.phone == user_data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

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

# --- Detail/Update/Delete ---

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, update_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if update_data.name:
        user.name = update_data.name
    if update_data.phone:
        user.phone = update_data.phone
    if update_data.role:
        user.role = update_data.role

    #reset password
    if update_data.password:
        user.password_hash = hash_password(update_data.password)

    #reset pin
    if hasattr(update_data, "pin") and update_data.pin:
        user.pin_hash = hash_password(update_data.pin)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# Get user account
@router.get("/{user_id}/accounts", response_model=List[AccountRowOut])
def get_user_accounts(user_id: int, db: Session = Depends(get_db)):
    rows = db.query(Account).filter(Account.user_id == user_id).all()
    return [
        AccountRowOut(
            id=r.id,
            account_number=r.number, 
            balance=r.balance,
            currency=r.currency,
            status="active",        
        )
        for r in rows
    ]

@router.put("/{user_id}/accounts/{account_id}", response_model=dict)
def update_account_balance(user_id: int, account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)):
    """Admin: Update a user's account balance."""
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.balance = payload.balance
    db.commit()
    db.refresh(account)

    return {
        "id": account.id,
        "user_id": account.user_id,
        "balance": float(account.balance),
        "currency": account.currency,
        "message": "Balance updated successfully"
    }


@router.get("/{user_id}/transactions", response_model=List[TransactionRowOut])
def user_transactions(user_id: int, limit: int = 20, db: Session = Depends(get_db)):
    rows = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        TransactionRowOut(
            id=r.id,
            # Your model has `description` and `direction` but not `type`
            # Use description if present, else fallback to direction
            type=(r.description or r.direction),
            amount=r.amount,
            currency=r.currency,
            created_at=(r.created_at.isoformat() if r.created_at else ""),
        )
        for r in rows
    ]


@router.get("/{user_id}/payments", response_model=List[PaymentRowOut])
def user_payments(user_id: int, limit: int = 20, db: Session = Depends(get_db)):
    q = (
        db.query(Payment)
        .filter(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .limit(limit)
    )
    # If Service relationship exists, eager-load so we can show method=service.name
    if Service:
        q = q.options(joinedload(Payment.service))

    rows = q.all()
    return [
        PaymentRowOut(
            id=r.id,
            method=(r.service.name if Service and r.service else None),
            amount=(r.total_amount or r.amount),
            currency=r.currency,
            created_at=(r.created_at.isoformat() if r.created_at else ""),
        )
        for r in rows
    ]


