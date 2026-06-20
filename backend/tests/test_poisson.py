"""Poisson goal model unit tests"""
from app.services.poisson import predict_goals


class TestPoissonPredictGoals:
    def test_return_type(self):
        result = predict_goals(1500, 1500)
        assert isinstance(result, dict)
        assert "score_matrix" in result
        assert "lambda_home" in result
        assert "lambda_away" in result

    def test_lambda_home_stronger(self):
        # Home team stronger (higher ELO) → lambda_home > lambda_away
        result = predict_goals(1600, 1400)
        assert result["lambda_home"] > result["lambda_away"]

    def test_lambda_away_stronger(self):
        result = predict_goals(1400, 1600)
        assert result["lambda_away"] > result["lambda_home"]

    def test_equal_teams(self):
        # Equal ELO → lambdas should be close (home advantage makes home slightly higher)
        result = predict_goals(1500, 1500)
        # lambda_home should be slightly higher due to home_advantage
        assert result["lambda_home"] > result["lambda_away"]

    def test_lambdas_in_range(self):
        result = predict_goals(1500, 1500)
        assert 0.3 <= result["lambda_home"] <= 4.5
        assert 0.3 <= result["lambda_away"] <= 4.5

    def test_score_matrix_sum(self):
        result = predict_goals(1500, 1500)
        matrix = result["score_matrix"]
        total = sum(sum(row) for row in matrix)
        assert abs(total - 1.0) < 0.01  # rounding to 4 decimals introduces small drift in an 11x11 matrix

    def test_goals_distribution_sum(self):
        result = predict_goals(1500, 1500)
        dist = result["goals_distribution"]
        total = sum(dist.values())
        assert abs(total - 1.0) < 0.01  # rounded to 4 decimals


class TestGoalsDistribution:
    def test_0_goals_possible(self):
        result = predict_goals(1500, 1500)
        dist = result["goals_distribution"]
        assert "0" in dist
        assert dist["0"] > 0

    def test_high_goals_rare(self):
        result = predict_goals(1500, 1500)
        dist = result["goals_distribution"]
        # 6+ total goals should be relatively rare
        p6plus = sum(dist[str(g)] for g in range(6, 11))
        assert p6plus < 0.3

    def test_most_common_1_2_goals(self):
        result = predict_goals(1500, 1500)
        dist = result["goals_distribution"]
        # 1 or 2 total goals should be most likely for equal teams
        assert dist["1"] + dist["2"] > dist["0"]


class TestScoreMatrix:
    def test_matrix_shape(self):
        result = predict_goals(1500, 1500)
        matrix = result["score_matrix"]
        assert len(matrix) == 11  # 0-10 goals per side
        assert all(len(row) == 11 for row in matrix)

    def test_diagonal_symmetry(self):
        # For equal teams, off-diagonal should be similar
        result = predict_goals(1500, 1500)
        matrix = result["score_matrix"]
        # 1-0 and 0-1 should be similar
        assert abs(matrix[1][0] - matrix[0][1]) < 0.05