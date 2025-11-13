# backend/core/utils/currency.py
from decimal import Decimal, InvalidOperation
from typing import Optional

from core.config import settings

DEFAULT_USD_TO_KHR = Decimal("4000")

def _get_rate_from_settings() -> Decimal:
    try:
        rate = getattr(settings, "USD_TO_KHR_RATE", None)
        if rate is None:
            return DEFAULT_USD_TO_KHR
        return Decimal(rate)
    except (InvalidOperation, TypeError, ValueError):
        return DEFAULT_USD_TO_KHR

def get_usd_to_khr_rate() -> Decimal:
    return _get_rate_from_settings()

def convert_amount(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    rate = settings.USD_TO_KHR_RATE or Decimal("4000")
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    amount = Decimal(amount)

    if from_currency == to_currency:
        return amount.quantize(Decimal("0.01"))

    if from_currency == "USD" and to_currency == "KHR":
        return (amount * rate).quantize(Decimal("0.01"))
    if from_currency == "KHR" and to_currency == "USD":
        return (amount / rate).quantize(Decimal("0.01"))

    return amount.quantize(Decimal("0.01"))
