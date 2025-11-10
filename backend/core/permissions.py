from fastapi_permissions import Allow, Authenticated, configure_permissions
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from db.session import SessionLocal
from models.user import User
from core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    """Decode JWT token and return current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise credentials_exception
    return user

def get_user_principals(user: User):
    """Return permission principals based on the user."""
    principals = [Authenticated]
    if user:
        principals.append(f"user:{user.id}")
        principals.append(f"role:{user.role}")
    return principals

# Base permission factory
_permission_factory = configure_permissions(get_user_principals)

# ✅ Wrapper function that returns a callable for FastAPI Depends
def Permission(perm: str, model):
    def dependency(user: User = Depends(get_current_user)):
        return _permission_factory(perm, model)(user)
    return dependency
