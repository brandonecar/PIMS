from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CrudeAssay(Base):
    __tablename__ = "crude_assays"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    crude_name: Mapped[str] = mapped_column(String(120), nullable=False)
    api_gravity: Mapped[float | None] = mapped_column(Numeric(8, 3), default=None)
    sulfur_pct: Mapped[float | None] = mapped_column(Numeric(8, 4), default=None)
    cost_per_bbl: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    min_volume: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    max_volume: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    case: Mapped["Case"] = relationship(back_populates="crude_assays")  # noqa: F821
    cuts: Mapped[list["CrudeAssayCut"]] = relationship(
        back_populates="assay", cascade="all, delete-orphan", lazy="selectin"
    )


class CrudeAssayCut(Base):
    __tablename__ = "crude_assay_cuts"

    id: Mapped[int] = mapped_column(primary_key=True)
    assay_id: Mapped[int] = mapped_column(
        ForeignKey("crude_assays.id", ondelete="CASCADE")
    )
    cut_name: Mapped[str] = mapped_column(String(120), nullable=False)
    yield_pct: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    density: Mapped[float | None] = mapped_column(Numeric(8, 4), default=None)
    sulfur_pct: Mapped[float | None] = mapped_column(Numeric(8, 4), default=None)

    assay: Mapped["CrudeAssay"] = relationship(back_populates="cuts")
