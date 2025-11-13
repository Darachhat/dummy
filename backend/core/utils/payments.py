from datetime import datetime

def mark_confirmed(payment, db):
    payment.status = "confirmed"
    if not getattr(payment, "confirmed_at", None):
        payment.confirmed_at = datetime.utcnow()
    db.add(payment)
    db.commit()
    db.refresh(payment)