from datetime import datetime, timedelta, timezone

CAMBODIA_OFFSET = timedelta(hours=7)

def to_local_time(utc_dt: datetime):
    """Convert UTC datetime to Cambodia local time (UTC+7)."""
    if not utc_dt:
        return None
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    local_dt = utc_dt + CAMBODIA_OFFSET
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")

def to_utc(local_dt: datetime):
    """Convert Cambodia local datetime to UTC."""
    if not local_dt:
        return None
    if local_dt.tzinfo is None:
        local_dt = local_dt.replace(tzinfo=timezone.utc)
    utc_dt = local_dt - CAMBODIA_OFFSET
    return utc_dt
