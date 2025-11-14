# backend/core/security.py
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from core.config import settings

ALGO = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def _build_payload(sub: int) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "sub": str(sub), 
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }


def create_token(sub: int) -> str:
    payload = _build_payload(sub)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGO)


def create_token_specific(sub: int) -> str:
    # kept for compatibility – same behavior, but separated if you later want different claims
    payload = _build_payload(sub)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGO)


def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGO])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return int(sub)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
