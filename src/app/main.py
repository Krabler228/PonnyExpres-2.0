from fastapi import FastAPI, Request
from src.app.config.settings import settings
from src.app.middleware.session import setup_session_middleware
from src.app.dependencies.session import SessionId

from src.app.api.parcels import router as parcels_router
from src.app.api.public import router as public_router

app = FastAPI(
    title=settings.app.name,
    version="0.1.0",
    debug=settings.app.debug,
)

setup_session_middleware(app)

app.include_router(parcels_router)
app.include_router(public_router)


@app.get("/health")
async def health_check(request: Request, session_id: str = SessionId):
    return {
        "status": "healthy",
        "message": settings.app.name,
        "session_id": session_id,
    }
