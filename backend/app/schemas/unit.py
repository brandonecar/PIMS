from pydantic import BaseModel


# --- Unit Yield ---

class UnitYieldBase(BaseModel):
    input_stream: str
    output_stream: str
    yield_fraction: float = 0


class UnitYieldRead(UnitYieldBase):
    id: int
    unit_id: int

    model_config = {"from_attributes": True}


# --- Process Unit ---

class ProcessUnitCreate(BaseModel):
    name: str
    unit_type: str
    min_capacity: float = 0
    max_capacity: float = 0
    variable_cost_per_bbl: float = 0


class ProcessUnitUpdate(BaseModel):
    name: str | None = None
    unit_type: str | None = None
    min_capacity: float | None = None
    max_capacity: float | None = None
    variable_cost_per_bbl: float | None = None


class ProcessUnitRead(BaseModel):
    id: int
    case_id: int
    name: str
    unit_type: str
    min_capacity: float
    max_capacity: float
    variable_cost_per_bbl: float
    yields: list[UnitYieldRead] = []

    model_config = {"from_attributes": True}


# --- Bulk upsert for yields ---

class YieldsUpsert(BaseModel):
    yields: list[UnitYieldBase]
