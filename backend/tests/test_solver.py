"""Tests for the refinery planning solver.

These test the solver logic directly using mock objects that match
the ORM shape, without requiring a database connection.
"""

import pytest

from app.solver.model_builder import solve_case


class Obj:
    """Minimal mock for ORM objects — sets attributes from kwargs."""

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def _build_demo_case():
    """Build a mock case matching the seeded demo refinery."""
    crudes_raw = [
        ("Arab Light", 72.0, 0, 50000, [
            ("Light Naphtha", 7.5, 0.0005), ("Heavy Naphtha", 11.0, 0.001),
            ("Kerosene", 14.0, 0.05), ("Light Gas Oil", 16.5, 0.80),
            ("Heavy Gas Oil", 12.0, 1.80), ("Atmospheric Residue", 39.0, 3.50),
        ]),
        ("Brent", 78.0, 0, 40000, [
            ("Light Naphtha", 10.0, 0.0002), ("Heavy Naphtha", 14.0, 0.0005),
            ("Kerosene", 16.0, 0.02), ("Light Gas Oil", 18.0, 0.15),
            ("Heavy Gas Oil", 10.0, 0.40), ("Atmospheric Residue", 32.0, 0.90),
        ]),
        ("WTI", 75.0, 0, 45000, [
            ("Light Naphtha", 11.0, 0.0001), ("Heavy Naphtha", 15.0, 0.0003),
            ("Kerosene", 15.5, 0.01), ("Light Gas Oil", 17.5, 0.10),
            ("Heavy Gas Oil", 9.5, 0.30), ("Atmospheric Residue", 31.5, 0.60),
        ]),
    ]
    assays = []
    for name, cost, mn, mx, cuts in crudes_raw:
        cut_objs = [Obj(cut_name=c, yield_pct=y, density=0.8, sulfur_pct=s) for c, y, s in cuts]
        assays.append(Obj(crude_name=name, cost_per_bbl=cost,
                          min_volume=mn, max_volume=mx,
                          api_gravity=35.0, sulfur_pct=1.0, cuts=cut_objs))

    units_raw = [
        ("CDU", "CDU", 10000, 100000, 1.50, []),
        ("VDU", "VDU", 5000, 50000, 1.20, [
            ("Atmospheric Residue", "Vacuum Gas Oil", 0.55, 1.20),
            ("Atmospheric Residue", "Vacuum Residue", 0.45, 2.50),
        ]),
        ("FCC", "FCC", 5000, 40000, 3.00, [
            ("Vacuum Gas Oil", "FCC Gasoline", 0.50, 0.05),
            ("Vacuum Gas Oil", "FCC Light Cycle Oil", 0.20, 0.80),
            ("Vacuum Gas Oil", "FCC Slurry", 0.10, 1.50),
            ("Vacuum Gas Oil", "LPG", 0.15, 0.001),
        ]),
        ("Reformer", "Reformer", 3000, 25000, 2.50, [
            ("Heavy Naphtha", "Reformate", 0.85, 0.0001),
            ("Heavy Naphtha", "LPG", 0.10, 0.001),
        ]),
        ("Hydrotreater", "Hydrotreater", 3000, 30000, 1.80, [
            ("Light Gas Oil", "Hydrotreated Diesel", 0.97, 0.005),
            ("FCC Light Cycle Oil", "Hydrotreated Diesel", 0.95, 0.005),
        ]),
    ]
    process_units = []
    for name, utype, mn, mx, cost, yields in units_raw:
        yobjs = [Obj(input_stream=i, output_stream=o, yield_fraction=f,
                      output_sulfur_pct=s) for i, o, f, s in yields]
        process_units.append(Obj(name=name, unit_type=utype,
                                 min_capacity=mn, max_capacity=mx,
                                 variable_cost_per_bbl=cost, yields=yobjs))

    products_raw = [
        ("Gasoline", 95.0, 5000, 50000, ["Light Naphtha", "FCC Gasoline", "Reformate"],
         [("sulfur", None, 0.10)]),
        ("Jet Fuel", 92.0, 3000, 25000, ["Kerosene"],
         [("sulfur", None, 0.30)]),
        ("Diesel", 90.0, 5000, 40000, ["Hydrotreated Diesel", "Light Gas Oil"],
         [("sulfur", None, 0.05)]),
        ("Fuel Oil", 60.0, 0, 30000, ["Vacuum Residue", "FCC Slurry", "Heavy Gas Oil"],
         [("sulfur", None, 3.50)]),
        ("LPG", 45.0, 0, 15000, ["LPG"], []),
        ("Naphtha", 70.0, 0, 20000, ["Light Naphtha", "Heavy Naphtha"], []),
    ]
    products = []
    for name, price, mn, mx, streams, specs in products_raw:
        recipes = [Obj(stream_name=s) for s in streams]
        spec_objs = [Obj(property_name=pn, min_value=lo, max_value=hi,
                         blend_type="linear_volume") for pn, lo, hi in specs]
        products.append(Obj(name=name, price_per_bbl=price,
                            min_demand=mn, max_demand=mx,
                            recipes=recipes, blend_specs=spec_objs))

    return Obj(crude_assays=assays, process_units=process_units, products=products)


