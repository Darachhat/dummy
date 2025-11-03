import httpx
from core.config import settings

async def osp_lookup(reference_number: str):
    url = f"{settings.OSP_BASE_URL}/query-payment"
    params = {"partner": settings.OSP_PARTNER, "reference_number": reference_number}
    headers = {"authorization": settings.OSP_AUTH}

    async with httpx.AsyncClient(timeout=settings.OSP_TIMEOUT) as client:
        resp = await client.get(url, params=params, headers=headers)
        return resp.json()

async def osp_commit(reference_number: str, session_id: str, transaction_id: str):
    url = f"{settings.OSP_BASE_URL}/commit-payment"
    params = {
        "partner": settings.OSP_PARTNER,
        "reference_number": reference_number,
        "session_id": session_id,
        "transaction_id": transaction_id,
    }
    headers = {"authorization": settings.OSP_AUTH}

    async with httpx.AsyncClient(timeout=settings.OSP_TIMEOUT) as client:
        resp = await client.get(url, params=params, headers=headers)
        return resp.json()

async def osp_confirm(reference_number: str, transaction_id: str, acknowledgement_id: str):
    url = f"{settings.OSP_BASE_URL}/confirm-payment"
    params = {
        "partner": settings.OSP_PARTNER,
        "reference_number": reference_number,
        "transaction_id": transaction_id,
        "acknowledgement_id": acknowledgement_id,
    }
    headers = {"authorization": settings.OSP_AUTH}

    async with httpx.AsyncClient(timeout=settings.OSP_TIMEOUT) as client:
        resp = await client.get(url, params=params, headers=headers)
        return resp.json()

async def osp_reverse(reference_number: str, transaction_id: str, reversal_transaction_id: str):
    url = f"{settings.OSP_BASE_URL}/reverse-payment"
    params = {
        "partner": settings.OSP_PARTNER,
        "reference_number": reference_number,
        "transaction_id": transaction_id,
        "reversal_transaction_id": reversal_transaction_id,
    }
    headers = {"authorization": settings.OSP_AUTH}

    async with httpx.AsyncClient(timeout=settings.OSP_TIMEOUT) as client:
        resp = await client.get(url, params=params, headers=headers)
        return resp.json()
