# backend/core/permissions.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_permissions import Authenticated, configure_permissions
from db.session import SessionLocal
from models.user import User
from core.security import decode_token
from api.deps import get_db

# Token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- Authentication: get current user ---
def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
    )
    try:
        user_id = decode_token(token)
    except HTTPException:

        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise credentials_exception
    return user

# --- Role-based check (admin only) ---
def require_admin(current_user: User = Depends(get_current_user)):
    """Allow only admin users."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user

# --- Permission System (for fine-grained control) ---
def get_user_principals(user: User):
    """Return permission principals based on the user."""
    principals = [Authenticated]
    if user:
        principals.append(f"user:{user.id}")
        principals.append(f"role:{user.role}")
    return principals

permission_factory = configure_permissions(get_user_principals)

def Permission(permission_name: str, model):
    """Permission dependency for routes."""
    def dependency(user: User = Depends(get_current_user)):
        checker = permission_factory(permission_name, model)
        return checker(user)
    return dependency
