"""Solver endpoints for refinery planning runs."""

from fastapi import APIRouter

from app.solver.results_parser import empty_result_payload

router = APIRouter(tags=["solver"])


@router.post("/api/cases/{case_id}/optimize")
def optimize(case_id: int):
    return {
        "status": "not_ready",
        "message": "The solve flow is still being finished.",
        "result": empty_result_payload(case_id),
    }
