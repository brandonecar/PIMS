// ── Case ─────────────────────────────────────────────────────
export interface Case {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

// ── Crude Assay ──────────────────────────────────────────────
export interface CrudeAssayCut {
  id: number;
  assay_id: number;
  cut_name: string;
  yield_pct: number;
  density: number | null;
  sulfur_pct: number | null;
}

export interface CrudeAssay {
  id: number;
  case_id: number;
  crude_name: string;
  api_gravity: number | null;
  sulfur_pct: number | null;
  cost_per_bbl: number;
  min_volume: number;
  max_volume: number;
  cuts: CrudeAssayCut[];
}

// ── Process Unit ─────────────────────────────────────────────
export interface UnitYield {
  id: number;
  unit_id: number;
  input_stream: string;
  output_stream: string;
  yield_fraction: number;
}

export interface ProcessUnit {
  id: number;
  case_id: number;
  name: string;
  unit_type: string;
  min_capacity: number;
  max_capacity: number;
  variable_cost_per_bbl: number;
  yields: UnitYield[];
}

// ── Product ──────────────────────────────────────────────────
export interface ProductBlendSpec {
  id: number;
  product_id: number;
  property_name: string;
  min_value: number | null;
  max_value: number | null;
  blend_type: string;
}

export interface Product {
  id: number;
  case_id: number;
  name: string;
  price_per_bbl: number;
  min_demand: number;
  max_demand: number;
  blend_specs: ProductBlendSpec[];
}

// ── Stream ───────────────────────────────────────────────────
export interface Stream {
  id: number;
  case_id: number;
  name: string;
  stream_type: string;
}
