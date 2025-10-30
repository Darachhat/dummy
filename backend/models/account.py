from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from db.base import Base


class Account(Base):
    __tablename__ = "accounts"


    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    number = Column(String, unique=True, nullable=False)
    balance_cents = Column(Integer, default=0)
    currency = Column(String, default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)