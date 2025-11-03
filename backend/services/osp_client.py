import httpx
import logging
from core.config import settings

logger = logging.getLogger(__name__)

HEADERS = {"Authorization": settings.CDC_API_AUTH}
BASE_URL = settings.CDC_API_BASE
TIMEOUT = settings.OSP_TIMEOUT or 10


async def osp_lookup(reference_number: str):
    """Call OSP query-payment API"""
    url = f"{BASE_URL}/query-payment"
    params = {"reference_number": reference_number, "partner": settings.OSP_PARTNER}
    logger.info(f"[OSP][lookup] → {url} {params}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.get(url, params=params, headers=HEADERS)
        logger.info(f"[OSP][lookup] ← {res.status_code}: {res.text}")
        res.raise_for_status()
        return res.json()


async def osp_commit(reference_number: str, session_id: str):
    """Call OSP commit-payment API"""
    url = f"{BASE_URL}/commit-payment"
    params = {"reference_number": reference_number, "session_id": session_id, "partner": settings.OSP_PARTNER}
    logger.info(f"[OSP][commit] → {url} {params}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.get(url, params=params, headers=HEADERS)
        logger.info(f"[OSP][commit] ← {res.status_code}: {res.text}")
        res.raise_for_status()
        return res.json()


async def osp_confirm(reference_number: str, transaction_id: int):
    """Call OSP confirm-payment API"""
    url = f"{BASE_URL}/confirm-payment"
    params = {
        "reference_number": reference_number,
        "transaction_id": transaction_id,
        "partner": settings.OSP_PARTNER,
        "reference_number": reference_number,
        "transaction_id": transaction_id,
        "partner": settings.OSP_PARTNER,
    }

    logger.info(f"[OSP][confirm] → {url} {params}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.get(url, params=params, headers=HEADERS)
        logger.info(f"[OSP][confirm] ← {res.status_code}: {res.text}")
        res.raise_for_status()
        return res.json()


async def osp_reverse(reference_number: str, session_id: str):
    """Call OSP reverse-payment API"""
    url = f"{BASE_URL}/reverse-payment"
    params = {
        "reference_number": reference_number,
        "session_id": session_id,
        "partner": settings.OSP_PARTNER,
    }

    logger.info(f"[OSP][reverse] → {url} {params}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.get(url, params=params, headers=HEADERS)
        logger.info(f"[OSP][reverse] ← {res.status_code}: {res.text}")
        res.raise_for_status()
        return res.json()
