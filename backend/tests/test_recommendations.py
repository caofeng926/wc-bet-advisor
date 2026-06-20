"""Tests for the value-bet probability selector (1x2 / ah)."""
from app.api.recommendations import _p_1x2, _p_for_selection


class TestP1x2:
    def test_sum_to_one(self):
        p = _p_1x2(1500, 1500)
        total = p["H"] + p["D"] + p["A"]
        assert abs(total - 1.0) < 0.01  # matrix rounded

    def test_strong_home(self):
        p = _p_1x2(1900, 1500)
        assert p["H"] > p["A"]
        assert p["H"] > p["D"]

    def test_weak_home(self):
        p = _p_1x2(1500, 1900)
        assert p["A"] > p["H"]

    def test_equal_teams_home_slight_edge(self):
        p = _p_1x2(1500, 1500)
        # Home advantage makes H slightly > A
        assert p["H"] >= p["A"]


class TestPForSelection:
    def test_1x2_routes(self):
        pH = _p_for_selection(1600, 1500, "1x2", "H")
        pA = _p_for_selection(1600, 1500, "1x2", "A")
        p123 = _p_1x2(1600, 1500)
        assert abs(pH - p123["H"]) < 0.001
        assert abs(pA - p123["A"]) < 0.001

    def test_ah_negative_handicap(self):
        # Home with -1 handicap should have lower prob than raw H
        pH = _p_for_selection(1700, 1500, "1x2", "H")
        pH_minus1 = _p_for_selection(1700, 1500, "ah", "H(-1)")
        assert pH_minus1 < pH

    def test_ah_positive_handicap_easier(self):
        # Away with +1 handicap should have higher prob than raw A
        pA = _p_for_selection(1500, 1700, "1x2", "A")
        pA_plus1 = _p_for_selection(1500, 1700, "ah", "A(+1)")
        assert pA_plus1 > pA

    def test_unknown_market_falls_back_to_1x2(self):
        p = _p_for_selection(1600, 1500, "unknown_market", "H")
        p123 = _p_1x2(1600, 1500)
        assert abs(p - p123["H"]) < 0.001
