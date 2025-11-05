import httpx
import logging
from core.config import settings

logger = logging.getLogger(__name__)

HEADERS = {"Authorization": settings.OSP_AUTH}
BASE_URL = settings.OSP_BASE_URL
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


async def osp_commit(reference_number: str, session_id: str, transaction_id: str):
    """Call OSP commit-payment API"""
    url = f"{BASE_URL}/commit-payment"
    data = {
        "reference_number": reference_number,
        "session_id": session_id,
        "transaction_id": transaction_id,
        "partner": settings.OSP_PARTNER,
    }
    logger.info(f"[OSP][commit] → POST {url} {data}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, json=data, headers=HEADERS)
        logger.info(f"[OSP][commit] ← {res.status_code}: {res.text}")
        res.raise_for_status()
        return res.json()


async def osp_confirm(reference_number: str, session_id: str, transaction_id: str, acknowledgement_id: str):
    """Call OSP confirm-payment API"""
    url = f"{BASE_URL}/confirm-payment"
    data = {
        "reference_number": reference_number,
        "session_id": session_id,
        "transaction_id": transaction_id,
        "acknowledgement_id": acknowledgement_id,  # ✅ REQUIRED FIELD
        "partner": settings.OSP_PARTNER,
    }

    logger.info(f"[OSP][confirm] → POST {url} {data}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, json=data, headers=HEADERS)
        logger.info(f"[OSP][confirm] ← {res.status_code}: {res.text}")
        if res.status_code != 200:
            logger.error(f"[OSP][confirm][ERROR BODY]: {res.text}")
        res.raise_for_status()
        return res.json()



async def osp_reverse(reference_number: str, session_id: str):
    """Call OSP reverse-payment API"""
    url = f"{BASE_URL}/reverse-payment"
    data = {
        "reference_number": reference_number,
        "session_id": session_id,
        "partner": settings.OSP_PARTNER,
    }
    logger.info(f"[OSP][reverse] → POST {url} {data}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, json=data, headers=HEADERS)
        logger.info(f"[OSP][reverse] ← {res.status_code}: {res.text}")
        res.raise_for_status()
        return res.json()
