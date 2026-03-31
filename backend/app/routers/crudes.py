from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.crude import CrudeAssay, CrudeAssayCut
from app.schemas.crude import (
    CrudeAssayCreate,
    CrudeAssayRead,
    CrudeAssayUpdate,
    CrudeAssayCutRead,
    CutsUpsert,
)

router = APIRouter(tags=["crudes"])


# ── Crude Assays ──────────────────────────────────────────────

@router.get("/api/cases/{case_id}/crudes", response_model=list[CrudeAssayRead])
def list_crudes(case_id: int, db: Session = Depends(get_db)):
    return (
        db.query(CrudeAssay)
        .filter(CrudeAssay.case_id == case_id)
        .order_by(CrudeAssay.id)
        .all()
    )


@router.post("/api/cases/{case_id}/crudes", response_model=CrudeAssayRead, status_code=201)
def create_crude(case_id: int, body: CrudeAssayCreate, db: Session = Depends(get_db)):
    assay = CrudeAssay(case_id=case_id, **body.model_dump())
    db.add(assay)
    db.commit()
    db.refresh(assay)
    return assay


@router.put("/api/crudes/{crude_id}", response_model=CrudeAssayRead)
def update_crude(crude_id: int, body: CrudeAssayUpdate, db: Session = Depends(get_db)):
    assay = db.get(CrudeAssay, crude_id)
    if not assay:
        raise HTTPException(404, "Crude assay not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(assay, field, value)
    db.commit()
    db.refresh(assay)
    return assay


@router.delete("/api/crudes/{crude_id}", status_code=204)
def delete_crude(crude_id: int, db: Session = Depends(get_db)):
    assay = db.get(CrudeAssay, crude_id)
    if not assay:
        raise HTTPException(404, "Crude assay not found")
    db.delete(assay)
    db.commit()


# ── Crude Assay Cuts (bulk upsert) ───────────────────────────

@router.get("/api/crudes/{crude_id}/cuts", response_model=list[CrudeAssayCutRead])
def list_cuts(crude_id: int, db: Session = Depends(get_db)):
    return (
        db.query(CrudeAssayCut)
        .filter(CrudeAssayCut.assay_id == crude_id)
        .order_by(CrudeAssayCut.id)
        .all()
    )


@router.put("/api/crudes/{crude_id}/cuts", response_model=list[CrudeAssayCutRead])
def upsert_cuts(crude_id: int, body: CutsUpsert, db: Session = Depends(get_db)):
    """Replace all cuts for this crude with the provided set."""
    assay = db.get(CrudeAssay, crude_id)
    if not assay:
        raise HTTPException(404, "Crude assay not found")

    # Delete existing cuts
    db.query(CrudeAssayCut).filter(CrudeAssayCut.assay_id == crude_id).delete()

    # Insert new cuts
    new_cuts = []
    for c in body.cuts:
        cut = CrudeAssayCut(assay_id=crude_id, **c.model_dump())
        db.add(cut)
        new_cuts.append(cut)

    db.commit()
    for cut in new_cuts:
        db.refresh(cut)
    return new_cuts
