# --- Request ID Tracking ---
import contextvars
import logging
import logging.handlers
import sys
import uuid
from pathlib import Path
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from core.config.settings import settings

_request_id_ctx_var = contextvars.ContextVar("request_id", default="system")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        token = _request_id_ctx_var.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            _request_id_ctx_var.reset(token)


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = _request_id_ctx_var.get()
        return True


# --- Logging Configuration ---
def configure_logging():
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)

    # Base Formatter
    fmt = "%(asctime)s | %(levelname)-8s | [%(request_id)s] | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    formatter = logging.Formatter(fmt)

    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIDFilter())

    # 2. File Handlers (Rotation)
    def create_file_handler(filename, level, filter_name=None):
        handler = logging.handlers.RotatingFileHandler(
            log_dir / filename, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        handler.setFormatter(formatter)
        handler.setLevel(level)
        handler.addFilter(RequestIDFilter())
        return handler

    # Root Logger Setup
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Remove existing handlers
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(create_file_handler("system.log", logging.WARNING))

    # Specialized Loggers
    # AI Logger
    ai_logger = logging.getLogger("jobhunterai.ai")
    ai_logger.propagate = True  # Let it bubble up to root for console/system.log
    ai_logger.addHandler(create_file_handler("ai.log", logging.DEBUG))

    # Scraper Logger
    scraper_logger = logging.getLogger("jobhunterai.scraper")
    scraper_logger.propagate = True
    scraper_logger.addHandler(create_file_handler("scraper.log", logging.DEBUG))

    # Suppress noisy library logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


# Initialize on import
configure_logging()
