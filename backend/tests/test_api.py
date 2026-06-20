"""API integration tests"""
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestHealth:
    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        assert "version" in r.json()


class TestMatches:
    def test_list_matches(self):
        r = client.get("/api/matches?limit=5")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_matches_filter_status(self):
        r = client.get("/api/matches?status=scheduled&limit=5")
        assert r.status_code == 200

    def test_get_match_not_found(self):
        r = client.get("/api/matches/99999")
        assert r.status_code == 404


class TestLotto:
    def test_lotto14_not_enough_matches(self):
        # If fewer than 14 scheduled matches, should return 503 or work with available
        r = client.get("/api/lotto/14场/recommendation")
        #503 if not enough, 200 if enough
        assert r.status_code in (200, 503)

    def test_lotto_periods(self):
        r = client.get("/api/lotto/periods")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestParlay:
    def test_parlay_candidates(self):
        r = client.get("/api/parlay/candidates?min_edge=0.05")
        assert r.status_code == 200
        data = r.json()
        assert "candidates" in data
        assert "min_edge" in data

    def test_parlay_candidates_min_edge_0(self):
        r = client.get("/api/parlay/candidates?min_edge=0")
        assert r.status_code == 200

    def test_parlay_calculate_empty(self):
        r = client.post("/api/parlay/calculate", json={"legs": [], "bankroll": 1000})
        assert r.status_code == 200
        data = r.json()
        assert data["total_odds"] == 1
        assert "warnings" in data

    def test_parlay_calculate_with_legs(self):
        # Need valid match_id from database - will fail gracefully if no matches
        r = client.post("/api/parlay/calculate", json={
            "legs": [
                {"match_id": 1, "market": "1x2", "selection": "H", "odds": 2.0}
            ],
            "bankroll": 1000,
            "kelly_fraction": 0.25,
        })
        assert r.status_code == 200


class TestSlips:
    def test_list_slips(self):
        r = client.get("/api/slips")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_slip(self):
        r = client.post("/api/slips", json={
            "title": "测试方案",
            "kind": "single",
            "selections": [{"note": "test", "odds": 2.0}],
            "total_odds": 2.0,
            "stake": 10,
            "cost": 0,
        })
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "测试方案"

    def test_pnl_summary(self):
        r = client.get("/api/slips/pnl/summary")
        assert r.status_code == 200
        data = r.json()
        assert "total_stake" in data
        assert "roi_pct" in data


class TestAdmin:
    def test_countdown_no_matches(self):
        r = client.get("/api/admin/countdown")
        assert r.status_code == 200
        data = r.json()
        assert "status" in data
        assert "seconds_remaining" in data

    def test_import_odds_invalid_match(self):
        r = client.post("/api/admin/odds/import", json={
            "bookmaker": "测试",
            "market": "1x2",
            "rows": [{"match_external_id": "invalid", "selection": "H", "odds": 2.0}],
        })
        assert r.status_code == 200
        data = r.json()
        assert len(data["errors"]) > 0