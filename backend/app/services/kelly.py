"""Kelly formula service"""


def kelly_fraction(p: float, odds: float) -> float:
    """Standard Kelly fraction: f = (b*p - q) / b where b=odds-1, q=1-p"""
    if p <= 0 or odds <= 1:
        return 0.0
    b = odds - 1
    q = 1 - p
    f = (b * p - q) / b
    return max(0.0, f)


def kelly_stake_pct(kelly: float, fraction: float = 0.25, cap: float = 0.05) -> float:
    """Apply Kelly fraction with cap. Default1/4 Kelly, 5% cap."""
    if kelly <= 0:
        return 0.0
    return min(kelly * fraction, cap)