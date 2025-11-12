from datetime import datetime

def generate_transaction_id_from_id(db_id: int, when: datetime | None = None) -> str:
    when = when or datetime.utcnow()
    return f"TX-{when.strftime('%Y%m%d')}-{db_id:06d}"