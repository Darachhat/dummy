from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from api.deps import get_db, get_user_id
from models import User, Account
from schemas.account import AccountOut
from decimal import Decimal

router = APIRouter(tags=["accounts"])


@router.get("/me")
def me(user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    accounts = db.query(Account).filter_by(user_id=user_id).all()
    total = sum(a.balance for a in accounts)  

    return {
        "user": {"id": user.id, "phone": user.phone},
        "total_balance": float(total), 
        "accounts": [AccountOut.model_validate(a).model_dump() for a in accounts],
    }


@router.get("/accounts/{account_id}")
def account_detail(account_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    a = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountOut.model_validate(a)
