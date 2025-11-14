# backend/schemas/service.py
from typing import Optional
from pydantic import BaseModel

class ServiceSchema(BaseModel):
    id: Optional[int] = None
    name: str
    code: str
    logo_url: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True
