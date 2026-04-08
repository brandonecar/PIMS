"""Build and solve the refinery LP for a given planning case."""

import time
from collections import defaultdict

from pulp import LpMaximize, LpProblem, LpVariable, lpSum, PULP_CBC_CMD


def _pick_solver():
    """Use HiGHS if highspy is importable, otherwise fall back to CBC."""
    try:
        import highspy  # noqa: F401
        from pulp import HiGHS
        return HiGHS(msg=0), "HiGHS"
    except (ImportError, Exception):
        return PULP_CBC_CMD(msg=0), "CBC"


_SOLVER, SOLVER_NAME = _pick_solver()

from app.solver.constraints import (
    add_cdu_capacity,
    add_unit_capacity,
    add_crude_cut_balance,
    add_intermediate_balance,
    add_product_demand,
    add_product_sulfur,
)
from app.solver.results_parser import parse_results


def solve_case(case):
    """Entry point: extract case data, build LP, solve, return structured results."""
    data = _extract_data(case)

    _empty = {
        "objective_value": None, "solve_time_ms": None,
        "crude_slate": [], "unit_throughputs": [], "product_outputs": [],
        "stream_flows": [],
        "margin": {"revenue": 0, "crude_cost": 0, "processing_cost": 0, "gross_margin": 0},
    }
    if not data["cdu"]:
        return {**_empty, "status": "error", "message": "No CDU found in case process units."}
    if not data["crudes"]:
        return {**_empty, "status": "error", "message": "No crudes defined for this case."}

    prob, ctx = _build_lp(data)

    start = time.perf_counter()
    prob.solve(_SOLVER)
    solve_ms = (time.perf_counter() - start) * 1000

    return parse_results(prob, ctx, solve_ms)


def _safe(name: str) -> str:
    """Sanitize a name for use as a PuLP variable identifier."""
    return name.replace(" ", "_").replace("/", "_").replace("-", "_")


def _extract_data(case) -> dict:
    """Pull ORM objects into plain dicts for LP construction."""
    crudes = []
    for assay in case.crude_assays:
        cuts = {}
        cut_sulfur = {}
        for cut in assay.cuts:
            cuts[cut.cut_name] = float(cut.yield_pct) / 100.0
            cut_sulfur[cut.cut_name] = float(cut.sulfur_pct) if cut.sulfur_pct else 0.0
        crudes.append({
            "name": assay.crude_name,
            "cost": float(assay.cost_per_bbl),
            "min_vol": float(assay.min_volume),
            "max_vol": float(assay.max_volume),
            "cuts": cuts,
            "cut_sulfur": cut_sulfur,
        })

    cdu = None
    units = []
    for unit in case.process_units:
        u = {
            "name": unit.name,
            "type": unit.unit_type,
            "min_cap": float(unit.min_capacity),
            "max_cap": float(unit.max_capacity),
            "var_cost": float(unit.variable_cost_per_bbl),
            "yields": [
                {"input": y.input_stream, "output": y.output_stream,
                 "fraction": float(y.yield_fraction),
                 "output_sulfur": float(y.output_sulfur_pct) if y.output_sulfur_pct else 0.0}
                for y in unit.yields
            ],
        }
        if unit.unit_type == "CDU":
            cdu = u
        else:
            units.append(u)

    products = []
    for prod in case.products:
        specs = {}
        for spec in prod.blend_specs:
            specs[spec.property_name] = {
                "min": float(spec.min_value) if spec.min_value is not None else None,
                "max": float(spec.max_value) if spec.max_value is not None else None,
            }
        products.append({
            "name": prod.name,
            "price": float(prod.price_per_bbl),
            "min_demand": float(prod.min_demand),
            "max_demand": float(prod.max_demand),
            "recipe_streams": [r.stream_name for r in prod.recipes],
            "specs": specs,
        })

    return {"crudes": crudes, "cdu": cdu, "units": units, "products": products}


