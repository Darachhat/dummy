#backend/main.py
import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from decimal import Decimal
from alembic.script import ScriptDirectory

from core.config import settings
from core.logging import setup_logging
from loguru import logger
from core.security import hash_password
from db.base import Base
from db.session import engine, SessionLocal
from alembic.config import Config
from alembic import command

# Routers
from api.routes import auth as auth_routes
from api.routes import accounts as accounts_routes
from api.routes import payments as payments_routes
from api.routes import transactions as transactions_routes
from api.routes import services as services_routes
from api.routes.admin import user_management, service_management, transaction_management, payment_management
from api.routes.admin.accounts import accounts_router
from api.routes import debug 

# Models
from models.user import User
from models.account import Account
from models.service import Service
from models.transaction import Transaction
from models.payment import Payment
import os
import pathlib
import traceback



API_VERSION = settings.API_VERSION
TITLE = settings.API_TITLE
DESCRIPTION = settings.API_DESCRIPTION
CONTACT_NAME = settings.API_CONTACT_NAME
CONTACT_EMAIL = settings.API_CONTACT_EMAIL

setup_logging()

app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=API_VERSION,
    contact={"name": CONTACT_NAME,"email": CONTACT_EMAIL,},
)

def _parse_cors(origins_str: str):
    # support: "http://a,http://b" or "*"
    if origins_str.strip() == "*":
        return ["*"]
    return [o.strip() for o in origins_str.split(",") if o.strip()]

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static files (logos) ---
app.mount(f"/api/dmb/{API_VERSION}/static", StaticFiles(directory="static"), name="static")

# --- DB Init ---
# TODO: Move into Postgres, and this cause conflict on deploy
# Base.metadata.create_all(bind=engine)


# --- Run Migrations ---
def run_migrations():
    try:
        here = pathlib.Path(__file__).parent.resolve()
        alembic_ini_path = here / "alembic.ini"
        if not alembic_ini_path.exists():
            alembic_ini_path = here.parent / "alembic.ini"

        if not alembic_ini_path.exists():
            raise FileNotFoundError(f"alembic.ini not found at {alembic_ini_path}")

        alembic_cfg = Config(str(alembic_ini_path))
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

        # Check for multiple heads and merge if needed
        script  = ScriptDirectory.from_config(alembic_cfg)
        heads   = script.get_heads()
        if len(heads) > 1:
            logger.warning(f"Multiple heads detected: {heads}. Merging...")
            command.merge(alembic_cfg, "heads", message="Auto-merge multiple heads")

        command.upgrade(alembic_cfg, "head")
    except Exception:
        logger.error("Error while running alembic migrations:\n" + traceback.format_exc())
        raise

# --- Startup seeding ---
@app.on_event("startup")
def seed_data():
    """Seed a default user, accounts, and services (idempotent)."""

    # # Only seed in debug/dev environments
    # if not settings.DEBUG:
    #     return
    
    logging.warning(f"USE_MOCK_OSP = {settings.USE_MOCK_OSP}")

    try:
        logging.info("Running alembic migrations (upgrade head)...")
        run_migrations()
        logging.info("Alembic migrations applied.")
    except Exception as e:
        logging.error(f"Failed to run migrations: {e}")
        
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(phone="069382165").first()
        if not user:
            user = User(
                name="System Admin",
                phone="069382165",
                password_hash=hash_password("admin123"),
                pin_hash=hash_password("1234"),
                role="admin",
            )
            db.add(user)
            db.flush()

        existing_accounts = {a.number for a in db.query(Account).filter_by(user_id=user.id).all()}

        default_accounts = [
            {"name": "Main Wallet", "number": "168-168-168", "balance": Decimal("15000.00"), "currency": "USD"},
            {"name": "Savings", "number": "369-369-369", "balance": Decimal("50000.00"), "currency": "USD"},
        ]

        for acc in default_accounts:
            if acc["number"] not in existing_accounts:
                db.add(Account(user_id=user.id, **acc))

        # Seed default services
        existing_services = {s.code for s in db.query(Service).all()}
        default_services = [
            {"name": "CDC Public Service", "code": "cdc", "logo_url": "/static/logos/cdc.webp"},
            {"name": "Road Tax", "code": "road", "logo_url": "/static/logos/road.png"},
            {"name": "EDC Cambodia", "code": "edc", "logo_url": "/static/logos/edc.webp"},
            {"name": "Phnom Penh Solid Waste Management", "code": "ppswm", "logo_url": "/static/logos/ppswm.webp"},
        ]

        for svc in default_services:
            if svc["code"] not in existing_services:
                db.add(Service(**svc))

        db.commit()
        logging.info("Database seeding completed successfully.")

    except Exception as e:
        logging.error(f"Seeding failed: {e}")
        db.rollback()

    finally:
        db.close()

# --------- Versioned API Router ----------
api_router = APIRouter(prefix=f"/api/dmb/{API_VERSION}")


# Use explicit prefixes 
api_router.include_router(auth_routes.router)
api_router.include_router(accounts_routes.router)
api_router.include_router(payments_routes.router)
api_router.include_router(transactions_routes.router)
api_router.include_router(services_routes.router)

api_router.include_router(debug.router)  


api_router.include_router(user_management.router)
api_router.include_router(service_management.router)
api_router.include_router(transaction_management.router)
api_router.include_router(payment_management.router)
api_router.include_router(accounts_router)
# Mount the versioned API
app.include_router(api_router)

# # --- Routers ---
# app.include_router(auth_routes.router)
# app.include_router(accounts_routes.router)
# app.include_router(payments_routes.router)
# app.include_router(transactions_routes.router)
# app.include_router(services_routes.router)
# app.include_router(user_management.router)
# app.include_router(service_management.router)
# app.include_router(transaction_management.router)
# app.include_router(payment_management.router)
# app.include_router(accounts_router)


@app.get("/")
def root():
    return {"status": "ok", "app": "Dummy Bank API", "api_base": f"/api/dmb/{API_VERSION}/"}