#backend\models\payment.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from datetime import datetime
from sqlalchemy.orm import relationship
from db.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    reference_number = Column(String, nullable=False)
    customer_name = Column(String)
    amount = Column(Numeric(12, 2), nullable=False)
    fee = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String, default="USD")

    session_id = Column(String, nullable=True)
    acknowledgement_id = Column(String, nullable=True)
    cdc_transaction_datetime = Column(DateTime, nullable=True)
    cdc_transaction_datetime_utc = Column(DateTime, nullable=True) 
    reversal_transaction_id = Column(String, nullable=True)
    reversal_acknowledgement_id = Column(String, nullable=True)
    status = Column(String, default="started")
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)

    account = relationship("Account", back_populates="payments")
    service = relationship("Service", back_populates="payments")
    transaction = relationship("Transaction", back_populates="payment", uselist=False)
