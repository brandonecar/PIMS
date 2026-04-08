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

export interface ProductRecipe {
  id: number;
  product_id: number;
  stream_name: string;
}

export interface Product {
  id: number;
  case_id: number;
  name: string;
  price_per_bbl: number;
  min_demand: number;
  max_demand: number;
  blend_specs: ProductBlendSpec[];
  recipes: ProductRecipe[];
}

// ── Stream ───────────────────────────────────────────────────
export interface Stream {
  id: number;
  case_id: number;
  name: string;
  stream_type: string;
}

// ── Solver Results ──────────────────────────────────────────
export interface CrudeSlateRow {
  crude: string;
  volume: number;
  cost_per_bbl: number;
  total_cost: number;
}

export interface UnitThroughputRow {
  unit: string;
  throughput: number;
  max_capacity: number;
  utilization_pct: number;
  processing_cost: number;
}

export interface ProductOutputRow {
  product: string;
  volume: number;
  price_per_bbl: number;
  revenue: number;
  sulfur_pct?: number;
  sulfur_max?: number;
}

export interface StreamFlowRow {
  stream: string;
  destination: string;
  flow_type: string;
  volume: number;
}

export interface MarginBreakdown {
  revenue: number;
  crude_cost: number;
  processing_cost: number;
  gross_margin: number;
}

export interface SolveResult {
  status: string;
  objective_value: number | null;
  solve_time_ms?: number;
  crude_slate: CrudeSlateRow[];
  unit_throughputs: UnitThroughputRow[];
  product_outputs: ProductOutputRow[];
  stream_flows: StreamFlowRow[];
  margin: MarginBreakdown;
}
