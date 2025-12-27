from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.app.core.config import settings
from src.app.db.base import Base

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from src.app.middleware.session import setup_session_middleware
from src.app.dependencies.session import get_session_id


@pytest.fixture(scope="session")
def sync_engine():
    engine = create_engine(
        settings.test_database_url.replace("+asyncpg", ""),
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(sync_engine) -> Generator[Session, None, None]:
    SessionLocal = sessionmaker(bind=sync_engine)
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


def create_test_app_with_session() -> FastAPI:
    app = FastAPI()

    setup_session_middleware(app)

    @app.get("/session-test")
    async def session_test(session_id: str = Depends(get_session_id)):
        return {"session_id": session_id}

    return app


@pytest.fixture
def app_with_session() -> FastAPI:
    return create_test_app_with_session()


@pytest.fixture
def client(app_with_session: FastAPI) -> TestClient:
    return TestClient(app_with_session)
