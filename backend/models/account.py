#backend\models\account.py
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from db.base import Base
from decimal import Decimal

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    number = Column(String, unique=True, nullable=False, index=True)
    balance = Column(Numeric(12, 2), default=Decimal("0.00"))
    currency = Column(String, default="USD")

    user = relationship("User", back_populates="accounts")
    payments = relationship("Payment", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")
