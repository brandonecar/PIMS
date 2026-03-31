from pydantic import BaseModel


class StreamCreate(BaseModel):
    name: str
    stream_type: str  # crude_cut, intermediate, product


class StreamUpdate(BaseModel):
    name: str | None = None
    stream_type: str | None = None


class StreamRead(BaseModel):
    id: int
    case_id: int
    name: str
    stream_type: str

    model_config = {"from_attributes": True}
