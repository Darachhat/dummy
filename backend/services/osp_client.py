import httpx
import logging
from core.config import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "Authorization": settings.OSP_AUTH,
    "Content-Type": "application/x-www-form-urlencoded",
}

BASE_URL = settings.OSP_BASE_URL
TIMEOUT = settings.OSP_TIMEOUT or 30


# 1️ Query Payment (Lookup)
async def osp_lookup(reference_number: str):
    """CDC Query Payment — GET"""
    url = f"{BASE_URL}/query-payment"
    params = {
        "reference_number": reference_number,
        "partner": settings.OSP_PARTNER,
    }
    logger.info(f"[OSP][lookup] → GET {url} {params}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.get(url, params=params, headers={"Authorization": settings.OSP_AUTH})
        logger.info(f"[OSP][lookup] ← {res.status_code}: {res.text}")
        res.raise_for_status()
        return res.json()


# 2️ Commit Payment
async def osp_commit(reference_number: str, session_id: str, transaction_id: str):
    """CDC Commit Payment — POST form-data"""
    url = f"{BASE_URL}/commit-payment"
    numeric_tid = transaction_id.replace("TID", "").zfill(6)

    data = {
        "reference_number": reference_number,
        "session_id": session_id,
        "transaction_id": numeric_tid,
        "partner": settings.OSP_PARTNER,
    }

    logger.info(f"[OSP][commit] → POST {url} {data}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, data=data, headers=HEADERS)
        if res.status_code != 200:
            logger.error(f"[OSP][commit][{res.status_code}] {res.text}")
        else:
            logger.info(f"[OSP][commit][OK] {res.text}")
        res.raise_for_status()
        return res.json()


# 3️ Confirm Payment
async def osp_confirm(reference_number: str, transaction_id: str, acknowledgement_id: str):
    """CDC Confirm Payment — POST form-data"""
    url = f"{BASE_URL}/confirm-payment"
    numeric_tid = transaction_id.replace("TID", "").zfill(6)

    data = {
        "reference_number": reference_number,
        "transaction_id": numeric_tid,
        "acknowledgement_id": acknowledgement_id,
        "partner": settings.OSP_PARTNER,
    }

    logger.info(f"[OSP][confirm] → POST {url} {data}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, data=data, headers=HEADERS)
        if res.status_code != 200:
            logger.error(f"[OSP][confirm][{res.status_code}] {res.text}")
        else:
            logger.info(f"[OSP][confirm][OK] {res.text}")
        res.raise_for_status()
        return res.json()


# 4️ Reverse Payment
async def osp_reverse(reference_number: str, transaction_id: str, reversal_transaction_id: str):
    """CDC Reverse Payment — POST form-data"""
    url = f"{BASE_URL}/reverse-payment"
    numeric_tid = transaction_id.replace("TID", "").zfill(6)
    numeric_rtid = reversal_transaction_id.replace("REV-", "").zfill(6)

    data = {
        "reference_number": reference_number,
        "transaction_id": numeric_tid,
        "reversal_transaction_id": numeric_rtid,
        "partner": settings.OSP_PARTNER,
    }

    logger.info(f"[OSP][reverse] → POST {url} {data}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, data=data, headers=HEADERS)
        if res.status_code != 200:
            logger.error(f"[OSP][reverse][{res.status_code}] {res.text}")
        else:
            logger.info(f"[OSP][reverse][OK] {res.text}")
        res.raise_for_status()
        return res.json()
