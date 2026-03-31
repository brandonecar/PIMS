import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OptimizationRun(Base):
    """Stores metadata for solver runs tied to a refinery case."""

    __tablename__ = "optimization_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending")
    solver_name: Mapped[str | None] = mapped_column(String(60), default=None)
    solve_time_ms: Mapped[float | None] = mapped_column(Numeric(12, 2), default=None)
    objective_value: Mapped[float | None] = mapped_column(Numeric(16, 4), default=None)
    solver_log: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    case: Mapped["Case"] = relationship(back_populates="optimization_runs")  # noqa: F821
