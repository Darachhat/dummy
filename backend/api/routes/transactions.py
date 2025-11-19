# backend/api/routes/transactions.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from core.permissions import get_current_user
from models.transaction import Transaction
from models.payment import Payment
from models.service import Service
from schemas.transaction import TransactionOut, PaginatedTransactions
from models.user import User

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=PaginatedTransactions)
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .join(Payment, Transaction.payment_id == Payment.id, isouter=True)
        .join(Service, Payment.service_id == Service.id, isouter=True)
    )

    total = q.count()
    items_orm = (
        q.offset((page - 1) * page_size)
         .limit(page_size)
         .all()
    )

    items: list[TransactionOut] = []
    for t in items_orm:
        p = t.payment
        s = getattr(p, "service", None) if p else None

        items.append(
            TransactionOut(
                id=t.id,
                transaction_id=t.transaction_id,
                reference_number=p.reference_number if p else t.reference_number,
                description=t.description,
                amount=p.total_amount if p and p.total_amount is not None else t.amount,
                currency= p.currency if p else t.currency,
                direction=t.direction,
                created_at=t.created_at,
                service_name=s.name if s else None,
                service_logo_url=s.logo_url if s else None,
                account_id=p.account_id if p else t.account_id,
            )
        )

    return PaginatedTransactions(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a single transaction, with payment + service details if available."""
    tx = (
        db.query(Transaction)
        .filter_by(id=transaction_id, user_id=user.id)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    p = tx.payment
    s = getattr(p, "service", None) if p else None

    # When there is no payment, fall back to raw tx data
    if not p:
        return TransactionOut(
            id=tx.id,
            transaction_id=tx.transaction_id,
            reference_number=tx.reference_number,
            description=tx.description,
            amount=float(tx.amount),
            currency=tx.currency,
            direction=tx.direction,
            created_at=tx.created_at,
            service_name=None,
            service_logo_url=None,
            account_id=tx.account_id,
        )

    return TransactionOut(
        id=tx.id,
        transaction_id=tx.transaction_id,
        reference_number=p.reference_number,
        description=tx.description,
        amount=float(p.amount),
        currency=p.currency,
        direction=tx.direction,
        created_at=tx.created_at,
        service_name=s.name if s else None,
        service_logo_url=s.logo_url if s else None,
        account_id=p.account_id,
    )
