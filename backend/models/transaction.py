from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from db.base import Base


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