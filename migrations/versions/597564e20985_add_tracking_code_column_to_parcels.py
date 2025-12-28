"""add tracking_code column to parcels

Revision ID: 597564e20985
Revises: 598884a14baa
Create Date: 2025-12-24 12:12:53.165871

"""

from typing import Sequence, Union

from alembic import op  # noqa
import sqlalchemy as sa  # noqa


# revision identifiers, used by Alembic.
revision: str = "597564e20985"
down_revision: Union[str, Sequence[str], None] = "598884a14baa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: tracking_code уже создаётся в c1bcc70b6c65."""
    # Колонка tracking_code добавлена в таблицу parcels
    # прямо в миграции c1bcc70b6c65_create_parcels,
    # поэтому здесь ничего делать не нужно.
    pass


def downgrade() -> None:
    """No-op: отдельного удаления tracking_code не требуется."""
    # При откате до base таблица parcels будет удалена
    # в миграции c1bcc70b6c65, вместе с колонкой tracking_code.
    pass
