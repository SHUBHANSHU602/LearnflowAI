"""Minimal request observability without logging user queries or file contents."""
import logging
import time
import uuid

from fastapi import Request

logger = logging.getLogger("learnflow.requests")


async def request_logging_middleware(request: Request, call_next):
    started = time.monotonic()
    request_id = uuid.uuid4().hex
    response = await call_next(request)
    elapsed_ms = round((time.monotonic() - started) * 1000, 1)
    # Avoid logging query/body contents, original filenames, auth headers or raw IDs.
    logger.info(
        "request_id=%s method=%s route=%s status=%s elapsed_ms=%.1f",
        request_id, request.method,
        request.scope.get("route").path if request.scope.get("route") else "<unknown>",
        response.status_code, elapsed_ms,
    )
    response.headers["X-Request-ID"] = request_id
    return response
