from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    price_per_bbl: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    min_demand: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    max_demand: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    case: Mapped["Case"] = relationship(back_populates="products")  # noqa: F821
    blend_specs: Mapped[list["ProductBlendSpec"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )
    recipes: Mapped[list["ProductRecipe"]] = relationship(  # noqa: F821
        back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )


class ProductBlendSpec(Base):
    __tablename__ = "product_blend_specs"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    property_name: Mapped[str] = mapped_column(String(60), nullable=False)
    min_value: Mapped[float | None] = mapped_column(Numeric(10, 4), default=None)
    max_value: Mapped[float | None] = mapped_column(Numeric(10, 4), default=None)
    blend_type: Mapped[str] = mapped_column(
        String(40), nullable=False, default="linear_volume"
    )

    product: Mapped["Product"] = relationship(back_populates="blend_specs")
