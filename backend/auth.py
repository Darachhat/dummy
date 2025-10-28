import jwt
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from db import SessionLocal
from models import User
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

SECRET = "Keep_this_secret"
ALGO = "HS256"
ACCESS_MIN = 60 * 24

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginIn(BaseModel):
    phone: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

def create_token(sub: int):
    payload = {"sub": sub, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_MIN)}
    return jwt.encode(payload, SECRET, algorithm=ALGO)

@router.post("/login", response_model=TokenOut)
def login(body: LoginIn):
    db = SessionLocal()
    user = db.query(User).filter_by(phone=body.phone).first()
    if not user or not bcrypt.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenOut(access_token=create_token(user.id))
