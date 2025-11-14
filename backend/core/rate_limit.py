# backend/core/rate_limit.py
import time
from typing import Dict, Tuple
from fastapi import HTTPException, Request

# key -> (reset_at_epoch, count)
_RL_STATE: Dict[str, Tuple[float, int]] = {}


def _make_key(client_id: str, scope: str) -> str:
    """
    Build a unique key for a client + scope.
    scope = where we apply the limiter (e.g. 'login', 'payments_confirm').
    """
    return f"{scope}:{client_id}"


def check_rate_limit(
    client_id: str,
    *,
    scope: str = "default",
    max_requests: int = 5,
    window_seconds: int = 60,
) -> None:
    """
    Simple in-memory sliding window counter.

    - client_id: identifier for the caller (e.g. IP, user id, phone, etc.)
    - scope: logical bucket (login/payment/etc)
    - max_requests: allowed requests per window_seconds
    """
    now = time.time()
    key = _make_key(client_id, scope)

    reset_at, count = _RL_STATE.get(key, (now + window_seconds, 0))

    # window expired → reset
    if now > reset_at:
        reset_at = now + window_seconds
        count = 0

    count += 1
    _RL_STATE[key] = (reset_at, count)

    if count > max_requests:
        retry_after = max(int(reset_at - now), 0)
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )


async def rate_limit_login(request: Request) -> None:
    """
    Rate-limit login attempts per client IP.
    5 requests / 60 seconds by default.
    """
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(
        client_id=client_ip,
        scope="login",
        max_requests=5,
        window_seconds=60,
    )
