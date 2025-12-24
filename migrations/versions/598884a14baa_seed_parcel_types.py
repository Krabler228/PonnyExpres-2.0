"""seed parcel types

Revision ID: 598884a14baa
Revises: c1bcc70b6c65
Create Date: 2025-12-17 20:36:01.821319

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "598884a14baa"
down_revision: Union[str, Sequence[str], None] = "c1bcc70b6c65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    parcel_types_table = sa.table(
        "parcel_types",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )

    op.bulk_insert(
        parcel_types_table,
        [
            {"id": 1, "name": "small"},
            {"id": 2, "name": "medium"},
            {"id": 3, "name": "large"},
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM parcel_types WHERE id IN (1,2,3)")
