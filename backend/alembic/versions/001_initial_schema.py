"""Initial application schema.

Revision ID: 001
Revises: 4
Create Date: 2026-03-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "crude_assays",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "case_id",
            sa.Integer(),
            sa.ForeignKey("cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("crude_name", sa.String(120), nullable=False),
        sa.Column("api_gravity", sa.Numeric(8, 3), nullable=True),
        sa.Column("sulfur_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("cost_per_bbl", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("min_volume", sa.Numeric(12, 2), server_default="0"),
        sa.Column("max_volume", sa.Numeric(12, 2), server_default="0"),
    )

    op.create_table(
        "crude_assay_cuts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "assay_id",
            sa.Integer(),
            sa.ForeignKey("crude_assays.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("cut_name", sa.String(120), nullable=False),
        sa.Column("yield_pct", sa.Numeric(8, 4), nullable=False, server_default="0"),
        sa.Column("density", sa.Numeric(8, 4), nullable=True),
        sa.Column("sulfur_pct", sa.Numeric(8, 4), nullable=True),
    )

    op.create_table(
        "process_units",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "case_id",
            sa.Integer(),
            sa.ForeignKey("cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("unit_type", sa.String(60), nullable=False),
        sa.Column("min_capacity", sa.Numeric(12, 2), server_default="0"),
        sa.Column("max_capacity", sa.Numeric(12, 2), server_default="0"),
        sa.Column("variable_cost_per_bbl", sa.Numeric(10, 2), server_default="0"),
    )

    op.create_table(
        "unit_yields",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "unit_id",
            sa.Integer(),
            sa.ForeignKey("process_units.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("input_stream", sa.String(120), nullable=False),
        sa.Column("output_stream", sa.String(120), nullable=False),
        sa.Column("yield_fraction", sa.Numeric(8, 5), nullable=False, server_default="0"),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "case_id",
            sa.Integer(),
            sa.ForeignKey("cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("price_per_bbl", sa.Numeric(10, 2), server_default="0"),
        sa.Column("min_demand", sa.Numeric(12, 2), server_default="0"),
        sa.Column("max_demand", sa.Numeric(12, 2), server_default="0"),
    )

    op.create_table(
        "product_blend_specs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("property_name", sa.String(60), nullable=False),
        sa.Column("min_value", sa.Numeric(10, 4), nullable=True),
        sa.Column("max_value", sa.Numeric(10, 4), nullable=True),
        sa.Column(
            "blend_type", sa.String(40), nullable=False, server_default="linear_volume"
        ),
    )

    op.create_table(
        "streams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "case_id",
            sa.Integer(),
            sa.ForeignKey("cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("stream_type", sa.String(40), nullable=False),
    )

    op.create_table(
        "optimization_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "case_id",
            sa.Integer(),
            sa.ForeignKey("cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(40), nullable=False, server_default="pending"),
        sa.Column("solver_name", sa.String(60), nullable=True),
        sa.Column("solve_time_ms", sa.Numeric(12, 2), nullable=True),
        sa.Column("objective_value", sa.Numeric(16, 4), nullable=True),
        sa.Column("solver_log", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("optimization_runs")
    op.drop_table("streams")
    op.drop_table("product_blend_specs")
    op.drop_table("products")
    op.drop_table("unit_yields")
    op.drop_table("process_units")
    op.drop_table("crude_assay_cuts")
    op.drop_table("crude_assays")
    op.drop_table("cases")
