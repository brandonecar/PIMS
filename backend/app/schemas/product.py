from pydantic import BaseModel


# --- Blend Spec ---

class ProductBlendSpecBase(BaseModel):
    property_name: str
    min_value: float | None = None
    max_value: float | None = None
    blend_type: str = "linear_volume"


class ProductBlendSpecRead(ProductBlendSpecBase):
    id: int
    product_id: int

    model_config = {"from_attributes": True}


# --- Product ---

class ProductCreate(BaseModel):
    name: str
    price_per_bbl: float = 0
    min_demand: float = 0
    max_demand: float = 0


class ProductUpdate(BaseModel):
    name: str | None = None
    price_per_bbl: float | None = None
    min_demand: float | None = None
    max_demand: float | None = None


class ProductRead(BaseModel):
    id: int
    case_id: int
    name: str
    price_per_bbl: float
    min_demand: float
    max_demand: float
    blend_specs: list[ProductBlendSpecRead] = []

    model_config = {"from_attributes": True}


# --- Bulk upsert for blend specs ---

class BlendSpecsUpsert(BaseModel):
    specs: list[ProductBlendSpecBase]
