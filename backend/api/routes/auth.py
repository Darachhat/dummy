from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.security import create_token, verify_password
from db.session import SessionLocal
from models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginIn(BaseModel):
    phone: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenOut)
def login(body: LoginIn):
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(phone=body.phone).first()
        if not user or not verify_password(body.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return TokenOut(access_token=create_token(user.id))
    finally:
        db.close()