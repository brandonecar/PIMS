"""Add guest_id to cases for anonymous workspace isolation.

Revision ID: 004
Revises: 003
Create Date: 2026-04-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cases",
        sa.Column("guest_id", sa.String(36), nullable=True),
    )
    op.create_index("ix_cases_guest_id", "cases", ["guest_id"])


def downgrade() -> None:
    op.drop_index("ix_cases_guest_id", table_name="cases")
    op.drop_column("cases", "guest_id")
