from pydantic import BaseModel


# --- Crude Assay Cut ---

class CrudeAssayCutBase(BaseModel):
    cut_name: str
    yield_pct: float = 0
    density: float | None = None
    sulfur_pct: float | None = None


class CrudeAssayCutRead(CrudeAssayCutBase):
    id: int
    assay_id: int

    model_config = {"from_attributes": True}


# --- Crude Assay ---

class CrudeAssayCreate(BaseModel):
    crude_name: str
    api_gravity: float | None = None
    sulfur_pct: float | None = None
    cost_per_bbl: float = 0
    min_volume: float = 0
    max_volume: float = 0


class CrudeAssayUpdate(BaseModel):
    crude_name: str | None = None
    api_gravity: float | None = None
    sulfur_pct: float | None = None
    cost_per_bbl: float | None = None
    min_volume: float | None = None
    max_volume: float | None = None


class CrudeAssayRead(BaseModel):
    id: int
    case_id: int
    crude_name: str
    api_gravity: float | None
    sulfur_pct: float | None
    cost_per_bbl: float
    min_volume: float
    max_volume: float
    cuts: list[CrudeAssayCutRead] = []

    model_config = {"from_attributes": True}


# --- Bulk upsert for cuts ---

class CutsUpsert(BaseModel):
    cuts: list[CrudeAssayCutBase]
