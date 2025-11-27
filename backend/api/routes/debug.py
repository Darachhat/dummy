# backend/api/routes/debug.py
from fastapi import APIRouter, HTTPException
from loguru import logger

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.get("/log-error")
async def debug_log_error():
    logger.bind(
        test_log="error",
        endpoint="debug.log-error",
        note="This is a forced error for logging test",
        some_value={"a": 1, "b": "x"},
    ).error("Test ERROR log from /debug/log-error")

    # Also trigger an exception with stacktrace
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.exception("Forced exception in /debug/log-error")
        raise HTTPException(status_code=500, detail="Forced error for logging test")
