from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProductRecipe(Base):
    """Maps which streams are allowed to blend into a product.

    Each row says "this stream can flow into this product."
    The solver decides how much of each stream actually goes there.
    """

    __tablename__ = "product_recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    stream_name: Mapped[str] = mapped_column(String(120), nullable=False)

    product: Mapped["Product"] = relationship(back_populates="recipes")  # noqa: F821
