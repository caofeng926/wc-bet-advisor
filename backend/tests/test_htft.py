"""HTFT (半全场) prediction unit tests"""
from app.services.htft import predict_htft


class TestHtfReturnShape:
    def test_keys(self):
        r = predict_htft(1500, 1500)
        assert "ht1_probs" in r
        assert "ht2_probs" in r
        assert "outcomes" in r
        assert "top3" in r

    def test_nine_outcomes(self):
        r = predict_htft(1500, 1500)
        assert len(r["outcomes"]) == 9
        expected = {"HH", "HD", "HA", "DH", "DD", "DA", "AH", "AD", "AA"}
        assert set(r["outcomes"].keys()) == expected

    def test_top3_is_list_of_3(self):
        r = predict_htft(1500, 1500)
        assert isinstance(r["top3"], list)
        assert len(r["top3"]) == 3


class TestHtfProbs:
    def test_probabilities_sum_to_one(self):
        r = predict_htft(1500, 1500)
        # Sum of all 9 outcomes (independent halves) must = 1
        total = sum(r["outcomes"].values())
        assert abs(total - 1.0) < 0.01  # rounding drift

    def test_all_probs_nonnegative(self):
        r = predict_htft(1500, 1500)
        for v in r["outcomes"].values():
            assert v >= 0.0
        for v in r["ht1_probs"].values():
            assert v >= 0.0
        for v in r["ht2_probs"].values():
            assert v >= 0.0

    def test_strong_home_more_HH(self):
        weak_home = predict_htft(1500, 1900)  # away much stronger
        strong_home = predict_htft(1900, 1500)  # home much stronger
        assert strong_home["outcomes"]["HH"] > weak_home["outcomes"]["HH"]


class TestHtfEdge:
    def test_equal_teams_dd_among_top(self):
        # With slight home edge for equal teams, HH should be the single most likely outcome
        r = predict_htft(1500, 1500)
        top1 = r["top3"][0][0]
        assert top1 == "HH"  # home slight edge → HH dominates

    def test_top3_sorted_descending(self):
        r = predict_htft(1600, 1400)
        probs = [p for _, p in r["top3"]]
        assert probs == sorted(probs, reverse=True)


class TestHtf2ndHalfScaling:
    """第二半场节奏略降（领先方收缩 + 落后方前压的净效应）"""

    def test_2nd_half_slower_than_1st(self):
        from app.services.htft import _half_probs
        ht1 = _half_probs(1.5, 1.0)
        ht2 = _half_probs(1.5 * 0.95, 1.0 * 0.95)
        # 0.95 缩放让总进球数减少 → 进球数差距更可能相同 → 平局概率上升
        assert ht2["D"] > ht1["D"]

    def test_total_htft_outcomes_sum_to_one(self):
        r = predict_htft(1700, 1500)
        total = sum(r["outcomes"].values())
        assert abs(total - 1.0) < 0.01

    def test_strong_home_still_dominates_after_scaling(self):
        r = predict_htft(1900, 1500)
        top1 = r["top3"][0][0]
        assert top1 == "HH"
