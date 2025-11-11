#
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    pin_hash = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow)

    accounts = relationship("Account", back_populates="user")

    def __acl__(self):
        """Access Control List for RBAC"""
        return [
            ("Allow", f"user:{self.id}", "view_self"),
            ("Allow", "role:admin", "view_user"),
            ("Allow", "role:admin", "delete_user"),
            ("Allow", "role:admin", "create_user"),
            ("Allow", "role:admin", "update_user"),
        ]
