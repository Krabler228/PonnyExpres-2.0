"""add tracking_code column to parcels

Revision ID: 597564e20985
Revises: 598884a14baa
Create Date: 2025-12-24 12:12:53.165871

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "597564e20985"
down_revision: Union[str, Sequence[str], None] = "598884a14baa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "parcels",
        sa.Column("tracking_code", sa.String(length=32), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("parcels", "tracking_code")
