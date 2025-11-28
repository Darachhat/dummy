import httpx
from core.config import settings
from typing import Any
from loguru import logger
from core.config import settings
import httpx

from loguru import logger

HEADERS = {
    "Authorization": settings.OSP_AUTH,
    "Content-Type": "application/x-www-form-urlencoded",
}

BASE_URL = settings.OSP_BASE_URL
TIMEOUT = settings.OSP_TIMEOUT or 30

SENSITIVE_KEYS = {"pin"} 

def _value_and_type(value: Any) -> dict[str, Any]:
    return {
        "value": value if isinstance(value, (str, int, float, bool)) or value is None else repr(value),
        "type": type(value).__name__,
    }


def _build_param_log(params: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        k: {"value": "***masked***", "type": "secret"} if k.lower() in SENSITIVE_KEYS else _value_and_type(v)
        for k, v in params.items()
    }


# 1️ Query Payment (Lookup)
async def osp_lookup(reference_number: str):
    """CDC Query Payment — GET"""
    url = f"{BASE_URL}/query-payment"
    params = {
        "reference_number": reference_number,
        "partner": settings.OSP_PARTNER,
    }
    logger.bind(
        osp_log="request",
        endpoint="osp.lookup",
        url=url,
        params=_build_param_log(params),
    ).info("[OSP][lookup] → GET")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.get(url, params=params, headers={"Authorization": settings.OSP_AUTH})
        logger.bind(
            osp_log="response",
            endpoint="osp.lookup",
            url=url,
            status_code=res.status_code,
        ).info(f"[OSP][lookup] ← {res.status_code}: {res.text}")
        res.raise_for_status()
        return res.json()
    
# Lookup Failed Simulation Service
async def lookup_failed(reference_number: str):
    url = f"{BASE_URL}/lookup-failed"
    data = {
        "reference_number": reference_number,
        "partner": "failed lookup test",
    }

    logger.bind(
        osp_log="request",
        endpoint="osp.lookup_failed",
        url=url,
        data=_build_param_log(data),
    ).info("[OSP][lookup_failed] → POST")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, data=data, headers=HEADERS)
        logger.bind(
                osp_log="response",
                endpoint="osp.lookup_failed",
                url=url,
                status_code=res.status_code,
        ).error(f"[OSP][lookup_failed][FAIL] {res.text}")
        res.raise_for_status()
        return res.json()



# 2️ Commit Payment
async def osp_commit(reference_number: str, session_id: str, transaction_id: str):
    """CDC Commit Payment — POST form-data"""
    url = f"{BASE_URL}/commit-payment"
    numeric_tid = transaction_id

    data = {
        "reference_number": reference_number,
        "session_id": session_id,
        "transaction_id": numeric_tid,
        "partner": settings.OSP_PARTNER,
    }
    logger.bind(
        osp_log="request",
        endpoint="osp.commit",
        url=url,
        data=_build_param_log(data),
    ).info("[OSP][commit] → POST")

    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, data=data, headers=HEADERS)
        if res.status_code != 200:
            logger.bind(
                osp_log="response",
                endpoint="osp.commit",
                url=url,
                status_code=res.status_code,
            ).error(f"[OSP][commit][FAIL] {res.text}")
        else:
            logger.bind(
                osp_log="response",
                endpoint="osp.commit",
                url=url,
                status_code=res.status_code,
            ).info(f"[OSP][commit][OK] {res.text}")
        res.raise_for_status()
        return res.json()

# Commit Failed Simulation Service
async def commt_failed(reference_number: str, session_id: str, transaction_id: str):
    url = f"{BASE_URL}/commit-failed"
    data = {
        "refernce_number": reference_number,
        "session_id": session_id,
        "transaction_id": transaction_id,
        "partner": "failed commit test",
    }

    logger.bind(
        osp_log="request",
        endpoint="osp.commit_failed",
        url=url,
        data=_build_param_log(data),
    ).info("[OSP][commit_failed] → POST")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, data=data, headers=HEADERS)
        logger.bind(
                osp_log="response",
                endpoint="osp.commit_failed",
                url=url,
                status_code=res.status_code,
        ).error(f"[OSP][commit_failed][FAIL] {res.text}")
        res.raise_for_status()
        return res.json()


# 3️ Confirm Payment
async def osp_confirm(reference_number: str, transaction_id: str, acknowledgement_id: str):
    """CDC Confirm Payment — POST form-data"""
    url = f"{BASE_URL}/confirm-payment"

    data = {
        "reference_number": reference_number,
        "transaction_id": transaction_id,
        "acknowledgement_id": acknowledgement_id,
        "partner": settings.OSP_PARTNER,
    }

    logger.bind(
        osp_log="request",
        endpoint="osp.confirm",
        url=url,
        data=_build_param_log(data),
    ).info("[OSP][confirm] → POST")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, data=data, headers=HEADERS)
        if res.status_code != 200:
            logger.bind(
                osp_log="response",
                endpoint="osp.confirm",
                url=url,
                status_code=res.status_code,
            ).error(f"[OSP][confirm][FAIL] {res.text}")
        else:
            logger.bind(
                osp_log="response",
                endpoint="osp.confirm",
                url=url,
                status_code=res.status_code,
            ).info(f"[OSP][confirm][OK] {res.text}")
        res.raise_for_status()
        return res.json()

#Confirm Failed Simulation Service
async def confirm_failed(reference_number: str, transaction_id: str, acknowledgement_id: str):
    url = f"{BASE_URL}/confirm-failed"
    data = {
        "reference_number": reference_number,
        "transaction_id": transaction_id,
        "acknowledgement_id": acknowledgement_id,
        "partner": "failed confirm test",
    }

    logger.bind(
        osp_log="request",
        endpoint="osp.confirm_failed",
        url=url,
        data=_build_param_log(data),
    ).info("[OSP][confirm_failed] → POST")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, data=data, headers=HEADERS)
        logger.bind(
                osp_log="response",
                endpoint="osp.confirm_failed",
                url=url,
                status_code=res.status_code,
        ).error(f"[OSP][confirm_failed][FAIL] {res.text}")
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

    logger.bind(
        osp_log="request",
        endpoint="osp.reverse",
        url=url,
        data=_build_param_log(data),
    ).info("[OSP][reverse] → POST")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, data=data, headers=HEADERS)
        if res.status_code != 200:
            logger.bind(
                osp_log="response",
                endpoint="osp.reverse",
                url=url,
                status_code=res.status_code,
            ).error(f"[OSP][reverse][FAIL] {res.text}")
        else:
            logger.bind(
                osp_log="response",
                endpoint="osp.reverse",
                url=url,
                status_code=res.status_code,
            ).info(f"[OSP][reverse][OK] {res.text}")
        res.raise_for_status()
        return res.json()

# Reverse Failed Simulation Service
async def reverse_failed(reference_number: str, transaction_id: str, reversal_transaction_id: str):
    url = f"{BASE_URL}/reverse-failed"
    data = {
        "reference_number": reference_number,
        "transaction_id": transaction_id,
        "reversal_transaction_id": reversal_transaction_id,
        "partner": "failed reverse test",
    }

    logger.bind(
        osp_log="request",
        endpoint="osp.reverse_failed",
        url=url,
        data=_build_param_log(data),
    ).info("[OSP][reverse_failed] → POST")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, data=data, headers=HEADERS)
        logger.bind(
                osp_log="response",
                endpoint="osp.reverse_failed",
                url=url,
                status_code=res.status_code,
        ).error(f"[OSP][reverse_failed][FAIL] {res.text}")
        res.raise_for_status()
        return res.json()