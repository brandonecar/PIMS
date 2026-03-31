from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product, ProductBlendSpec
from app.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ProductBlendSpecRead,
    BlendSpecsUpsert,
)

router = APIRouter(tags=["products"])


# ── Products ──────────────────────────────────────────────────

@router.get("/api/cases/{case_id}/products", response_model=list[ProductRead])
def list_products(case_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Product)
        .filter(Product.case_id == case_id)
        .order_by(Product.id)
        .all()
    )


@router.post("/api/cases/{case_id}/products", response_model=ProductRead, status_code=201)
def create_product(case_id: int, body: ProductCreate, db: Session = Depends(get_db)):
    product = Product(case_id=case_id, **body.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/api/products/{product_id}", response_model=ProductRead)
def update_product(product_id: int, body: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/api/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    db.delete(product)
    db.commit()


# ── Blend Specs (bulk upsert) ────────────────────────────────

@router.get(
    "/api/products/{product_id}/specs", response_model=list[ProductBlendSpecRead]
)
def list_blend_specs(product_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ProductBlendSpec)
        .filter(ProductBlendSpec.product_id == product_id)
        .order_by(ProductBlendSpec.id)
        .all()
    )


@router.put(
    "/api/products/{product_id}/specs", response_model=list[ProductBlendSpecRead]
)
def upsert_blend_specs(
    product_id: int, body: BlendSpecsUpsert, db: Session = Depends(get_db)
):
    """Replace all blend specs for this product with the provided set."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    db.query(ProductBlendSpec).filter(
        ProductBlendSpec.product_id == product_id
    ).delete()

    new_specs = []
    for s in body.specs:
        spec = ProductBlendSpec(product_id=product_id, **s.model_dump())
        db.add(spec)
        new_specs.append(spec)

    db.commit()
    for spec in new_specs:
        db.refresh(spec)
    return new_specs
