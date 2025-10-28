from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from db import Base, engine, SessionLocal
from models import User, Account, Payment, Transaction, Service
from auth import router as auth_router
from deps import get_user_id
from services.invoices import mock_lookup
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Dummy Bank Backend")
app.include_router(auth_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(User).first():
        u = User(phone="069382165",
                 password_hash=bcrypt.hash("admin123"),
                 pin_hash=bcrypt.hash("1234"))
        db.add(u); db.flush()
        db.add_all([
            Account(user_id=u.id, name="Main Wallet", number="100-001", balance_cents=150_000, currency="USD"),
            Account(user_id=u.id, name="Savings",     number="200-001", balance_cents=50_000,  currency="USD"),
        ])
    # Seed default services
    if not db.query(Service).first():
        db.add_all([
        Service(name="CDC Public Service", code="cdc", logo_url="/static/logos/cdc.webp"),
        Service(name="Road Tax", code="road", logo_url="/static/logos/road.png"),
        Service(name="EDC Cambodia", code="edc", logo_url="/static/logos/edc.webp"),
        Service(name="Phnom Penh Solid Waste Management", code="ppswm", logo_url="/static/logos/ppswm.webp"),
        ])
    db.commit()


def db_sess():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# -------- Accounts & balances --------
@app.get("/me")
def me(user_id: int = Depends(get_user_id), db: Session = Depends(db_sess)):
    user = db.query(User).get(user_id)
    accounts = db.query(Account).filter_by(user_id=user_id).all()
    total = sum(a.balance_cents for a in accounts)
    return {"user": {"id": user.id, "phone": user.phone},
            "total_balance_cents": total,
            "accounts": [{"id":a.id,"name":a.name,"number":a.number,"balance_cents":a.balance_cents,"currency":a.currency} for a in accounts]}

@app.get("/accounts/{account_id}")
def account_detail(account_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(db_sess)):
    a = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    if not a: raise HTTPException(404, "Account not found")
    return {"id": a.id, "name": a.name, "number": a.number, "balance_cents": a.balance_cents, "currency": a.currency}


# -------- Payment: lookup → start → confirm --------
@app.get("/payments/lookup")
def lookup(reference_number: str, user_id: int = Depends(get_user_id)):
    return mock_lookup(reference_number)

@app.post("/payments/start")
def start_payment(account_id: int, reference_number: str, service_id: int,
                  user_id: int = Depends(get_user_id), db: Session = Depends(db_sess)):

    inv = mock_lookup(reference_number)  # returns customer_name, amount_cents, etc.
    a = db.query(Account).filter_by(id=account_id, user_id=user_id).first()
    s = db.query(Service).filter_by(id=service_id).first()

    if not a:
        raise HTTPException(404, "Account not found")
    if not s:
        raise HTTPException(404, "Service not found")
        
    FEE = 500  

    pi = Payment(
        user_id=user_id,
        account_id=a.id,
        reference_number=reference_number,
        service_id=s.id,
        session_id=inv["session_id"],
        amount_cents=inv["amount_cents"],
        customer_name=inv["customer_name"],
        fee_cents=FEE,
        total_amount_cents=inv["amount_cents"] + FEE,
        currency=inv["currency"],
        status="started"
    )

    db.add(pi)
    db.commit()
    db.refresh(pi)

    return {
        "payment_id": pi.id,
        "reference_number": pi.reference_number,
        "customer_name": pi.customer_name,
        "amount_cents": pi.amount_cents,
        "fee_cents": pi.fee_cents,
        "total_amount_cents": pi.total_amount_cents,
        "service": {
            "id": s.id,
            "name": s.name,
            "logo_url": s.logo_url
        }
    }


class ConfirmBody:
    pin: str

@app.post("/payments/{payment_id}/confirm")
def confirm_payment(payment_id: int, pin: str = Query(...),
                    user_id: int = Depends(get_user_id),
                    db: Session = Depends(db_sess)):
    pi = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not pi or pi.status != "started":
        raise HTTPException(404, "Payment not found or invalid")

    user = db.query(User).get(user_id)
    if not bcrypt.verify(pin, user.pin_hash):
        raise HTTPException(status_code=401, detail="Invalid PIN")

    a = db.query(Account).filter_by(id=pi.account_id, user_id=user_id).first()
    if a.balance_cents < pi.total_amount_cents:
        raise HTTPException(402, "Insufficient funds")

    a.balance_cents -= pi.total_amount_cents
    tx = Transaction(
        user_id=user_id,
        account_id=a.id,
        reference_number=pi.reference_number,
        amount_cents=pi.total_amount_cents,
        currency=pi.currency,
        direction="debit",
        description=f"Payment to {pi.customer_name or pi.service.name}"
    )
    db.add(tx)
    db.flush() 

    # Link to payment
    pi.status = "confirmed"
    pi.transaction_id = tx.id
    db.commit()

    return {
        "status": "success",
        "transaction_id": tx.id,  
        "account_id": a.id,
        "new_balance_cents": a.balance_cents,
        "reference_number": pi.reference_number,
        "customer_name": pi.customer_name,
        "amount_cents": pi.amount_cents,
        "fee_cents": pi.fee_cents,
        "total_amount_cents": pi.total_amount_cents,
        "service": {
            "name": pi.service.name,
            "logo_url": pi.service.logo_url
        }
    }


@app.post("/payments/{payment_id}/reverse")
def reverse_payment(payment_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(db_sess)):
    pi = db.query(Payment).filter_by(id=payment_id, user_id=user_id).first()
    if not pi or pi.status != "confirmed":
        raise HTTPException(404, "Only confirmed payments can be reversed")
    a = db.query(Account).filter_by(id=pi.account_id, user_id=user_id).first()
    a.balance_cents += pi.amount_cents
    db.add(Transaction(user_id=user_id, account_id=a.id, reference_number=pi.reference_number,
                       amount_cents=pi.amount_cents, currency=pi.currency, direction="credit",
                       description="Payment reversal"))
    pi.status = "reversed"
    db.commit()
    return {"status": "reversed", "account_id": a.id, "new_balance_cents": a.balance_cents}
   
# -------- Transactions --------
@app.get("/transactions")
def list_transactions(user_id: int = Depends(get_user_id), db: Session = Depends(db_sess)):
    txs = (
        db.query(Transaction)
        .filter_by(user_id=user_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    results = []
    for t in txs:
        payment = db.query(Payment).filter_by(transaction_id=t.id).first()
        results.append({
            "id": t.id,
            "transaction_id": t.id,
            "reference_number": payment.reference_number if payment else t.reference_number,
            "description": t.description,
            "amount_cents": payment.amount_cents if payment else t.amount_cents,
            "fee_cents": payment.fee_cents if payment else 0,
            "total_amount_cents": payment.total_amount_cents if payment else t.amount_cents,
            "customer_name": payment.customer_name if payment else None,
            "service_name": payment.service.name if payment and payment.service else None,
            "service_logo_url": payment.service.logo_url if payment and payment.service else None,
            "direction": t.direction,
            "created_at": t.created_at,
        })

    return results


# Get transaction by ID
@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: int, user_id: int = Depends(get_user_id), db: Session = Depends(db_sess)):
    tx = db.query(Transaction).filter_by(id=transaction_id, user_id=user_id).first()
    if not tx:
        raise HTTPException(404, "Transaction not found")

    payment = db.query(Payment).filter_by(transaction_id=tx.id).first()
    if not payment:
        return {
            "transaction_id": tx.id,
            "reference_number": tx.reference_number,
            "description": tx.description,
            "amount_cents": tx.amount_cents,
            "currency": tx.currency,
            "direction": tx.direction,
            "created_at": tx.created_at,
        }

    return {
        "transaction_id": tx.id,
        "reference_number": payment.reference_number,
        "customer_name": payment.customer_name,
        "amount_cents": payment.amount_cents,
        "fee_cents": payment.fee_cents,
        "total_amount_cents": payment.total_amount_cents,
        "service_name": payment.service.name if payment.service else None,
        "service_logo_url": payment.service.logo_url if payment.service else None,
        "account_id": payment.account_id,
        "currency": payment.currency,
        "direction": tx.direction,
        "created_at": tx.created_at,
    }

@app.get("/services")
def list_services(db: Session = Depends(db_sess)):
    services = db.query(Service).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "logo_url": s.logo_url,
            "description": s.description
        }
        for s in services
    ]

@app.post("/accounts/transfer")
def transfer_funds(
    from_id: int,
    to_id: int,
    amount_cents: int,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(db_sess)
):
    from_acc = db.query(Account).filter_by(id=from_id, user_id=user_id).first()
    to_acc = db.query(Account).filter_by(id=to_id, user_id=user_id).first()

    if not from_acc or not to_acc:
        raise HTTPException(status_code=404, detail="Account not found")
    if from_acc.balance_cents < amount_cents:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    from_acc.balance_cents -= amount_cents
    to_acc.balance_cents += amount_cents

    db.commit()
    return {
        "status": "success",
        "from_balance": from_acc.balance_cents,
        "to_balance": to_acc.balance_cents
    }