def _build_lp(data: dict):
    """Construct the PuLP LP problem and return (problem, context)."""
    prob = LpProblem("refinery_plan", LpMaximize)

    crudes = data["crudes"]
    cdu = data["cdu"]
    units = data["units"]
    products = data["products"]

    # ── Decision variables ────────────────────────────────────

    # Crude purchase volumes (bbl)
    crude_vars = {}
    for c in crudes:
        crude_vars[c["name"]] = LpVariable(
            f"crude_{_safe(c['name'])}",
            lowBound=c["min_vol"],
            upBound=c["max_vol"] if c["max_vol"] > 0 else None,
        )

    # Stream-to-unit feed flows (bbl) — only valid (stream, unit) pairs
    unit_inputs = defaultdict(set)
    for u in units:
        for y in u["yields"]:
            unit_inputs[u["name"]].add(y["input"])

    to_unit = {}
    for u in units:
        for inp in unit_inputs[u["name"]]:
            key = (inp, u["name"])
            to_unit[key] = LpVariable(
                f"stu_{_safe(inp)}_{_safe(u['name'])}", lowBound=0,
            )

    # Stream-to-product allocation flows (bbl) — only valid pairs from recipes
    to_product = {}
    for p in products:
        for s in p["recipe_streams"]:
            key = (s, p["name"])
            to_product[key] = LpVariable(
                f"stp_{_safe(s)}_{_safe(p['name'])}", lowBound=0,
            )

    # ── Index sets ────────────────────────────────────────────

    # All crude cut stream names (produced by CDU fractionation)
    crude_cut_streams = set()
    for c in crudes:
        crude_cut_streams.update(c["cuts"].keys())

    # For each output stream, which (unit, input, fraction) tuples produce it
    output_producers = defaultdict(list)
    # Sulfur content of unit output streams (fixed values from yield data)
    unit_output_sulfur = {}
    for u in units:
        for y in u["yields"]:
            output_producers[y["output"]].append(
                (u["name"], y["input"], y["fraction"])
            )
            unit_output_sulfur[y["output"]] = y["output_sulfur"]

    # Per-stream consumption lookup
    stream_unit_keys = defaultdict(list)
    for key in to_unit:
        stream_unit_keys[key[0]].append(key)

    stream_product_keys = defaultdict(list)
    for key in to_product:
        stream_product_keys[key[0]].append(key)

    ctx = {
        "crude_vars": crude_vars,
        "to_unit": to_unit,
        "to_product": to_product,
        "crudes": crudes,
        "cdu": cdu,
        "units": units,
        "products": products,
        "unit_inputs": dict(unit_inputs),
        "output_producers": dict(output_producers),
        "crude_cut_streams": crude_cut_streams,
        "stream_unit_keys": dict(stream_unit_keys),
        "stream_product_keys": dict(stream_product_keys),
        "unit_output_sulfur": unit_output_sulfur,
    }

    # ── Objective: maximize gross margin ──────────────────────

    product_prices = {p["name"]: p["price"] for p in products}
    revenue = lpSum(
        var * product_prices[pname]
        for (_, pname), var in to_product.items()
    )

    crude_cost = lpSum(
        crude_vars[c["name"]] * c["cost"] for c in crudes
    )

    cdu_processing = lpSum(crude_vars.values()) * cdu["var_cost"]

    unit_var_costs = {u["name"]: u["var_cost"] for u in units}
    downstream_processing = lpSum(
        var * unit_var_costs[uname]
        for (_, uname), var in to_unit.items()
    )

    prob += revenue - crude_cost - cdu_processing - downstream_processing

    # ── Constraints ───────────────────────────────────────────

    add_cdu_capacity(prob, ctx)
    add_unit_capacity(prob, ctx)
    add_crude_cut_balance(prob, ctx)
    add_intermediate_balance(prob, ctx)
    add_product_demand(prob, ctx)
    add_product_sulfur(prob, ctx)

    return prob, ctx
