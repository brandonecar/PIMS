"""Integration tests for solver API endpoints.

Uses SQLite in-memory with a shared connection to avoid requiring Postgres.
"""

import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.seed.demo_refinery import seed  # noqa: E402


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def _override_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_db

    db = TestSession()
    seed(db)
    db.close()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


class TestOptimizeEndpoint:
    def test_optimize_returns_optimal(self, client):
        resp = client.post("/api/cases/1/optimize")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "Optimal"
        assert data["objective_value"] > 0
        assert data["margin"]["gross_margin"] > 0

    def test_optimize_result_shape(self, client):
        resp = client.post("/api/cases/1/optimize")
        data = resp.json()
        expected = {"status", "objective_value", "solve_time_ms",
                    "crude_slate", "unit_throughputs", "product_outputs",
                    "stream_flows", "margin"}
        assert expected.issubset(set(data.keys()))

    def test_results_before_solve(self, client):
        resp = client.get("/api/cases/1/results")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "not_run"

    def test_results_after_solve(self, client):
        client.post("/api/cases/1/optimize")
        resp = client.get("/api/cases/1/results")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "Optimal"

    def test_optimize_nonexistent_case(self, client):
        resp = client.post("/api/cases/999/optimize")
        assert resp.status_code == 404
