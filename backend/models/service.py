from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base


class Service(Base):
    __tablename__ = "services"


    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    logo_url = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)


    payments = relationship("Payment", back_populates="service")