"""Add output_sulfur_pct to unit_yields for blend quality tracking.

Revision ID: 003
Revises: 002
Create Date: 2026-04-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "unit_yields",
        sa.Column("output_sulfur_pct", sa.Numeric(10, 6), nullable=True, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("unit_yields", "output_sulfur_pct")
