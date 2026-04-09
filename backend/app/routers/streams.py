from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_guest_id, verify_case_owner, verify_entity_owner
from app.models.stream import Stream
from app.schemas.stream import StreamCreate, StreamRead, StreamUpdate

router = APIRouter(tags=["streams"])


@router.get("/api/cases/{case_id}/streams", response_model=list[StreamRead])
def list_streams(
    case_id: int,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    verify_case_owner(case_id, guest_id, db)
    return (
        db.query(Stream)
        .filter(Stream.case_id == case_id)
        .order_by(Stream.id)
        .all()
    )


@router.post(
    "/api/cases/{case_id}/streams", response_model=StreamRead, status_code=201
)
def create_stream(
    case_id: int,
    body: StreamCreate,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    verify_case_owner(case_id, guest_id, db)
    stream = Stream(case_id=case_id, **body.model_dump())
    db.add(stream)
    db.commit()
    db.refresh(stream)
    return stream


@router.put("/api/streams/{stream_id}", response_model=StreamRead)
def update_stream(
    stream_id: int,
    body: StreamUpdate,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    stream = db.get(Stream, stream_id)
    verify_entity_owner(stream, guest_id, db, "Stream")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(stream, field, value)
    db.commit()
    db.refresh(stream)
    return stream


@router.delete("/api/streams/{stream_id}", status_code=204)
def delete_stream(
    stream_id: int,
    guest_id: str = Depends(get_guest_id),
    db: Session = Depends(get_db),
):
    stream = db.get(Stream, stream_id)
    verify_entity_owner(stream, guest_id, db, "Stream")
    db.delete(stream)
    db.commit()