class TestSolverDemoCase:
    """Verify the demo refinery case produces a sensible optimal solution."""

    @pytest.fixture()
    def result(self):
        case = _build_demo_case()
        return solve_case(case)

    def test_status_optimal(self, result):
        assert result["status"] == "Optimal"

    def test_positive_margin(self, result):
        assert result["margin"]["gross_margin"] > 0

    def test_revenue_exceeds_cost(self, result):
        m = result["margin"]
        assert m["revenue"] > m["crude_cost"] + m["processing_cost"]

    def test_crude_slate_present(self, result):
        assert len(result["crude_slate"]) == 3
        total_vol = sum(c["volume"] for c in result["crude_slate"])
        assert total_vol >= 10000  # CDU min capacity

    def test_product_outputs_present(self, result):
        assert len(result["product_outputs"]) == 6
        total_vol = sum(p["volume"] for p in result["product_outputs"])
        assert total_vol > 0

    def test_material_balance(self, result):
        """Total product volume should be less than total crude (yield losses)."""
        crude_vol = sum(c["volume"] for c in result["crude_slate"])
        product_vol = sum(p["volume"] for p in result["product_outputs"])
        assert product_vol < crude_vol
        assert product_vol > crude_vol * 0.90  # losses should be small

    def test_unit_throughputs_present(self, result):
        assert len(result["unit_throughputs"]) == 5
        for u in result["unit_throughputs"]:
            assert u["utilization_pct"] >= 0
            assert u["utilization_pct"] <= 100

    def test_stream_flows_present(self, result):
        assert len(result["stream_flows"]) > 0
        for f in result["stream_flows"]:
            assert f["volume"] > 0

    def test_result_shape(self, result):
        """Verify all expected top-level keys exist."""
        expected = {"status", "objective_value", "solve_time_ms",
                    "crude_slate", "unit_throughputs", "product_outputs",
                    "stream_flows", "margin"}
        assert expected.issubset(result.keys())

    def test_margin_shape(self, result):
        expected = {"revenue", "crude_cost", "processing_cost", "gross_margin"}
        assert expected == set(result["margin"].keys())

    def test_sulfur_specs_reported(self, result):
        """Products with sulfur specs should report blended sulfur."""
        spec_products = {"Gasoline", "Jet Fuel", "Diesel", "Fuel Oil"}
        for p in result["product_outputs"]:
            if p["product"] in spec_products:
                assert "sulfur_pct" in p, f"{p['product']} missing sulfur_pct"
                assert "sulfur_max" in p, f"{p['product']} missing sulfur_max"
                assert p["sulfur_pct"] <= p["sulfur_max"], (
                    f"{p['product']} sulfur {p['sulfur_pct']} exceeds max {p['sulfur_max']}"
                )
            else:
                assert "sulfur_pct" not in p

    def test_gasoline_sulfur_tight(self, result):
        """Gasoline has a 0.10% sulfur spec — verify it's respected."""
        gasoline = [p for p in result["product_outputs"] if p["product"] == "Gasoline"][0]
        assert gasoline["sulfur_pct"] <= 0.10

    def test_diesel_sulfur_under_spec(self, result):
        """Diesel sulfur should be well under 0.05% due to hydrotreated diesel."""
        diesel = [p for p in result["product_outputs"] if p["product"] == "Diesel"][0]
        assert diesel["sulfur_pct"] <= 0.05


class TestSolverEdgeCases:
    """Verify the solver handles bad input without crashing."""

    def test_no_cdu(self):
        case = Obj(
            crude_assays=[Obj(crude_name="X", cost_per_bbl=70, min_volume=0,
                              max_volume=1000, api_gravity=35, sulfur_pct=1, cuts=[])],
            process_units=[],
            products=[],
        )
        result = solve_case(case)
        assert result["status"] == "error"
        assert "margin" in result

    def test_no_crudes(self):
        case = Obj(
            crude_assays=[],
            process_units=[Obj(name="CDU", unit_type="CDU", min_capacity=0,
                               max_capacity=100000, variable_cost_per_bbl=1.5, yields=[])],
            products=[],
        )
        result = solve_case(case)
        assert result["status"] == "error"
        assert "margin" in result
