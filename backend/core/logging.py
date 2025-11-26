# backend/core/logging.py
from __future__ import annotations
import logging, sys, os, threading
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger as _loguru_logger
from core.config import settings
from typing import Any

LOG_PATH = settings.LOG_PATH
LOG_LEVEL = settings.LOG_LEVEL
SINGLE_PROCESS = settings.SINGLE_PROCESS

LOG_DIR = Path(LOG_PATH)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _create_or_update_symlink(target: Path, link_name: Path) -> None:
    try:
        if link_name.exists() or link_name.is_symlink():
            try:
                link_name.unlink()
            except Exception:
                pass
        try:
            os.symlink(os.path.basename(target), link_name)
        except Exception:
            tmp = link_name.with_suffix(".ptr")
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(str(target))
            os.replace(tmp, link_name)
    except Exception:
        return


def _current_daily_filename(date: datetime | None = None) -> Path:
    d = date or datetime.now()
    return LOG_DIR / f"app_{d.strftime('%Y-%m-%d')}.log"


def _symlink_updater_daemon(stop_event: threading.Event) -> None:
    link = LOG_DIR / "app.log"
    while not stop_event.is_set():
        now = datetime.now()
        todays = _current_daily_filename(now)
        try:
            if not todays.exists():
                todays.touch(exist_ok=True)
        except Exception:
            pass
        _create_or_update_symlink(todays, link)
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        wait_seconds = (next_midnight - now).total_seconds()
        stop_event.wait(timeout=wait_seconds + 1)


def _safe_str(v: Any) -> str:
    """Stable safe string representation for values (handles nested dicts)."""
    try:
        # Prefer compact repr for dicts/lists, otherwise str()
        if isinstance(v, (dict, list, tuple)):
            return repr(v)
        return str(v)
    except Exception:
        return "<unserializable>"


def _safe_format(record: dict) -> str:
    extra = record.get("extra") or {}
    # flatten/format nested response safely if present
    response = extra.get("response")
    response_str = _safe_str(response) if response is not None else ""

    try:
        t = record["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    except Exception:
        t = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    level = getattr(record.get("level"), "name", str(record.get("level")))
    module = record.get("module") or record.get("name") or "-"
    function = record.get("function", "-")
    line = record.get("line", "-")
    message = record.get("message", "")

    # copy extra but remove the response object (already handled)
    extra_display = {k: v for k, v in extra.items() if k != "response"}
    # stringify values to avoid nested formatting issues
    extra_display = {k: _safe_str(v) for k, v in extra_display.items()}

    return f"{t} | {level:<8} | {module}:{function}:{line} - {message} | response={response_str} | extra={extra_display}"


def setup_logging() -> None:
    try:
        _loguru_logger.remove()
    except Exception:
        pass

    # console sink
    _loguru_logger.add(sys.stderr, level=LOG_LEVEL, format=_safe_format, enqueue=True, backtrace=True, diagnose=False)

    # daily file sink (callable formatter)
    _loguru_logger.add(
        str(LOG_DIR / "app_{time:YYYY-MM-DD}.log"),
        level=LOG_LEVEL,
        rotation="00:00",
        retention="14 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        format=_safe_format,
    )

    # ERROR-only sink — <--- important: use same callable formatter
    _loguru_logger.add(
        str(LOG_DIR / "error_{time:YYYY-MM-DD}.log"),
        level="ERROR",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        format=_safe_format,   # <--- previously missing, now added
    )

    # Intercept stdlib logging -> loguru (forward pre-formatted message as raw)
    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            try:
                formatted = record.getMessage()
                _loguru_logger.opt(exception=record.exc_info, raw=True).log(record.levelname, formatted)
            except Exception:
                try:
                    print(record.getMessage(), file=sys.stderr)
                except Exception:
                    pass

    logging.root.handlers = [logging.NullHandler()]
    logging.basicConfig(handlers=[logging.NullHandler()], level=logging.NOTSET)

    # ensure no duplicate intercept handlers
    try:
        for h in list(logging.root.handlers):
            if isinstance(h, InterceptHandler):
                try:
                    logging.root.removeHandler(h)
                except Exception:
                    pass
    except Exception:
        pass

    logging.root.addHandler(InterceptHandler())

    # quiet noisy libs
    for noisy in ("uvicorn.access", "uvicorn.error", "asyncio"):
        try:
            logging.getLogger(noisy).setLevel(LOG_LEVEL)
        except Exception:
            pass

    # symlink updater
    if SINGLE_PROCESS:
        stop_event = threading.Event()
        t = threading.Thread(target=_symlink_updater_daemon, args=(stop_event,), daemon=True, name="log-symlink-updater")
        t.start()
        _loguru_logger.debug("SINGLE_PROCESS=True: started symlink updater thread")
    else:
        _loguru_logger.debug("SINGLE_PROCESS=False: skipping symlink updater")

    _loguru_logger.debug(f"Logging initialized. logdir={LOG_DIR} level={LOG_LEVEL}")


# initialize on import
setup_logging()
logger = _loguru_logger
