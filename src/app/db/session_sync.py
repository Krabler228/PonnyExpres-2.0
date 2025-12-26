from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.core.config import settings

engine = create_engine(
    settings.alembic_database_url or settings.database_url.replace("+asyncpg", ""),
    echo=False,
    future=True,
)

SyncSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_sync_session():
    return SyncSessionLocal()
