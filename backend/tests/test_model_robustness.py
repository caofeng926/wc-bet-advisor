"""模型健壮性测试: 强/弱/平 ELO 下的概率合理性"""
from app.services.poisson import predict_goals
from app.services.htft import predict_htft


def _p_1x2_from_matrix(eh: int, ea: int) -> tuple[float, float, float]:
    p = predict_goals(eh, ea)
    m = p["score_matrix"]
    pH = pD = pA = 0.0
    n = len(m)
    for i in range(n):
        for j in range(n):
            if i > j:
                pH += m[i][j]
            elif i < j:
                pA += m[i][j]
            else:
                pD += m[i][j]
    return pH, pD, pA


class TestPoisson1x2:
    def test_strong_home_huge_edge(self):
        pH, pD, pA = _p_1x2_from_matrix(2120, 1610)
        assert pH > 0.85, f"ARG 主场胜率应>0.85, 实际 {pH:.3f}"
        assert pA < 0.05, f"NZL 客场胜率应<0.05, 实际 {pA:.3f}"

    def test_strong_away_huge_edge(self):
        pH, pD, pA = _p_1x2_from_matrix(1610, 2120)
        assert pA > 0.75, f"ARG 客场胜率应>0.75, 实际 {pA:.3f}"
        assert pH < 0.10, f"NZL 主场胜率应<0.10, 实际 {pH:.3f}"

    def test_equal_elo_draw_reasonable(self):
        pH, pD, pA = _p_1x2_from_matrix(1800, 1800)
        assert 0.20 <= pD <= 0.30, f"平局概率应在 [0.20, 0.30], 实际 {pD:.3f}"
        assert pH > pA, f"同 ELO 下主场应略胜: H={pH:.3f} A={pA:.3f}"

    def test_near_equal_elo_balanced(self):
        pH, pD, pA = _p_1x2_from_matrix(1870, 1920)
        assert 0.30 < pH < 0.50
        assert 0.20 < pD < 0.30
        assert 0.25 < pA < 0.45

    def test_mex_vs_rsa_first_match(self):
        pH, pD, pA = _p_1x2_from_matrix(1820, 1640)
        assert pH > 0.55, f"MEX 主场应 > 0.55, 实际 {pH:.3f}"
        assert pA < 0.20, f"RSA 客场应 < 0.20, 实际 {pA:.3f}"

    def test_probability_sum_to_one(self):
        for eh, ea in [(2120, 1610), (1610, 2120), (1870, 1920), (1800, 1800), (1640, 1780), (2090, 1920)]:
            pH, pD, pA = _p_1x2_from_matrix(eh, ea)
            total = pH + pD + pA
            assert abs(total - 1.0) < 0.01, f"({eh},{ea}) sum={total:.3f}"


class TestPoissonLambdas:
    def test_lambda_stronger_team_higher(self):
        p = predict_goals(2000, 1700)
        assert p["lambda_home"] > p["lambda_away"]

    def test_lambda_realistic_range(self):
        for eh, ea in [(2000, 1500), (1500, 2000), (1800, 1800)]:
            p = predict_goals(eh, ea)
            assert 0.3 <= p["lambda_home"] <= 5.0
            assert 0.3 <= p["lambda_away"] <= 5.0

    def test_matrix_is_11x11(self):
        p = predict_goals(1800, 1800)
        assert len(p["score_matrix"]) == 11
        for row in p["score_matrix"]:
            assert len(row) == 11

    def test_home_advantage_creates_gap(self):
        p = predict_goals(1800, 1800)
        gap = p["lambda_home"] - p["lambda_away"]
        assert 0.2 <= gap <= 0.5, f"主场优势 gap 应在 [0.2, 0.5], 实际 {gap:.3f}"


class TestHTFTOutcomes:
    def test_has_9_outcomes(self):
        h = predict_htft(1800, 1800)
        assert len(h["outcomes"]) == 9

    def test_sum_to_one(self):
        h = predict_htft(1800, 1800)
        total = sum(h["outcomes"].values())
        assert abs(total - 1.0) < 0.01

    def test_strong_home_favors_HH(self):
        h = predict_htft(2120, 1610)
        best = max(h["outcomes"].items(), key=lambda x: x[1])
        assert best[0] in ("HH", "HD"), f"强主场 best 应 HH/HD, 实际 {best[0]}={best[1]:.3f}"

    def test_strong_away_favors_AA(self):
        h = predict_htft(1610, 2120)
        best = max(h["outcomes"].items(), key=lambda x: x[1])
        assert best[0] in ("AA", "AD"), f"强客场 best 应 AA/AD, 实际 {best[0]}={best[1]:.3f}"
