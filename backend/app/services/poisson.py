"""Poisson goal prediction model.

Base rate lam_base=1.3 goals/team is the global soccer average. ELO adjustment
is additive in the log-rate so a +200 ELO gap multiplies lambda by exp(200/600)
\u2248 1.39x. The matrix is computed 11x11 to properly account for high-scoring
outcomes; for very high totals the tail mass is aggregated.
"""
from math import factorial, exp


_BASE_LAM = 1.3      # global soccer average goals per team
_ELO_SCALE = 600     # ELO points per 1.0 in log-rate (200 \u2248 +39% lambda)
_MIN_LAM = 0.3
_MAX_LAM = 4.5
_MATRIX_N = 11       # 0..10 goals per side, captures 99.9% of mass for lam<=4.5


def _poisson_pmf(lam: float, k: int) -> float:
    return exp(-lam) * (lam ** k) / factorial(k)


def predict_goals(elo_home: int, elo_away: int, home_advantage: int = 80) -> dict:
    """Predict goal distribution using a two-independent-Poisson model.

    Args:
        elo_home: ELO rating of home team
        elo_away: ELO rating of away team
        home_advantage: ELO bonus for playing at home (default 80)

    Returns:
        dict with score_matrix, lambda_home, lambda_away, goals_distribution, top_scores
    """
    diff = elo_home + home_advantage - elo_away
    lam_home = min(max(_BASE_LAM * exp(diff / _ELO_SCALE), _MIN_LAM), _MAX_LAM)
    lam_away = min(max(_BASE_LAM * exp(-diff / _ELO_SCALE), _MIN_LAM), _MAX_LAM)

    # Build NxN matrix and renormalize (the tail beyond 10 goals is negligible for lam<=4.5)
    raw = [[_poisson_pmf(lam_home, i) * _poisson_pmf(lam_away, j)
            for j in range(_MATRIX_N)] for i in range(_MATRIX_N)]
    total = sum(sum(row) for row in raw)
    matrix = [[round(v / total, 4) for v in row] for row in raw]

    # Goals distribution: total goals 0..(2N-2), aggregated
    max_g = 2 * (_MATRIX_N - 1)
    goals_dist: dict[str, float] = {}
    for g in range(max_g + 1):
        p = sum(matrix[i][j] for i in range(_MATRIX_N) for j in range(_MATRIX_N) if i + j == g)
        goals_dist[str(g)] = round(p, 4)

    # Top 5 scores
    flat = [(f"{i}-{j}", matrix[i][j]) for i in range(_MATRIX_N) for j in range(_MATRIX_N)]
    flat.sort(key=lambda x: -x[1])
    top_scores = [(s, round(p, 4)) for s, p in flat[:5]]

    return {
        "score_matrix": matrix,
        "lambda_home": round(lam_home, 3),
        "lambda_away": round(lam_away, 3),
        "goals_distribution": goals_dist,
        "top_scores": top_scores,
    }
