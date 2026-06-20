"""Tests for the Polymarket normalizer."""
from app.services.polymarket import normalize_polymarket


class TestNormalizePolymarket:
    def test_empty_input(self):
        assert normalize_polymarket([]) == []

    def test_skips_single_outcome_markets(self):
        market = {"id": "m1", "outcomes": ["Yes"], "outcomePrices": {"Yes": 0.5}}
        assert normalize_polymarket([market]) == []

    def test_zero_price_skipped(self):
        market = {"id": "m1", "outcomes": ["Yes", "No"], "outcomePrices": {"Yes": 0, "No": 0.5}}
        assert normalize_polymarket([market]) == []

    def test_happy_path(self):
        market = {
            "id": "m1",
            "question": "Will Brazil win?",
            "outcomes": ["Yes", "No"],
            "outcomePrices": {"Yes": 0.42, "No": 0.58},
            "liquidity": 1000.0,
            "volume24hr": 200.0,
        }
        out = normalize_polymarket([market])
        assert len(out) == 1
        m = out[0]
        assert m["market_id"] == "m1"
        assert m["price_yes"] == 0.42
        assert m["price_no"] == 0.58
        assert m["implied_prob"] == 0.42
        assert m["liquidity"] == 1000.0
        assert m["volume_24h"] == 200.0


class TestFetchMatchMarkets:
    """fetch_match_markets requires network; smoke-test the offline filter branch only."""

    def test_offline_returns_empty(self, monkeypatch):
        # If httpx fails, fetch_markets_for_team returns []; the filter then yields []
        from app.services import polymarket as pm
        monkeypatch.setattr(pm.httpx, "Client", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("offline")))
        out = pm.fetch_match_markets("Brazil", "Croatia")
        assert out == []
