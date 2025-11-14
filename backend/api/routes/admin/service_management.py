# backend/api/routes/admin/service_management.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from core.permissions import require_admin
from models.service import Service
from schemas.service import ServiceSchema

router = APIRouter(
    prefix="/adm/services",
    tags=["Admin: Service Management"],
    dependencies=[Depends(require_admin)],
)


@router.get("/")
def get_services(db: Session = Depends(get_db)):
    """
    Return all services for admin management.
    Frontend expects a plain list of objects: [{ id, name, code, logo_url, ... }]
    """
    return db.query(Service).order_by(Service.id.asc()).all()


@router.get("/{service_id}")
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/")
def add_service(data: dict, db: Session = Depends(get_db)):
    """
    Create a new service.

    Your frontend sends:
      { name, code, logo_url }
    so we accept a generic dict instead of ServiceSchema (which requires id).
    """
    # Minimal validation
    name = data.get("name")
    code = data.get("code")
    if not name or not code:
        raise HTTPException(status_code=400, detail="name and code are required")

    service = Service(
        name=name,
        code=code,
        logo_url=data.get("logo_url"),
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return {"message": "Service added successfully", "service": service}


@router.put("/{service_id}")
def update_service(service_id: int, data: dict, db: Session = Depends(get_db)):
    """
    Update a service.

    Frontend sends the whole object from edit page:
      { id, name, code, logo_url, ... }
    We just patch allowed fields.
    """
    service = db.query(Service).get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Only update known fields
    for field in ["name", "code", "logo_url"]:
        if field in data and data[field] is not None:
            setattr(service, field, data[field])

    db.commit()
    db.refresh(service)
    return {"message": "Service updated successfully", "service": service}


@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    db.delete(service)
    db.commit()
    return {"message": "Service deleted successfully"}
