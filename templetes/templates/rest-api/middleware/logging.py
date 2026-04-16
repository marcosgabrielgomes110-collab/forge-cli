"""Middleware de logging para requests."""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from utils.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware que loga todas as requisições HTTP."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log da request
        logger.info(f"→ {request.method} {request.url.path}")

        response: Response = await call_next(request)

        # Log da response
        duration = time.time() - start_time
        status = response.status_code
        status_icon = "✓" if status < 400 else "✗"

        logger.info(
            f"← {status_icon} {request.method} {request.url.path} "
            f"- {status} ({duration:.3f}s)"
        )

        # Header com tempo de processamento
        response.headers["X-Process-Time"] = str(duration)

        return response
