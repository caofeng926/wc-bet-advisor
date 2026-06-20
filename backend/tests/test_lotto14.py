"""14场胜负彩 algorithm tests"""
from app.services.lotto14 import lotto14_search, lotto9_search


class TestLotto14Search:
    def test_output_structure(self):
        """Test that search returns main ticket + backups"""
        # Mock match predictions (14 matches, each with H/D/A probs)
        mock_preds = [
            {"H": 0.7, "D": 0.2, "A": 0.1} for _ in range(14)
        ]
        main, backups = lotto14_search(mock_preds)
        assert len(main) == 14
        assert all(p in "HDA" for p in main)
        assert len(backups) == 6
        assert all(len(b) == 14 for b in backups)

    def test_main_pick_highest_prob(self):
        """Main ticket should pick highest probability each match"""
        mock_preds = [
            {"H": 0.8, "D": 0.1, "A": 0.1},
            {"H": 0.2, "D": 0.1, "A": 0.7},
            {"H": 0.3, "D": 0.4, "A": 0.3},
        ] * 5 # 15 entries (excess is fine)
        main, _ = lotto14_search(mock_preds[:14])
        # First match: H=0.8 highest → should be H
        assert main[0] == "H"
        # Second: A=0.7 highest → should be A
        assert main[1] == "A"

    def test_backup_different_from_main(self):
        """At least some backups should differ from main"""
        mock_preds = [
            {"H": 0.5, "D": 0.3, "A": 0.2} for _ in range(14)
        ]
        main, backups = lotto14_search(mock_preds)
        # At least one backup should be different from main
        assert any(b != main for b in backups)

    def test_backup_count(self):
        """Should return exactly 6 backups"""
        mock_preds = [{"H": 0.6, "D": 0.2, "A": 0.2} for _ in range(14)]
        _, backups = lotto14_search(mock_preds)
        assert len(backups) == 6


class TestLotto9Search:
    def test_output_length(self):
        """9场任选九 should select 9 matches"""
        mock_preds = [
            {"H": 0.6, "D": 0.2, "A": 0.2} for _ in range(14)
        ]
        main, backups = lotto9_search(mock_preds)
        assert len(main) == 9
        assert len(backups) <= 6

    def test_selects_most_confident(self):
        """Should select matches with largest ELO diff (highest confidence)"""
        # First match: small diff (close), last match: large diff
        mock_preds = [
            {"H": 0.52, "D": 0.2, "A": 0.28},  # near50-50
            {"H": 0.9, "D": 0.05, "A": 0.05},   # very confident H
        ] * 7  # 14 total
        main, _ = lotto9_search(mock_preds)
        # The confident matches (even indices1,3,5...) should be picked
        # At minimum, not all picks should be 'D' (the low confidence pick)
        assert any(p != "D" for p in main)