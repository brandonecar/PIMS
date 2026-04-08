"""Solver endpoints — run optimization and retrieve results."""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.case import Case
from app.models.run import OptimizationRun
from app.solver.model_builder import solve_case, SOLVER_NAME

log = logging.getLogger(__name__)

router = APIRouter(tags=["solver"])

EMPTY_RESULT = {
    "status": "not_run",
    "objective_value": None,
    "solve_time_ms": None,
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


@router.post("/api/cases/{case_id}/optimize")
def optimize(case_id: int, db: Session = Depends(get_db)):
    """Build and solve the refinery LP for a case, store the run, return results."""
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(404, "Case not found")

    try:
        result = solve_case(case)
    except Exception as exc:
        log.exception("Solver failed for case %d", case_id)
        result = {**EMPTY_RESULT, "status": "error", "message": str(exc)}

    run = OptimizationRun(
        case_id=case_id,
        status=result["status"],
        solver_name=SOLVER_NAME,
        solve_time_ms=result.get("solve_time_ms"),
        objective_value=result.get("objective_value"),
        solver_log=json.dumps(result),
    )
    db.add(run)
    db.commit()

    return result


@router.get("/api/cases/{case_id}/results")
def get_results(case_id: int, db: Session = Depends(get_db)):
    """Return the most recent optimization results for a case."""
    run = (
        db.query(OptimizationRun)
        .filter(OptimizationRun.case_id == case_id)
        .order_by(OptimizationRun.created_at.desc())
        .first()
    )

    if not run or not run.solver_log:
        return {**EMPTY_RESULT}

    return json.loads(run.solver_log)
