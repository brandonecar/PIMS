import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # relationships
    crude_assays: Mapped[list["CrudeAssay"]] = relationship(  # noqa: F821
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    process_units: Mapped[list["ProcessUnit"]] = relationship(  # noqa: F821
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    products: Mapped[list["Product"]] = relationship(  # noqa: F821
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    streams: Mapped[list["Stream"]] = relationship(  # noqa: F821
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    optimization_runs: Mapped[list["OptimizationRun"]] = relationship(  # noqa: F821
        back_populates="case", cascade="all, delete-orphan", lazy="select"
    )
