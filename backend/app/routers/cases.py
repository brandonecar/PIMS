from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.case import Case
from app.models.crude import CrudeAssay, CrudeAssayCut
from app.models.unit import ProcessUnit, UnitYield
from app.models.product import Product, ProductBlendSpec
from app.models.product_recipe import ProductRecipe
from app.models.stream import Stream
from app.schemas.case import CaseCreate, CaseRead, CaseUpdate

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("", response_model=list[CaseRead])
def list_cases(db: Session = Depends(get_db)):
    return db.query(Case).order_by(Case.id).all()


@router.post("", response_model=CaseRead, status_code=201)
def create_case(body: CaseCreate, db: Session = Depends(get_db)):
    case = Case(name=body.name, description=body.description)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    return case


@router.put("/{case_id}", response_model=CaseRead)
def update_case(case_id: int, body: CaseUpdate, db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(case, field, value)
    db.commit()
    db.refresh(case)
    return case


@router.delete("/{case_id}", status_code=204)
def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    db.delete(case)
    db.commit()


@router.post("/{case_id}/clone", response_model=CaseRead, status_code=201)
def clone_case(case_id: int, db: Session = Depends(get_db)):
    """Deep-clone a case and all its children."""
    orig = db.get(Case, case_id)
    if not orig:
        raise HTTPException(404, "Case not found")

    new_case = Case(name=f"{orig.name} (copy)", description=orig.description)
    db.add(new_case)
    db.flush()  # get new_case.id

    # Clone crude assays + cuts
    for assay in orig.crude_assays:
        new_assay = CrudeAssay(
            case_id=new_case.id,
            crude_name=assay.crude_name,
            api_gravity=assay.api_gravity,
            sulfur_pct=assay.sulfur_pct,
            cost_per_bbl=assay.cost_per_bbl,
            min_volume=assay.min_volume,
            max_volume=assay.max_volume,
        )
        db.add(new_assay)
        db.flush()
        for cut in assay.cuts:
            db.add(CrudeAssayCut(
                assay_id=new_assay.id,
                cut_name=cut.cut_name,
                yield_pct=cut.yield_pct,
                density=cut.density,
                sulfur_pct=cut.sulfur_pct,
            ))

    # Clone process units + yields
    for unit in orig.process_units:
        new_unit = ProcessUnit(
            case_id=new_case.id,
            name=unit.name,
            unit_type=unit.unit_type,
            min_capacity=unit.min_capacity,
            max_capacity=unit.max_capacity,
            variable_cost_per_bbl=unit.variable_cost_per_bbl,
        )
        db.add(new_unit)
        db.flush()
        for y in unit.yields:
            db.add(UnitYield(
                unit_id=new_unit.id,
                input_stream=y.input_stream,
                output_stream=y.output_stream,
                yield_fraction=y.yield_fraction,
            ))

    # Clone products + blend specs
    for product in orig.products:
        new_product = Product(
            case_id=new_case.id,
            name=product.name,
            price_per_bbl=product.price_per_bbl,
            min_demand=product.min_demand,
            max_demand=product.max_demand,
        )
        db.add(new_product)
        db.flush()
        for spec in product.blend_specs:
            db.add(ProductBlendSpec(
                product_id=new_product.id,
                property_name=spec.property_name,
                min_value=spec.min_value,
                max_value=spec.max_value,
                blend_type=spec.blend_type,
            ))
        for recipe in product.recipes:
            db.add(ProductRecipe(
                product_id=new_product.id,
                stream_name=recipe.stream_name,
            ))

    # Clone streams
    for stream in orig.streams:
        db.add(Stream(
            case_id=new_case.id,
            name=stream.name,
            stream_type=stream.stream_type,
        ))

    db.commit()
    db.refresh(new_case)
    return new_case
