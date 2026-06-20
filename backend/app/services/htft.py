"""Half-time/Full-time (半全场) prediction using two-stage Poisson model.

HTFT: 9 outcomes = {HH, HD, HA, DH, DD, DA, AH, AD, AA}
Approach: Use half-length Poisson (λ/2) for each half, then combine. Each
half's H/D/A probabilities are computed on an 11x11 score grid so the mass
is properly conserved (the tail beyond 10 goals is negligible for λ<=3).
"""
from math import factorial, exp


_BASE_LAM = 1.3     # global soccer average goals per team
_ELO_SCALE = 600    # ELO points per 1.0 in log-rate
_MIN_LAM = 0.2
_MAX_LAM = 4.0
_MATRIX_N = 11      # 0..10 goals per side per half


def _poisson_pmf(lam: float, k: int) -> float:
    return exp(-lam) * (lam ** k) / factorial(k)


def _half_probs(lam_h: float, lam_a: float) -> dict[str, float]:
    """Half-time result probabilities: H/D/A"""
    probs = {"H": 0.0, "D": 0.0, "A": 0.0}
    for hg in range(_MATRIX_N):
        for ag in range(_MATRIX_N):
            p = _poisson_pmf(lam_h, hg) * _poisson_pmf(lam_a, ag)
            if hg > ag:
                probs["H"] += p
            elif hg < ag:
                probs["A"] += p
            else:
                probs["D"] += p
    total = probs["H"] + probs["D"] + probs["A"]
    return {k: round(v / total, 4) for k, v in probs.items()}


def predict_htft(home_elo: int, away_elo: int, home_adv: int = 60) -> dict:
    """Predict half-time/full-time outcomes.

    Returns dict with ht1_probs, ht2_probs, matrix, outcomes, top3.
    """
    diff = home_elo + home_adv - away_elo
    lam_h = min(max(_BASE_LAM * exp(diff / _ELO_SCALE), _MIN_LAM), _MAX_LAM)
    lam_a = min(max(_BASE_LAM * exp(-diff / _ELO_SCALE), _MIN_LAM), _MAX_LAM)

    ht1 = _half_probs(lam_h, lam_a)
    # 2nd half: 双方节奏都略降（领先方收缩 + 落后方前压相互抵消后的净效应）。
    # 这是足球 HTFT 模型的标准做法——半场完全独立会高估重复的进球率。
    ht2 = _half_probs(lam_h * 0.95, lam_a * 0.95)

    result: dict[str, float] = {}
    for ht_key, ht_p in ht1.items():
        for ft_key, ft_p in ht2.items():
            outcome = ht_key + ft_key
            result[outcome] = round(ht_p * ft_p, 4)

    sorted_outcomes = sorted(result.items(), key=lambda x: -x[1])

    return {
        "ht1_probs": ht1,
        "ht2_probs": ht2,
        "matrix": [["HH", "HD", "HA"], ["DH", "DD", "DA"], ["AH", "AD", "AA"]],
        "outcomes": result,
        "top3": sorted_outcomes[:3],
    }
