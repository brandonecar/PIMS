"""Shared FastAPI dependencies."""

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from app.models.case import Case


def get_guest_id(x_guest_id: str = Header()) -> str:
    """Extract guest ID from the X-Guest-Id request header."""
    if not x_guest_id or len(x_guest_id) > 36:
        raise HTTPException(400, "Invalid or missing X-Guest-Id header")
    return x_guest_id


def verify_case_owner(case_id: int, guest_id: str, db: Session) -> Case:
    """Load a case and verify it belongs to the guest. Raises 404 if not."""
    case = db.get(Case, case_id)
    if not case or case.guest_id != guest_id:
        raise HTTPException(404, "Case not found")
    return case


def verify_entity_owner(entity, guest_id: str, db: Session, label: str = "Resource"):
    """Verify a child entity's parent case belongs to the guest.

    The entity must have a case_id attribute (crudes, units, products, streams)
    or be joinable to a case. Raises 404 if the entity doesn't exist or the
    parent case doesn't belong to the guest.
    """
    if entity is None:
        raise HTTPException(404, f"{label} not found")
    case = db.get(Case, entity.case_id)
    if not case or case.guest_id != guest_id:
        raise HTTPException(404, f"{label} not found")
    return entity
