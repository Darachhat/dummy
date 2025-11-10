from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.service import Service
from schemas.service import ServiceSchema

router = APIRouter(prefix="/admin/services", tags=["Admin: Service Management"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all services
@router.get("/")
def get_services(db: Session = Depends(get_db)):
    return db.query(Service).all()

# Add a new service
@router.post("/")
def add_service(data: ServiceSchema, db: Session = Depends(get_db)):
    service = Service(**data.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return {"message": "Service added successfully", "service": service}

# Update service
@router.put("/{service_id}")
def update_service(service_id: int, data: ServiceSchema, db: Session = Depends(get_db)):
    service = db.query(Service).get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    for key, value in data.model_dump().items():
        setattr(service, key, value)
    db.commit()
    return {"message": "Service updated successfully", "service": service}

# Delete service
@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()
    return {"message": "Service deleted successfully"}
