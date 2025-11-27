# backend/core/logging.py
import logging
import os
import sys
from typing import Optional

from loguru import logger
from core.config import settings


LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} - "
    "{message} | extra={extra}"
)

class InterceptHandler(logging.Handler):
    """
    Redirect standard logging (logging.getLogger) into loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Respect existing logger name
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(level, record.getMessage())


def _get_log_level() -> str:
    lvl: Optional[str] = getattr(settings, "LOG_LEVEL", "INFO")
    return str(lvl).upper()


def setup_logging() -> None:
    log_dir = getattr(settings, "LOG_PATH", "./logs")
    os.makedirs(log_dir, exist_ok=True)

    log_level = _get_log_level()

    # Remove default loguru handler to avoid duplicates
    logger.remove()

    # Decide if we need enqueue=True (multi-process)
    # SINGLE_PROCESS=1 → single process (no queue)
    # SINGLE_PROCESS=0 → multi-process (use queue)
    single_process = int(getattr(settings, "SINGLE_PROCESS", 1))
    use_enqueue = single_process == 0

    # Console
    logger.add(
        sys.stderr,
        level=log_level,
        format=LOG_FORMAT,
        backtrace=getattr(settings, "DEBUG", False),
        diagnose=getattr(settings, "DEBUG", False),
        enqueue=use_enqueue,
    )

    # app.log – all logs, rotated daily
    logger.add(
        os.path.join(log_dir, "app.log"),
        level=log_level,
        format=LOG_FORMAT,
        rotation="00:00",      
        retention="30 days",    
        enqueue=use_enqueue,
    )

    # error.log – only errors, rotated daily
    logger.add(
        os.path.join(log_dir, "error.log"),
        level="ERROR",
        format=LOG_FORMAT,
        rotation="00:00",
        retention="30 days",
        enqueue=use_enqueue,
    )

    # app_YYYYMMDD.log – per-day archive of all logs
    logger.add(
        os.path.join(log_dir, "app_{time:YYYYMMDD}.log"),
        level=log_level,
        format=LOG_FORMAT,
        # rotation based on filename pattern -> new file each day
        rotation="00:00",
        retention="90 days",
        enqueue=use_enqueue,
    )

    # error_YYYYMMDD.log – per-day archive of error logs
    logger.add(
        os.path.join(log_dir, "error_{time:YYYYMMDD}.log"),
        level="ERROR",
        format=LOG_FORMAT,
        rotation="00:00",
        retention="90 days",
        enqueue=use_enqueue,
    )

    # Intercept standard logging so anything using logging.getLogger() goes into loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Make uvicorn / fastapi loggers go through our handler as well
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        std_logger = logging.getLogger(name)
        std_logger.handlers = [InterceptHandler()]
        std_logger.propagate = False

    logger.info(f"Logging initialized path={log_dir} level={log_level} | module=core.logging")
