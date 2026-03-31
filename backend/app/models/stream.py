from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Stream(Base):
    __tablename__ = "streams"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    stream_type: Mapped[str] = mapped_column(String(40), nullable=False)
    # stream_type: "crude_cut", "intermediate", "product"

    case: Mapped["Case"] = relationship(back_populates="streams")  # noqa: F821
