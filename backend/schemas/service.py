from pydantic import BaseModel
from typing import Optional


class ServiceOut(BaseModel):
    id: int
    name: str
    code: str
    logo_url: Optional[str]
    description: Optional[str]


    class Config:
        from_attributes = True