from fastapi import Header, HTTPException, Depends
from db.session import SessionLocal
from core.security import decode_token

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_id(authorization: str = Header(...)):
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split()[1]
    return decode_token(token)