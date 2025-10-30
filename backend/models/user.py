from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    pin_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)