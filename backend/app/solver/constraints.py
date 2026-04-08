"""Constraint groups for the refinery planning LP.

Each function receives the PuLP problem and a context dict built by model_builder,
then adds one logical group of constraints to the problem.
"""

from pulp import lpSum


def _cname(s: str) -> str:
    """Sanitize a string for use in a PuLP constraint name."""
    return s.replace(" ", "_").replace("/", "_").replace("-", "_")


def add_cdu_capacity(prob, ctx):
    """CDU throughput (= total crude purchased) must respect CDU capacity bounds."""
    cdu = ctx["cdu"]
    total_crude = lpSum(ctx["crude_vars"].values())

    if cdu["min_cap"] > 0:
        prob += total_crude >= cdu["min_cap"], "cdu_min_capacity"
    if cdu["max_cap"] > 0:
        prob += total_crude <= cdu["max_cap"], "cdu_max_capacity"


def add_unit_capacity(prob, ctx):
    """Each downstream unit's total feed must respect its capacity bounds."""
    for u in ctx["units"]:
        inputs = ctx["unit_inputs"].get(u["name"], set())
        if not inputs:
            continue

        throughput = lpSum(ctx["to_unit"][(inp, u["name"])] for inp in inputs)

        if u["min_cap"] > 0:
            prob += throughput >= u["min_cap"], f"unit_min_{_cname(u['name'])}"
        if u["max_cap"] > 0:
            prob += throughput <= u["max_cap"], f"unit_max_{_cname(u['name'])}"


def add_crude_cut_balance(prob, ctx):
    """For each crude cut stream: total CDU production = total outgoing flows.

    Production of cut k = sum over crudes c: crude[c] * yield[c, k].
    Consumption = whatever goes to downstream units + whatever goes to products.
    """
    for stream in ctx["crude_cut_streams"]:
        supply = lpSum(
            ctx["crude_vars"][c["name"]] * c["cuts"].get(stream, 0)
            for c in ctx["crudes"]
        )

        demand_terms = []
        for key in ctx["stream_unit_keys"].get(stream, []):
            demand_terms.append(ctx["to_unit"][key])
        for key in ctx["stream_product_keys"].get(stream, []):
            demand_terms.append(ctx["to_product"][key])

        prob += supply == lpSum(demand_terms), f"cut_bal_{_cname(stream)}"


def add_intermediate_balance(prob, ctx):
    """For each intermediate stream produced by downstream units:
    total unit output = total outgoing flows.

    Production of stream s = sum over (unit, input) that produce s:
        stream_to_unit[input, unit] * yield_fraction.
    """
    for stream, producers in ctx["output_producers"].items():
        if stream in ctx["crude_cut_streams"]:
            continue

        supply = lpSum(
            ctx["to_unit"][(inp, unit)] * frac
            for unit, inp, frac in producers
        )

        demand_terms = []
        for key in ctx["stream_unit_keys"].get(stream, []):
            demand_terms.append(ctx["to_unit"][key])
        for key in ctx["stream_product_keys"].get(stream, []):
            demand_terms.append(ctx["to_product"][key])

        prob += supply == lpSum(demand_terms), f"int_bal_{_cname(stream)}"


def add_product_demand(prob, ctx):
    """Each product's total volume must respect min/max demand bounds."""
    for p in ctx["products"]:
        recipe_keys = [
            (s, p["name"]) for s in p["recipe_streams"]
            if (s, p["name"]) in ctx["to_product"]
        ]
        if not recipe_keys:
            continue

        volume = lpSum(ctx["to_product"][k] for k in recipe_keys)

        if p["min_demand"] > 0:
            prob += volume >= p["min_demand"], f"dem_min_{_cname(p['name'])}"
        if p["max_demand"] > 0:
            prob += volume <= p["max_demand"], f"dem_max_{_cname(p['name'])}"


def add_product_sulfur(prob, ctx):
    """Enforce sulfur blend specs on products.

    For each product with a sulfur max spec:
        Σ(flow_i × sulfur_i) ≤ max_sulfur × Σ(flow_i)

    Sulfur values come from two sources:
    - Crude cut streams: weighted-average sulfur across crudes (v1 approximation)
    - Unit output streams: fixed output_sulfur_pct from unit_yields
    """
    crude_cut_streams = ctx["crude_cut_streams"]
    unit_output_sulfur = ctx["unit_output_sulfur"]

    # Pre-compute weighted-average sulfur for each crude cut stream.
    # avg_sulfur[cut] = Σ(crude_vol * yield * sulfur) / Σ(crude_vol * yield)
    # This is approximate — uses crude volumes as if they were known, but they're
    # decision variables. A proper formulation would split per-crude flows.
    # For v1 this is acceptable; crude mixes don't vary wildly in practice.
    # We compute a static estimate using midpoint of each crude's volume range.
    crude_cut_sulfur = {}
    for stream in crude_cut_streams:
        weighted_s = 0.0
        total_w = 0.0
        for c in ctx["crudes"]:
            yld = c["cuts"].get(stream, 0)
            if yld <= 0:
                continue
            mid_vol = (c["min_vol"] + c["max_vol"]) / 2.0 if c["max_vol"] > 0 else 1.0
            w = mid_vol * yld
            weighted_s += w * c["cut_sulfur"].get(stream, 0)
            total_w += w
        crude_cut_sulfur[stream] = weighted_s / total_w if total_w > 0 else 0.0

    for p in ctx["products"]:
        sulfur_spec = p["specs"].get("sulfur")
        if not sulfur_spec:
            continue
        max_sulfur = sulfur_spec["max"]
        if max_sulfur is None:
            continue

        recipe_keys = [
            (s, p["name"]) for s in p["recipe_streams"]
            if (s, p["name"]) in ctx["to_product"]
        ]
        if not recipe_keys:
            continue

        # Build: Σ(flow * sulfur) ≤ max_sulfur × Σ(flow)
        # Rearranged: Σ(flow * (sulfur - max_sulfur)) ≤ 0
        sulfur_terms = []
        for (stream, _pname) in recipe_keys:
            var = ctx["to_product"][(stream, _pname)]
            if stream in crude_cut_streams:
                s_val = crude_cut_sulfur.get(stream, 0)
            else:
                s_val = unit_output_sulfur.get(stream, 0)
            sulfur_terms.append(var * (s_val - max_sulfur))

        prob += lpSum(sulfur_terms) <= 0, f"sulfur_max_{_cname(p['name'])}"
