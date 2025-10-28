from fastapi import HTTPException
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from models import Account, Payment, Transaction, User

def ensure_sufficient_balance(account: Account, amount_cents: int):
    if account.balance_cents < amount_cents:
        raise HTTPException(status_code=402, detail="Insufficient funds") 