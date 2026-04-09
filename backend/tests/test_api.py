"""Integration tests for API endpoints and guest isolation.

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

GUEST_A = "test-guest-aaaaaaaa"
GUEST_B = "test-guest-bbbbbbbb"
HEADERS_A = {"X-Guest-Id": GUEST_A}
HEADERS_B = {"X-Guest-Id": GUEST_B}


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

    # Seed a demo case for guest A
    db = TestSession()
    seed(db, guest_id=GUEST_A)
    db.close()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ── Solver Endpoints ─────────────────────────────────────────

class TestOptimizeEndpoint:
    def test_optimize_returns_optimal(self, client):
        resp = client.post("/api/cases/1/optimize", headers=HEADERS_A)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "Optimal"
        assert data["objective_value"] > 0
        assert data["margin"]["gross_margin"] > 0

    def test_optimize_result_shape(self, client):
        resp = client.post("/api/cases/1/optimize", headers=HEADERS_A)
        data = resp.json()
        expected = {"status", "objective_value", "solve_time_ms",
                    "crude_slate", "unit_throughputs", "product_outputs",
                    "stream_flows", "margin"}
        assert expected.issubset(set(data.keys()))

    def test_results_before_solve(self, client):
        resp = client.get("/api/cases/1/results", headers=HEADERS_A)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "not_run"

    def test_results_after_solve(self, client):
        client.post("/api/cases/1/optimize", headers=HEADERS_A)
        resp = client.get("/api/cases/1/results", headers=HEADERS_A)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "Optimal"

    def test_optimize_nonexistent_case(self, client):
        resp = client.post("/api/cases/999/optimize", headers=HEADERS_A)
        assert resp.status_code == 404


# ── Guest Isolation ──────────────────────────────────────────

class TestGuestIsolation:
    def test_cases_scoped_to_guest(self, client):
        """Different guest IDs should see different cases."""
        resp_a = client.get("/api/cases", headers=HEADERS_A)
        resp_b = client.get("/api/cases", headers=HEADERS_B)
        assert resp_a.status_code == 200
        assert resp_b.status_code == 200
        ids_a = {c["id"] for c in resp_a.json()}
        ids_b = {c["id"] for c in resp_b.json()}
        assert ids_a.isdisjoint(ids_b)

    def test_guest_cannot_access_other_guest_case(self, client):
        resp = client.get("/api/cases/1", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_missing_guest_header_rejected(self, client):
        resp = client.get("/api/cases")
        assert resp.status_code == 422

    def test_reset_workspace(self, client):
        client.post("/api/cases", headers=HEADERS_A, json={"name": "Test Case"})
        cases_before = client.get("/api/cases", headers=HEADERS_A).json()
        assert len(cases_before) == 2

        resp = client.post("/api/guest/reset", headers=HEADERS_A)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Demo Refinery"

        cases_after = client.get("/api/cases", headers=HEADERS_A).json()
        assert len(cases_after) == 1


# ── Child Entity Ownership ───────────────────────────────────

class TestChildEntityOwnership:
    """Verify all child-entity routes enforce guest ownership."""

    def _get_case_id(self, client, headers):
        """Get the first case ID for this guest."""
        cases = client.get("/api/cases", headers=headers).json()
        return cases[0]["id"]

    def _get_first_id(self, client, path, headers):
        """Get the first entity ID from a list endpoint."""
        resp = client.get(path, headers=headers)
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) > 0, f"No items at {path}"
        return items[0]["id"]

    # ── Case-scoped list/create routes ──────────────────

    def test_list_crudes_wrong_guest(self, client):
        resp = client.get("/api/cases/1/crudes", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_list_units_wrong_guest(self, client):
        resp = client.get("/api/cases/1/units", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_list_products_wrong_guest(self, client):
        resp = client.get("/api/cases/1/products", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_list_streams_wrong_guest(self, client):
        resp = client.get("/api/cases/1/streams", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_create_crude_wrong_guest(self, client):
        resp = client.post(
            "/api/cases/1/crudes", headers=HEADERS_B,
            json={"crude_name": "Hack", "cost_per_bbl": 1},
        )
        assert resp.status_code == 404

    def test_create_unit_wrong_guest(self, client):
        resp = client.post(
            "/api/cases/1/units", headers=HEADERS_B,
            json={"name": "Hack", "unit_type": "CDU"},
        )
        assert resp.status_code == 404

    def test_create_product_wrong_guest(self, client):
        resp = client.post(
            "/api/cases/1/products", headers=HEADERS_B,
            json={"name": "Hack", "price_per_bbl": 1},
        )
        assert resp.status_code == 404

    def test_create_stream_wrong_guest(self, client):
        resp = client.post(
            "/api/cases/1/streams", headers=HEADERS_B,
            json={"name": "Hack", "stream_type": "crude_cut"},
        )
        assert resp.status_code == 404

    # ── Entity-level routes (update/delete by ID) ──────

    def test_update_crude_wrong_guest(self, client):
        crude_id = self._get_first_id(client, "/api/cases/1/crudes", HEADERS_A)
        resp = client.put(
            f"/api/crudes/{crude_id}", headers=HEADERS_B,
            json={"cost_per_bbl": 999},
        )
        assert resp.status_code == 404

    def test_delete_crude_wrong_guest(self, client):
        crude_id = self._get_first_id(client, "/api/cases/1/crudes", HEADERS_A)
        resp = client.delete(f"/api/crudes/{crude_id}", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_get_cuts_wrong_guest(self, client):
        crude_id = self._get_first_id(client, "/api/cases/1/crudes", HEADERS_A)
        resp = client.get(f"/api/crudes/{crude_id}/cuts", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_update_unit_wrong_guest(self, client):
        unit_id = self._get_first_id(client, "/api/cases/1/units", HEADERS_A)
        resp = client.put(
            f"/api/units/{unit_id}", headers=HEADERS_B,
            json={"max_capacity": 999999},
        )
        assert resp.status_code == 404

    def test_delete_unit_wrong_guest(self, client):
        unit_id = self._get_first_id(client, "/api/cases/1/units", HEADERS_A)
        resp = client.delete(f"/api/units/{unit_id}", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_get_yields_wrong_guest(self, client):
        unit_id = self._get_first_id(client, "/api/cases/1/units", HEADERS_A)
        resp = client.get(f"/api/units/{unit_id}/yields", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_update_product_wrong_guest(self, client):
        prod_id = self._get_first_id(client, "/api/cases/1/products", HEADERS_A)
        resp = client.put(
            f"/api/products/{prod_id}", headers=HEADERS_B,
            json={"price_per_bbl": 999},
        )
        assert resp.status_code == 404

    def test_delete_product_wrong_guest(self, client):
        prod_id = self._get_first_id(client, "/api/cases/1/products", HEADERS_A)
        resp = client.delete(f"/api/products/{prod_id}", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_get_specs_wrong_guest(self, client):
        prod_id = self._get_first_id(client, "/api/cases/1/products", HEADERS_A)
        resp = client.get(f"/api/products/{prod_id}/specs", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_get_recipes_wrong_guest(self, client):
        prod_id = self._get_first_id(client, "/api/cases/1/products", HEADERS_A)
        resp = client.get(f"/api/products/{prod_id}/recipes", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_update_stream_wrong_guest(self, client):
        stream_id = self._get_first_id(client, "/api/cases/1/streams", HEADERS_A)
        resp = client.put(
            f"/api/streams/{stream_id}", headers=HEADERS_B,
            json={"name": "Hack"},
        )
        assert resp.status_code == 404

    def test_delete_stream_wrong_guest(self, client):
        stream_id = self._get_first_id(client, "/api/cases/1/streams", HEADERS_A)
        resp = client.delete(f"/api/streams/{stream_id}", headers=HEADERS_B)
        assert resp.status_code == 404

    # ── Solver routes for wrong guest ──────────────────

    def test_optimize_wrong_guest(self, client):
        resp = client.post("/api/cases/1/optimize", headers=HEADERS_B)
        assert resp.status_code == 404

    def test_results_wrong_guest(self, client):
        resp = client.get("/api/cases/1/results", headers=HEADERS_B)
        assert resp.status_code == 404
