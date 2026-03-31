"""Helpers for shaping solver output for the results view."""


def empty_result_payload(case_id: int) -> dict:
    """Return the empty results shape used before a case is solved."""
    return {
        "case_id": case_id,
        "status": "not_run",
        "objective_value": None,
        "crude_slate": [],
        "unit_utilization": [],
        "product_output": [],
        "economics": {},
        "constraints": [],
    }
