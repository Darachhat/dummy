from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base
import enum

class Currency(str, enum.Enum):
    USD = "USD"
    KHR = "KHR"

class TxDirection(str, enum.Enum):
    debit = "debit"
    credit = "credit"

class PaymentStatus(str, enum.Enum):
    lookup = "lookup"
    started = "started"
    confirmed = "confirmed"
    reversed = "reversed"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    pin_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    number = Column(String, unique=True, nullable=False)
    balance_cents = Column(Integer, default=0)
    currency = Column(String, default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payment"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    reference_number = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="lookup")
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    service = relationship("Service", back_populates="payments")
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    reference_number = Column(String, index=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="USD")
    direction = Column(String, default="debit")
    description = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    logo_url = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    payments = relationship("Payment", back_populates="service")