# backend/schemas/service.py
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class ServiceSchema(BaseModel):
    id: Optional[int] = None
    name: str
    code: str
    description: Optional[str] = None
    logo_url: Optional[str] = None


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    description: Optional[str] = None
    logo_url: Optional[str] = None


class ServiceListResponse(BaseModel):
    items: List[ServiceOut]
    total: int
    page: int
    page_size: int


class ServiceCreateResponse(BaseModel):
    message: str
    service: ServiceOut


class ServiceUpdateResponse(BaseModel):
    message: str
    service: ServiceOut


class ServiceDeleteResponse(BaseModel):
    message: str


class UploadLogoOut(BaseModel):
    logo_url: str
