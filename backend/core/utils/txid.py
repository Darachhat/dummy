# backend/core/utils/txid.py
from datetime import datetime

def generate_transaction_id_from_id(db_id: int, when: datetime | None = None) -> str:
    when = when or datetime.utcnow()
    return f"{when.strftime('%Y%m%d%H%M%S')}{db_id:06d}"