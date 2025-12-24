from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from app.core.config import settings
from app.db.base import Base

from alembic import context
from sqlalchemy import engine_from_config, pool

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# Alembic Config
config = context.config

alembic_url = getattr(
    settings, "alembic_database_url", None
) or settings.database_url.replace("+asyncpg", "+psycopg")
config.set_main_option("sqlalchemy.url", alembic_url)


# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# metadata всех моделей, для autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме (генерация SQL без подключения)."""

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
    """Запуск миграций в 'online' режиме (с реальным подключением к БД)."""

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
