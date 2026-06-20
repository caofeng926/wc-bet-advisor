"""Tests for the /api/football/today endpoint graceful offline behavior.

The endpoint should never raise 503: when sporttery.cn is unreachable, it
returns 200 with source=offline and empty matches, so the frontend can show
a friendly "等待体彩开盘" hint.
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_today_offline_returns_empty():
    """When sporttery fetch fails, /api/football/today returns 200 + empty."""
    with patch("app.api.football.fetch", side_effect=RuntimeError("network down")):
        r = client.get("/api/football/today")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["source"] == "offline"
    assert body["matches"] == []
    assert "date" in body
    assert "fetched_at" in body


def test_today_online_enriches_per_market_best():
    """When sporttery returns data, each match gets crs/ttg/hafu best."""
    fake_match = {
        "id": 1001,
        "homeTeamAllName": "Mexico",
        "awayTeamAllName": "South Africa",
        "matchDate": "2026-06-12",
        "matchTime": "21:00:00",
        "home_elo": 1820,
        "away_elo": 1640,
        "crs": {
            "s1s0": 7.0, "s0s0": 9.0, "s2s1": 8.5, "s1s1": 6.5, "s2s0": 11.0,
        },
        "ttg": {
            "s0": 8.0, "s1": 3.5, "s2": 3.2, "s3": 4.5, "s4": 7.0,
        },
        "hafu": {
            "hh": 4.0, "hd": 12.0, "ha": 25.0, "dh": 7.0, "dd": 5.5,
            "da": 18.0, "ah": 30.0, "ad": 20.0, "aa": 45.0,
        },
        "poolList": [
            {"poolCode": "crs", "single": 1},
            {"poolCode": "ttg", "single": 0},
            {"poolCode": "hafu", "single": 0},
        ],
    }
    with patch("app.api.football.fetch", return_value={"matchList": [fake_match]}):
        r = client.get("/api/football/today")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["source"] == "sporttery_api"
    assert len(body["matches"]) == 1
    m = body["matches"][0]
    assert m["match_id"] == 1001
    assert m["home"] == "Mexico"
    assert m["away"] == "South Africa"
    assert m["best_crs"] is not None
    assert m["best_ttg"] is not None
    assert m["best_hafu"] is not None
    # best_crs.single should be 1 (单关) since the fake poolList says so
    assert m["best_crs"]["single"] == 1
    # Verify edge = p_model * odds - 1
    crs = m["best_crs"]
    expected_edge = round(crs["p_model"] * crs["odds"] - 1, 3)
    assert abs(crs["edge"] - expected_edge) < 1e-6
