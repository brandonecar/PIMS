from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProcessUnit(Base):
    __tablename__ = "process_units"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    unit_type: Mapped[str] = mapped_column(String(60), nullable=False)
    min_capacity: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    max_capacity: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    variable_cost_per_bbl: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    case: Mapped["Case"] = relationship(back_populates="process_units")  # noqa: F821
    yields: Mapped[list["UnitYield"]] = relationship(
        back_populates="unit", cascade="all, delete-orphan", lazy="selectin"
    )


class UnitYield(Base):
    __tablename__ = "unit_yields"

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(
        ForeignKey("process_units.id", ondelete="CASCADE")
    )
    input_stream: Mapped[str] = mapped_column(String(120), nullable=False)
    output_stream: Mapped[str] = mapped_column(String(120), nullable=False)
    yield_fraction: Mapped[float] = mapped_column(Numeric(8, 5), nullable=False, default=0)
    output_sulfur_pct: Mapped[float | None] = mapped_column(Numeric(10, 6), default=0)

    unit: Mapped["ProcessUnit"] = relationship(back_populates="yields")
