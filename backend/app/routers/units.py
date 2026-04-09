from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_guest_id, verify_case_owner, verify_entity_owner
from app.models.unit import ProcessUnit, UnitYield
from app.schemas.unit import (
    ProcessUnitCreate,
    ProcessUnitRead,
    ProcessUnitUpdate,
    UnitYieldRead,
    YieldsUpsert,
)

router = APIRouter(tags=["units"])


# ── Process Units ─────────────────────────────────────────────

@router.get("/api/cases/{case_id}/units", response_model=list[ProcessUnitRead])
def list_units(
    case_id: int,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    verify_case_owner(case_id, guest_id, db)
    return (
        db.query(ProcessUnit)
        .filter(ProcessUnit.case_id == case_id)
        .order_by(ProcessUnit.id)
        .all()
    )


@router.post("/api/cases/{case_id}/units", response_model=ProcessUnitRead, status_code=201)
def create_unit(
    case_id: int,
    body: ProcessUnitCreate,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    verify_case_owner(case_id, guest_id, db)
    unit = ProcessUnit(case_id=case_id, **body.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@router.put("/api/units/{unit_id}", response_model=ProcessUnitRead)
def update_unit(
    unit_id: int,
    body: ProcessUnitUpdate,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    unit = db.get(ProcessUnit, unit_id)
    verify_entity_owner(unit, guest_id, db, "Process unit")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(unit, field, value)
    db.commit()
    db.refresh(unit)
    return unit


@router.delete("/api/units/{unit_id}", status_code=204)
def delete_unit(
    unit_id: int,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    unit = db.get(ProcessUnit, unit_id)
    verify_entity_owner(unit, guest_id, db, "Process unit")
    db.delete(unit)
    db.commit()


# ── Unit Yields (bulk upsert) ────────────────────────────────

@router.get("/api/units/{unit_id}/yields", response_model=list[UnitYieldRead])
def list_yields(
    unit_id: int,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    unit = db.get(ProcessUnit, unit_id)
    verify_entity_owner(unit, guest_id, db, "Process unit")
    return (
        db.query(UnitYield)
        .filter(UnitYield.unit_id == unit_id)
        .order_by(UnitYield.id)
        .all()
    )


@router.put("/api/units/{unit_id}/yields", response_model=list[UnitYieldRead])
def upsert_yields(
    unit_id: int,
    body: YieldsUpsert,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    """Replace all yields for this unit with the provided set."""
    unit = db.get(ProcessUnit, unit_id)
    verify_entity_owner(unit, guest_id, db, "Process unit")

    db.query(UnitYield).filter(UnitYield.unit_id == unit_id).delete()

    new_yields = []
    for y in body.yields:
        yld = UnitYield(unit_id=unit_id, **y.model_dump())
        db.add(yld)
        new_yields.append(yld)

    db.commit()
    for yld in new_yields:
        db.refresh(yld)
    return new_yields
