import sqlalchemy
from alembic.config import Config
import pytest

from src.app.core.config import settings


def _sync_test_url() -> str:
    url = settings.test_database_url
    return url.replace("+asyncpg", "+psycopg")


@pytest.fixture(scope="session")
def alembic_engine():
    engine = sqlalchemy.create_engine(_sync_test_url())
    print("ALEMBIC ENGINE URL:", engine.url)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def alembic_config(alembic_engine):
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", str(alembic_engine.url))
    print("ALEMBIC CFG URL:", cfg.get_main_option("sqlalchemy.url"))
    return cfg
