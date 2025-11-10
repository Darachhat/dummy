from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.user import User
from schemas.user import User as UserSchema
from core.permissions import Permission  # ✅ import the wrapper

router = APIRouter(prefix="/admin/users", tags=["Admin: User Management"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    _ = Depends(Permission("view_user", User)),  # ✅ works now
):
    return db.query(User).all()


@router.post("/")
def create_user(
    user_data: UserSchema,
    db: Session = Depends(get_db),
    _ = Depends(Permission("create_user", User)),
):
    existing = db.query(User).filter(User.phone == user_data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        name=user_data.name,
        phone=user_data.phone,
        password_hash=user_data.password_hash,
        pin_hash="N/A",
        role=user_data.role or "user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user": new_user}


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _ = Depends(Permission("delete_user", User)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.name} deleted successfully"}
