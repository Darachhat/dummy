from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_user_id
from models import User, Account
from schemas.account import AccountOut


router = APIRouter(tags=["accounts"])


@router.get("/me")
def me(user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    accounts = db.query(Account).filter_by(user_id=user_id).all()
    total = sum(a.balance_cents for a in accounts)
    return {
        "user": {"id": user.id, "phone": user.phone},
        "total_balance_cents": total,
        "accounts": [AccountOut.model_validate(a).model_dump() for a in accounts],
    }


@router.get("/accounts/{account_id}")
def account_detail(account_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    a = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    if not a:
        raise HTTPException(404, "Account not found")
    return AccountOut.model_validate(a)


@router.post("/accounts/transfer")
def transfer_funds(from_id: int, to_id: int, amount_cents: int, user_id: int = Depends(get_user_id), db: Session = Depends(get_db)):
    if from_id == to_id:
        raise HTTPException(400, "Cannot transfer to the same account")
    if amount_cents <= 0:
        raise HTTPException(400, "Amount must be positive")


    from_acc = db.query(Account).filter_by(id=from_id, user_id=user_id).first()
    to_acc = db.query(Account).filter_by(id=to_id, user_id=user_id).first()


    if not from_acc or not to_acc:
        raise HTTPException(404, "Account not found")
    if from_acc.balance_cents < amount_cents:
        raise HTTPException(400, "Insufficient balance")


    from_acc.balance_cents -= amount_cents
    to_acc.balance_cents += amount_cents
    db.commit()
    return {"status": "success", "from_balance": from_acc.balance_cents, "to_balance": to_acc.balance_cents}