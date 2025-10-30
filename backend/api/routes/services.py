from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.deps import get_db
from models.service import Service


router = APIRouter(prefix="/services", tags=["services"])


@router.get("")
def list_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    return [
        {"id": s.id, "name": s.name, "code": s.code, "logo_url": s.logo_url, "description": s.description}
        for s in services
    ]