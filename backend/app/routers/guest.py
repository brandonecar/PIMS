"""Guest workspace management."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_guest_id
from app.models.case import Case
from app.schemas.case import CaseRead
from app.seed.demo_refinery import seed

router = APIRouter(prefix="/api/guest", tags=["guest"])


@router.post("/reset", response_model=CaseRead)
def reset_workspace(
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    """Delete all cases for this guest and re-seed a fresh Demo Refinery."""
    cases = db.query(Case).filter(Case.guest_id == guest_id).all()
    for case in cases:
        db.delete(case)
    db.flush()

    case = seed(db, guest_id=guest_id)
    db.commit()
    db.refresh(case)
    return case
