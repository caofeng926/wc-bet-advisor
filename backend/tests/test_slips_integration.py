"""Integration tests for the slips (slip ledger) endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def _baseline_pnl():
    """Read the current pnl summary so the test asserts on deltas, not absolutes."""
    r = client.get("/api/slips/pnl/summary")
    r.raise_for_status()
    s = r.json()
    return s["total_pnl"], s["settled_count"]


class TestSlipsFlow:
    def test_create_list_settle_pnl(self):
        baseline_pnl, baseline_count = _baseline_pnl()

        body = {
            "title": "test parlay",
            "kind": "parlay",
            "selections": [{"match_id": 1, "market": "1x2", "pick": "H", "odds": 1.9}],
            "total_odds": 1.9,
            "stake": 100.0,
            "cost": 0.0,
            "notes": None,
        }
        r = client.post("/api/slips", json=body)
        assert r.status_code == 201, r.text
        created = r.json()
        slip_id = created["id"]
        assert created["title"] == "test parlay"
        assert created["result"] == "pending"
        assert created["stake"] == 100.0

        r = client.get("/api/slips")
        assert r.status_code == 200
        ids = [s["id"] for s in r.json()]
        assert slip_id in ids

        # Settle as a win: payout = stake * total_odds = 190, so pnl = +90
        r = client.post(f"/api/slips/{slip_id}/settle", json={"result": "win", "payout": 190.0})
        assert r.status_code == 200
        settled = r.json()
        assert settled["result"] == "win"
        assert settled["payout"] == 190.0
        assert settled["pnl"] == 90.0

        r = client.get("/api/slips/pnl/summary")
        assert r.status_code == 200
        summary = r.json()
        # pnl should have grown by exactly +90
        assert summary["total_pnl"] - baseline_pnl == pytest.approx(90.0, abs=0.01)
        assert summary["settled_count"] - baseline_count == 1

    def test_settle_lose_negative_pnl(self):
        baseline_pnl, _ = _baseline_pnl()
        body = {
            "title": "test lose",
            "kind": "single",
            "selections": [],
            "total_odds": 1.5,
            "stake": 50.0,
        }
        r = client.post("/api/slips", json=body)
        slip_id = r.json()["id"]
        r = client.post(f"/api/slips/{slip_id}/settle", json={"result": "lose", "payout": 0.0})
        assert r.status_code == 200
        assert r.json()["pnl"] == -50.0
        # total_pnl should drop by exactly 50
        r = client.get("/api/slips/pnl/summary")
        assert r.json()["total_pnl"] - baseline_pnl == pytest.approx(-50.0, abs=0.01)

    def test_settle_nonexistent_404(self):
        r = client.post("/api/slips/99999/settle", json={"result": "win", "payout": 100.0})
        assert r.status_code == 404
