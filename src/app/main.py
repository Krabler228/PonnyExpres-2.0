from fastapi import FastAPI, Request
from app.config.settings import settings
from app.middleware.session import setup_session_middleware
from app.dependencies.session import SessionId

app = FastAPI(
    title=settings.app.name,
    version="0.1.0",
    debug=settings.app.debug,
)

setup_session_middleware(app)


@app.get("/health")
async def health_check(request: Request, session_id: str = SessionId):
    return {
        "status": "healthy",
        "message": settings.app.name,
        "session_id": session_id,
    }
