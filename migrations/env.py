from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from src.app.db.base import Base
import src.app.db.models.parcel  # noqa: F401  ← важно: регистрирует модели в Base.metadata

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

config = context.config


if "PYTEST_CURRENT_TEST" in os.environ:
    test_url = settings.test_database_url
    if test_url is None:
        raise RuntimeError("TEST_DATABASE_URL is not set in settings")
    alembic_url = test_url.replace("+asyncpg", "+psycopg")
    config.set_main_option("sqlalchemy.url", alembic_url)
else:
    current_url = config.get_main_option("sqlalchemy.url")
    if not current_url:
        alembic_url = getattr(
            settings, "alembic_database_url", None
        ) or settings.database_url.replace("+asyncpg", "+psycopg")
        config.set_main_option("sqlalchemy.url", alembic_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
