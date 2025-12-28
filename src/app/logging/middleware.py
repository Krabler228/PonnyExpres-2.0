import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        session_id = request.cookies.get("session_id", "anonymous")
        request.state.session_id = session_id

        start_time = time.time()
        logger.info(
            f'{request.client.host} "{request.method} {request.url.path} HTTP/1.1"',
            extra={"request_id": request_id, "session_id": session_id},
        )

        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        logger.info(
            f"{request.method} {request.url.path} {response.status_code}",
            extra={
                "request_id": request_id,
                "session_id": session_id,
                "time_ms": round(process_time, 2),
            },
        )

        return response
