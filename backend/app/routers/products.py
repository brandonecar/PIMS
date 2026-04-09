from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_guest_id, verify_case_owner, verify_entity_owner
from app.models.product import Product, ProductBlendSpec
from app.models.product_recipe import ProductRecipe
from app.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ProductBlendSpecRead,
    BlendSpecsUpsert,
    ProductRecipeRead,
    RecipesUpsert,
)

router = APIRouter(tags=["products"])


def _get_product(product_id: int, guest_id: str, db: Session) -> Product:
    product = db.get(Product, product_id)
    verify_entity_owner(product, guest_id, db, "Product")
    return product


# ── Products ──────────────────────────────────────────────────

@router.get("/api/cases/{case_id}/products", response_model=list[ProductRead])
def list_products(
    case_id: int,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    verify_case_owner(case_id, guest_id, db)
    return (
        db.query(Product)
        .filter(Product.case_id == case_id)
        .order_by(Product.id)
        .all()
    )


@router.post("/api/cases/{case_id}/products", response_model=ProductRead, status_code=201)
def create_product(
    case_id: int,
    body: ProductCreate,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    verify_case_owner(case_id, guest_id, db)
    product = Product(case_id=case_id, **body.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/api/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    body: ProductUpdate,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    product = _get_product(product_id, guest_id, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/api/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    product = _get_product(product_id, guest_id, db)
    db.delete(product)
    db.commit()


# ── Blend Specs (bulk upsert) ────────────────────────────────

@router.get(
    "/api/products/{product_id}/specs", response_model=list[ProductBlendSpecRead]
)
def list_blend_specs(
    product_id: int,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    _get_product(product_id, guest_id, db)
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
    product_id: int,
    body: BlendSpecsUpsert,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    """Replace all blend specs for this product with the provided set."""
    _get_product(product_id, guest_id, db)

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


# ── Product Recipes (bulk upsert) ───────────────────────────

@router.get(
    "/api/products/{product_id}/recipes", response_model=list[ProductRecipeRead]
)
def list_recipes(
    product_id: int,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    _get_product(product_id, guest_id, db)
    return (
        db.query(ProductRecipe)
        .filter(ProductRecipe.product_id == product_id)
        .order_by(ProductRecipe.id)
        .all()
    )


@router.put(
    "/api/products/{product_id}/recipes", response_model=list[ProductRecipeRead]
)
def upsert_recipes(
    product_id: int,
    body: RecipesUpsert,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    """Replace all recipes for this product with the provided set."""
    _get_product(product_id, guest_id, db)

    db.query(ProductRecipe).filter(
        ProductRecipe.product_id == product_id
    ).delete()

    new_recipes = []
    for r in body.recipes:
        recipe = ProductRecipe(product_id=product_id, **r.model_dump())
        db.add(recipe)
        new_recipes.append(recipe)

    db.commit()
    for recipe in new_recipes:
        db.refresh(recipe)
    return new_recipes
