from datetime import datetime

from pydantic import BaseModel


class CaseCreate(BaseModel):
    name: str
    description: str | None = None


class CaseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CaseRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
