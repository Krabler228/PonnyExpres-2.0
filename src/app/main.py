from fastapi import FastAPI
from app.config.settings import settings

app = FastAPI(
    title=settings.app.name,
    version="0.1.0",
    debug=settings.app.debug,
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": settings.app.name,
    }
