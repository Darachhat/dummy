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


# 1. Lookup (Query Payment)
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


# 2. Commit (CDC expects transaction_id as numeric string)
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


async def osp_commit(reference_number: str, session_id: str, transaction_id: str):
    """CDC Commit Payment — strict validation"""
    url = f"{BASE_URL}/commit-payment"

    if not all([reference_number, session_id, transaction_id]):
        raise ValueError("Missing required parameters for commit-payment")

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
        logger.info(f"[OSP][commit] ← {res.status_code}: {res.text}")

        if res.status_code == 422:
            logger.error(f"[OSP][commit][422] Invalid data validation. Payload: {data}")
            logger.error(f"[OSP][commit][422] Response: {res.text}")

        res.raise_for_status()
        return res.json()



# 3. Confirm Payment
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
        logger.info(f"[OSP][confirm] ← {res.status_code}: {res.text}")

        if res.status_code != 200:
            logger.error(f"[OSP][confirm][ERROR BODY]: {res.text}")
        res.raise_for_status()
        return res.json()

# 4. Reverse Payment
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
        logger.info(f"[OSP][reverse] ← {res.status_code}: {res.text}")

        if res.status_code != 200:
            logger.error(f"[OSP][reverse][ERROR BODY]: {res.text}")
        res.raise_for_status()
        return res.json()
