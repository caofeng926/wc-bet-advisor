"""Kelly formula unit tests"""
from app.services.kelly import kelly_fraction, kelly_stake_pct


class TestKellyFraction:
    def test_standard(self):
        # p=0.6, odds=2.0 → b=1, kelly = (1*0.6 - 0.4)/1 = 0.2
        assert abs(kelly_fraction(0.6, 2.0) - 0.2) < 1e-6

    def test_exact_breakeven(self):
        # p=0.5, odds=2.0 → b=1, kelly = (1*0.5 - 0.5)/1 = 0
        assert abs(kelly_fraction(0.5, 2.0)) < 1e-6

    def test_negative_edge(self):
        # p=0.3, odds=2.0 → negative kelly → should be 0
        assert kelly_fraction(0.3, 2.0) <= 0

    def test_p_zero(self):
        assert kelly_fraction(0, 2.0) == 0

    def test_p_one(self):
        # p=1, odds=2 → b=1, kelly = (1*1 - 0)/1 = 1 (all-in)
        assert abs(kelly_fraction(1.0, 2.0) - 1.0) < 1e-6

    def test_odds_one(self):
        # odds=1 → no value, kelly = 0
        assert kelly_fraction(0.6, 1.0) == 0

    def test_odds_less_than_one(self):
        assert kelly_fraction(0.6, 0.9) == 0

    def test_high_odds(self):
        # p=0.1, odds=10 → b=9, kelly = (9*0.1 - 0.9)/9 = 0
        assert kelly_fraction(0.1, 10.0) <= 0

    def testdecimal_odds(self):
        # p=0.4, odds=3.0 → b=2, kelly = (2*0.4 - 0.6)/2 = 0.1
        assert abs(kelly_fraction(0.4, 3.0) - 0.1) < 1e-6


class TestKellyStakePct:
    def test_fraction_apply(self):
        # kelly=0.2, fraction=0.25 → stake_pct = 0.05
        assert abs(kelly_stake_pct(0.2, 0.25) - 0.05) < 1e-6

    def test_cap_at_5pct(self):
        # kelly=0.5, fraction=0.25 → kelly*fraction=0.125, cap=0.05
        assert kelly_stake_pct(0.5, 0.25) <= 0.05

    def test_negative_kelly(self):
        assert kelly_stake_pct(-0.1, 0.25) == 0

    def test_zero_kelly(self):
        assert kelly_stake_pct(0, 0.25) == 0