#backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from decimal import Decimal
import logging

from core.config import settings
from core.security import hash_password
from db.base import Base
from db.session import engine, SessionLocal

# Routers
from api.routes import auth as auth_routes
from api.routes import accounts as accounts_routes
from api.routes import payments as payments_routes
from api.routes import transactions as transactions_routes
from api.routes import services as services_routes
from api.routes.admin import user_management, service_management, transaction_management, payment_management
from api.routes.admin.accounts import accounts_router

# Models
from models.user import User
from models.account import Account
from models.service import Service
from models.transaction import Transaction
from models.payment import Payment


app = FastAPI(title="Dummy Bank Backend")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static files (logos) ---
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- DB Init ---
# TODO: Move into Postgres, and this cause conflict on deploy
# Base.metadata.create_all(bind=engine)

# --- Startup seeding ---
@app.on_event("startup")
def seed_data():
    """Seed a default user, accounts, and services (idempotent)."""
    logging.warning(f"USE_MOCK_OSP = {settings.USE_MOCK_OSP}")
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


# --- Routers ---
app.include_router(auth_routes.router)
app.include_router(accounts_routes.router)
app.include_router(payments_routes.router)
app.include_router(transactions_routes.router)
app.include_router(services_routes.router)
app.include_router(user_management.router)
app.include_router(service_management.router)
app.include_router(transaction_management.router)
app.include_router(payment_management.router)
app.include_router(accounts_router)


@app.get("/")
def root():
    return {"status": "ok", "app": "Dummy Bank API"}
