# backend/api/routes/admin/service_management.py

from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    Body,
)
from sqlalchemy.orm import Session

from api.deps import get_db
from core.permissions import require_admin
from models.service import Service
from schemas.service import (
    ServiceSchema,
    ServiceOut,
    ServiceListResponse,
    ServiceCreateResponse,
    ServiceUpdateResponse,
    ServiceDeleteResponse,
    UploadLogoOut,
)

router = APIRouter(
    prefix="/adm/services",
    tags=["Admin: Service Management"],
    dependencies=[Depends(require_admin)],
)

# Where logos are stored (FastAPI should already be serving /static)
STATIC_LOGO_DIR = Path("static/logos")
STATIC_LOGO_DIR.mkdir(parents=True, exist_ok=True)


# ---------- Helpers ----------

def _ensure_unique_code(db: Session, code: str, exclude_id: Optional[int] = None) -> None:
    """Raise 400 if a service with the same code already exists."""
    q = db.query(Service).filter(Service.code == code)
    if exclude_id is not None:
        q = q.filter(Service.id != exclude_id)
    if q.first():
        raise HTTPException(status_code=400, detail="Service code already exists")


# ---------- Routes ----------

@router.get("/", response_model=ServiceListResponse)
def list_services(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description="Search by name or code"),
    sort: str = Query("id"),
    dir: str = Query("asc"),
):
    query = db.query(Service)

    # Search
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Service.name.ilike(like)) |
            (Service.code.ilike(like))
        )

    # Sort
    sort_map = {
        "id": Service.id,
        "name": Service.name,
        "code": Service.code,
        "created_at": getattr(Service, "created_at", Service.id),  # if present
    }
    sort_col = sort_map.get(sort, Service.id)
    if dir.lower() == "desc":
        sort_col = sort_col.desc()
    else:
        sort_col = sort_col.asc()

    query = query.order_by(sort_col)

    total = query.count()
    services = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ServiceListResponse(
        items=services,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """Get a single service for the edit page."""
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/upload-logo", response_model=UploadLogoOut)
async def upload_logo(file: UploadFile = File(...)):
    allowed_ext = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in allowed_ext:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    from uuid import uuid4
    fname = f"{uuid4().hex}{ext}"
    dest = STATIC_LOGO_DIR / fname

    data = await file.read()
    dest.write_bytes(data)

    logo_url = f"/static/logos/{fname}"
    return UploadLogoOut(logo_url=logo_url)


@router.post("/", response_model=ServiceCreateResponse)
def add_service(data: ServiceSchema, db: Session = Depends(get_db)):
    """Create a new service (admin only)."""
    _ensure_unique_code(db, data.code)

    service = Service(**data.model_dump(exclude={"id"}))
    db.add(service)
    db.commit()
    db.refresh(service)

    return ServiceCreateResponse(
        message="Service added successfully",
        service=service,
    )


@router.put("/{service_id}", response_model=ServiceUpdateResponse)
def update_service(
    service_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    """Update an existing service (admin only)."""

    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    name = (payload.get("name") or "").strip()
    code = (payload.get("code") or "").strip()
    description = payload.get("description")
    logo_url = payload.get("logo_url")

    if not name or not code:
        raise HTTPException(
            status_code=400,
            detail="Name and code are required",
        )

    # enforce unique code if changed
    if code != service.code:
        _ensure_unique_code(db, code, exclude_id=service_id)

    service.name = name
    service.code = code
    service.description = description
    if logo_url is not None:
        service.logo_url = logo_url

    db.commit()
    db.refresh(service)

    return ServiceUpdateResponse(
        message="Service updated successfully",
        service=service,
    )


@router.delete("/{service_id}", response_model=ServiceDeleteResponse)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    """Delete a service (admin only)."""
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    db.delete(service)
    db.commit()
    return ServiceDeleteResponse(message="Service deleted successfully")
