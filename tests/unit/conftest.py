import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.db.base import Base


@pytest.fixture(scope="function")
def sqlite_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def sqlite_session(sqlite_engine):
    SessionLocal = sessionmaker(bind=sqlite_engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()
