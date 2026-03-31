"""
Seed a demo refinery case with realistic simplified data.

Usage:
    python -m app.seed.demo_refinery

This uses create_all for seeding convenience only. Normal runtime uses Alembic migrations.
"""

from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models.case import Case
from app.models.crude import CrudeAssay, CrudeAssayCut
from app.models.unit import ProcessUnit, UnitYield
from app.models.product import Product, ProductBlendSpec
from app.models.stream import Stream


def seed(db: Session) -> Case:
    # Check if demo case already exists
    existing = db.query(Case).filter(Case.name == "Demo Refinery").first()
    if existing:
        print("Demo case already exists, skipping seed.")
        return existing

    case = Case(name="Demo Refinery", description="Simplified refinery for development and testing")
    db.add(case)
    db.flush()

    # ── Streams ───────────────────────────────────────────────
    stream_names = {
        # Crude cuts from CDU
        "crude_cut": [
            "Light Naphtha", "Heavy Naphtha", "Kerosene", "Light Gas Oil",
            "Heavy Gas Oil", "Atmospheric Residue",
        ],
        # Intermediate streams
        "intermediate": [
            "Vacuum Gas Oil", "Vacuum Residue",
            "FCC Gasoline", "FCC Light Cycle Oil", "FCC Slurry",
            "Reformate",
            "Hydrotreated Diesel",
        ],
        # Products
        "product": [
            "Gasoline", "Jet Fuel", "Diesel", "Fuel Oil", "LPG", "Naphtha",
        ],
    }

    for stype, names in stream_names.items():
        for name in names:
            db.add(Stream(case_id=case.id, name=name, stream_type=stype))

    # ── Crudes ────────────────────────────────────────────────
    crudes_data = [
        {
            "crude_name": "Arab Light",
            "api_gravity": 33.4,
            "sulfur_pct": 1.77,
            "cost_per_bbl": 72.00,
            "min_volume": 0,
            "max_volume": 50000,
            "cuts": [
                ("Light Naphtha", 7.5, 0.68, 0.0005),
                ("Heavy Naphtha", 11.0, 0.74, 0.001),
                ("Kerosene", 14.0, 0.79, 0.05),
                ("Light Gas Oil", 16.5, 0.84, 0.80),
                ("Heavy Gas Oil", 12.0, 0.88, 1.80),
                ("Atmospheric Residue", 39.0, 0.96, 3.50),
            ],
        },
        {
            "crude_name": "Brent",
            "api_gravity": 38.3,
            "sulfur_pct": 0.37,
            "cost_per_bbl": 78.00,
            "min_volume": 0,
            "max_volume": 40000,
            "cuts": [
                ("Light Naphtha", 10.0, 0.66, 0.0002),
                ("Heavy Naphtha", 14.0, 0.73, 0.0005),
                ("Kerosene", 16.0, 0.78, 0.02),
                ("Light Gas Oil", 18.0, 0.83, 0.15),
                ("Heavy Gas Oil", 10.0, 0.87, 0.40),
                ("Atmospheric Residue", 32.0, 0.94, 0.90),
            ],
        },
        {
            "crude_name": "WTI",
            "api_gravity": 39.6,
            "sulfur_pct": 0.24,
            "cost_per_bbl": 75.00,
            "min_volume": 0,
            "max_volume": 45000,
            "cuts": [
                ("Light Naphtha", 11.0, 0.65, 0.0001),
                ("Heavy Naphtha", 15.0, 0.72, 0.0003),
                ("Kerosene", 15.5, 0.77, 0.01),
                ("Light Gas Oil", 17.5, 0.82, 0.10),
                ("Heavy Gas Oil", 9.5, 0.86, 0.30),
                ("Atmospheric Residue", 31.5, 0.93, 0.60),
            ],
        },
    ]

    for cd in crudes_data:
        cuts_data = cd["cuts"]
        assay = CrudeAssay(
            case_id=case.id,
            crude_name=cd["crude_name"],
            api_gravity=cd["api_gravity"],
            sulfur_pct=cd["sulfur_pct"],
            cost_per_bbl=cd["cost_per_bbl"],
            min_volume=cd["min_volume"],
            max_volume=cd["max_volume"],
        )
        db.add(assay)
        db.flush()
        for cut_name, yield_pct, density, sulfur in cuts_data:
            db.add(CrudeAssayCut(
                assay_id=assay.id,
                cut_name=cut_name,
                yield_pct=yield_pct,
                density=density,
                sulfur_pct=sulfur,
            ))

    # ── Process Units ─────────────────────────────────────────
    units_data = [
        {
            "name": "CDU", "unit_type": "CDU",
            "min_capacity": 10000, "max_capacity": 100000,
            "variable_cost_per_bbl": 1.50,
            "yields": [
                # CDU fractionates crude into cuts — yields defined per-crude above,
                # so CDU yields here represent the pass-through (1:1 crude → cut mix)
            ],
        },
        {
            "name": "VDU", "unit_type": "VDU",
            "min_capacity": 5000, "max_capacity": 50000,
            "variable_cost_per_bbl": 1.20,
            "yields": [
                ("Atmospheric Residue", "Vacuum Gas Oil", 0.55),
                ("Atmospheric Residue", "Vacuum Residue", 0.45),
            ],
        },
        {
            "name": "FCC", "unit_type": "FCC",
            "min_capacity": 5000, "max_capacity": 40000,
            "variable_cost_per_bbl": 3.00,
            "yields": [
                ("Vacuum Gas Oil", "FCC Gasoline", 0.50),
                ("Vacuum Gas Oil", "FCC Light Cycle Oil", 0.20),
                ("Vacuum Gas Oil", "FCC Slurry", 0.10),
                ("Vacuum Gas Oil", "LPG", 0.15),
            ],
        },
        {
            "name": "Reformer", "unit_type": "Reformer",
            "min_capacity": 3000, "max_capacity": 25000,
            "variable_cost_per_bbl": 2.50,
            "yields": [
                ("Heavy Naphtha", "Reformate", 0.85),
                ("Heavy Naphtha", "LPG", 0.10),
            ],
        },
        {
            "name": "Hydrotreater", "unit_type": "Hydrotreater",
            "min_capacity": 3000, "max_capacity": 30000,
            "variable_cost_per_bbl": 1.80,
            "yields": [
                ("Light Gas Oil", "Hydrotreated Diesel", 0.97),
                ("FCC Light Cycle Oil", "Hydrotreated Diesel", 0.95),
            ],
        },
    ]

    for ud in units_data:
        yields_list = ud["yields"]
        unit = ProcessUnit(
            case_id=case.id,
            name=ud["name"],
            unit_type=ud["unit_type"],
            min_capacity=ud["min_capacity"],
            max_capacity=ud["max_capacity"],
            variable_cost_per_bbl=ud["variable_cost_per_bbl"],
        )
        db.add(unit)
        db.flush()
        for inp, out, frac in yields_list:
            db.add(UnitYield(
                unit_id=unit.id,
                input_stream=inp,
                output_stream=out,
                yield_fraction=frac,
            ))

    # ── Products ──────────────────────────────────────────────
    products_data = [
        {
            "name": "Gasoline", "price_per_bbl": 95.00,
            "min_demand": 5000, "max_demand": 50000,
            "specs": [("sulfur", None, 0.001)],
        },
        {
            "name": "Jet Fuel", "price_per_bbl": 92.00,
            "min_demand": 3000, "max_demand": 25000,
            "specs": [("sulfur", None, 0.30)],
        },
        {
            "name": "Diesel", "price_per_bbl": 90.00,
            "min_demand": 5000, "max_demand": 40000,
            "specs": [("sulfur", None, 0.05)],
        },
        {
            "name": "Fuel Oil", "price_per_bbl": 60.00,
            "min_demand": 0, "max_demand": 30000,
            "specs": [("sulfur", None, 3.50)],
        },
        {
            "name": "LPG", "price_per_bbl": 45.00,
            "min_demand": 0, "max_demand": 15000,
            "specs": [],
        },
        {
            "name": "Naphtha", "price_per_bbl": 70.00,
            "min_demand": 0, "max_demand": 20000,
            "specs": [],
        },
    ]

    for pd_ in products_data:
        specs_data = pd_["specs"]
        product = Product(
            case_id=case.id,
            name=pd_["name"],
            price_per_bbl=pd_["price_per_bbl"],
            min_demand=pd_["min_demand"],
            max_demand=pd_["max_demand"],
        )
        db.add(product)
        db.flush()
        for prop_name, min_val, max_val in specs_data:
            db.add(ProductBlendSpec(
                product_id=product.id,
                property_name=prop_name,
                min_value=min_val,
                max_value=max_val,
                blend_type="linear_volume",
            ))

    db.commit()
    db.refresh(case)
    print(f"Seeded demo case: id={case.id}, name='{case.name}'")
    return case


def main():
    # For seed convenience only — normal runtime uses Alembic migrations
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
