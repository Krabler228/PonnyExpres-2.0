import uuid
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.types import ASGIApp

SESSION_COOKIE_NAME = "session_id"
SESSION_COOKIE_PATH = "/"
SESSION_COOKIE_SAMESITE = "lax"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False


def setup_session_middleware(app: ASGIApp) -> None:
    @app.middleware("http")
    async def session_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        new_session_created = False

        if session_id is None:
            session_id = str(uuid.uuid4())
            new_session_created = True

        request.state.session_id = session_id

        response = await call_next(request)

        if new_session_created:
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=session_id,
                path=SESSION_COOKIE_PATH,
                httponly=SESSION_COOKIE_HTTPONLY,
                secure=SESSION_COOKIE_SECURE,
                samesite=SESSION_COOKIE_SAMESITE,
            )
        return response
