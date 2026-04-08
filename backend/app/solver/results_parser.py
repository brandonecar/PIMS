"""Extract structured results from a solved PuLP refinery LP."""

from pulp import LpStatus, value


def parse_results(prob, ctx, solve_time_ms: float) -> dict:
    """Read variable values from a solved problem and return a result dict."""
    status = LpStatus[prob.status]

    if status != "Optimal":
        return {
            "status": status,
            "objective_value": None,
            "solve_time_ms": round(solve_time_ms, 1),
            "crude_slate": [],
            "unit_throughputs": [],
            "product_outputs": [],
            "stream_flows": [],
            "margin": {
                "revenue": 0,
                "crude_cost": 0,
                "processing_cost": 0,
                "gross_margin": 0,
            },
        }

    obj = value(prob.objective)

    # ── Crude slate ────────────────────────────────���──────────

    crude_slate = []
    total_crude_cost = 0.0
    for c in ctx["crudes"]:
        vol = value(ctx["crude_vars"][c["name"]]) or 0.0
        cost = vol * c["cost"]
        total_crude_cost += cost
        crude_slate.append({
            "crude": c["name"],
            "volume": round(vol, 1),
            "cost_per_bbl": c["cost"],
            "total_cost": round(cost, 2),
        })

    # ── Unit throughputs ──────────────────────────────────────

    unit_throughputs = []
    total_processing_cost = 0.0

    # CDU (throughput = total crude purchased)
    cdu = ctx["cdu"]
    cdu_throughput = sum(
        (value(ctx["crude_vars"][c["name"]]) or 0.0) for c in ctx["crudes"]
    )
    cdu_cost = cdu_throughput * cdu["var_cost"]
    total_processing_cost += cdu_cost
    unit_throughputs.append(_unit_row(cdu, cdu_throughput, cdu_cost))

    # Downstream units
    for u in ctx["units"]:
        inputs = ctx["unit_inputs"].get(u["name"], set())
        throughput = sum(
            (value(ctx["to_unit"][(inp, u["name"])]) or 0.0) for inp in inputs
        )
        cost = throughput * u["var_cost"]
        total_processing_cost += cost
        unit_throughputs.append(_unit_row(u, throughput, cost))

    # ── Product outputs ─────────────────────────────────��─────

    product_outputs = []
    total_revenue = 0.0
    crude_cut_streams = ctx["crude_cut_streams"]
    unit_output_sulfur = ctx.get("unit_output_sulfur", {})

    # Compute crude cut sulfur (same midpoint approximation as constraints)
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
            weighted_s += w * c.get("cut_sulfur", {}).get(stream, 0)
            total_w += w
        crude_cut_sulfur[stream] = weighted_s / total_w if total_w > 0 else 0.0

    for p in ctx["products"]:
        recipe_keys = [
            (s, p["name"]) for s in p["recipe_streams"]
            if (s, p["name"]) in ctx["to_product"]
        ]
        vol = sum(
            (value(ctx["to_product"][k]) or 0.0) for k in recipe_keys
        )
        rev = vol * p["price"]
        total_revenue += rev

        # Compute blended sulfur for this product
        sulfur_num = 0.0
        sulfur_den = 0.0
        for (stream, _pname) in recipe_keys:
            sv = value(ctx["to_product"][(stream, _pname)]) or 0.0
            if sv > 0:
                if stream in crude_cut_streams:
                    s_val = crude_cut_sulfur.get(stream, 0)
                else:
                    s_val = unit_output_sulfur.get(stream, 0)
                sulfur_num += sv * s_val
                sulfur_den += sv
        blended_sulfur = sulfur_num / sulfur_den if sulfur_den > 0 else 0.0

        row = {
            "product": p["name"],
            "volume": round(vol, 1),
            "price_per_bbl": p["price"],
            "revenue": round(rev, 2),
        }
        sulfur_spec = p.get("specs", {}).get("sulfur")
        if sulfur_spec and sulfur_spec.get("max") is not None:
            row["sulfur_pct"] = round(blended_sulfur, 6)
            row["sulfur_max"] = sulfur_spec["max"]
        product_outputs.append(row)

    # ── Stream flows (all non-trivial material movements) ─────

    stream_flows = []

    for (stream, unit), var in ctx["to_unit"].items():
        vol = value(var) or 0.0
        if vol > 0.5:
            stream_flows.append({
                "stream": stream,
                "destination": unit,
                "flow_type": "unit_feed",
                "volume": round(vol, 1),
            })

    for (stream, product), var in ctx["to_product"].items():
        vol = value(var) or 0.0
        if vol > 0.5:
            stream_flows.append({
                "stream": stream,
                "destination": product,
                "flow_type": "product_blend",
                "volume": round(vol, 1),
            })

    # ── Margin breakdown ──────────────────────────────────────

    gross_margin = total_revenue - total_crude_cost - total_processing_cost
    margin = {
        "revenue": round(total_revenue, 2),
        "crude_cost": round(total_crude_cost, 2),
        "processing_cost": round(total_processing_cost, 2),
        "gross_margin": round(gross_margin, 2),
    }

    return {
        "status": status,
        "objective_value": round(obj, 2),
        "solve_time_ms": round(solve_time_ms, 1),
        "crude_slate": crude_slate,
        "unit_throughputs": unit_throughputs,
        "product_outputs": product_outputs,
        "stream_flows": stream_flows,
        "margin": margin,
    }


def _unit_row(unit: dict, throughput: float, cost: float) -> dict:
    max_cap = unit["max_cap"]
    return {
        "unit": unit["name"],
        "throughput": round(throughput, 1),
        "max_capacity": max_cap,
        "utilization_pct": round(throughput / max_cap * 100, 1) if max_cap else 0.0,
        "processing_cost": round(cost, 2),
    }
