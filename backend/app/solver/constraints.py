"""Small helpers for the main LP constraint groups."""


def constraint_groups() -> list[str]:
    """Constraint buckets I plan to use in the first solve pass."""
    return [
        "crude_bounds",
        "unit_capacity",
        "material_balance",
        "product_demand",
    ]
