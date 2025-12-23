from fastapi import Depends, Request


def get_session_id(request: Request) -> str:
    session_id = getattr(request.state, "session_id", None)
    if session_id is None:
        raise RuntimeError(
            "session_id не установлен request.state. Проверь концфигурацию middleware сессий."
        )
    return session_id


SessionId = Depends(get_session_id)
