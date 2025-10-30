from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base


class Payment(Base):
    __tablename__ = "payment"


    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    reference_number = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    customer_name = Column(String, nullable=True)
    amount_cents = Column(Integer, nullable=False)
    fee_cents = Column(Integer, default=0)
    total_amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="USD")
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    status = Column(String, default="lookup")
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)


    service = relationship("Service", back_populates="payments")
    created_at = Column(DateTime, default=datetime.utcnow)