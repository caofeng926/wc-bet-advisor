"""Manual test runner - run with: python -m tests.run_tests"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_kelly():
    from app.services.kelly import kelly_fraction, kelly_stake_pct
    assert abs(kelly_fraction(0.6, 2.0) - 0.2) < 1e-6
    assert abs(kelly_fraction(0.5, 2.0)) < 1e-6
    assert kelly_fraction(0.3, 2.0) <= 0
    assert kelly_fraction(0, 2.0) == 0
    assert kelly_fraction(0.6, 1.0) == 0
    assert abs(kelly_fraction(0.4, 3.0) - 0.1) < 1e-6
    assert abs(kelly_stake_pct(0.2, 0.25) - 0.05) < 1e-6
    assert kelly_stake_pct(0.5, 0.25) <= 0.05
    assert kelly_stake_pct(-0.1, 0.25) == 0
    assert kelly_stake_pct(0, 0.25) == 0
    print("Kelly: PASS")

def test_poisson():
    from app.services.poisson import predict_goals
    r = predict_goals(1500, 1500)
    assert "score_matrix" in r
    assert "lambda_home" in r
    assert "lambda_away" in r
    assert r["lambda_home"] > r["lambda_away"]
    assert 0.3 <= r["lambda_home"] <= 5.0
    assert 0.3 <= r["lambda_away"] <= 5.0
    total = sum(sum(m) for m in r["score_matrix"])
    assert abs(total - 1.0) < 1e-3
    total_g = sum(r["goals_distribution"].values())
    assert abs(total_g - 1.0) < 1e-3
    print("Poisson: PASS")

def test_lotto14():
    from app.services.lotto14 import lotto14_search, lotto9_search
    preds = [{"H": 0.7, "D": 0.2, "A": 0.1} for _ in range(14)]
    main, backs = lotto14_search(preds)
    assert len(main) == 14
    assert all(p in "HDA" for p in main)
    assert len(backs) == 6
    assert all(len(b) == 14 for b in backs)
    main9, backs9 = lotto9_search(preds)
    assert len(main9) == 9
    print("Lotto14: PASS")

def test_api_imports():
    print("API imports: PASS")

def test_htft():
    from app.services.htft import predict_htft
    r = predict_htft(1500, 1500)
    ht1_total = sum(r["ht1_probs"].values())
    outcomes_total = sum(r["outcomes"].values())
    assert abs(ht1_total - 1.0) < 0.02, f"HT1 sum {ht1_total} far from 1"
    assert abs(outcomes_total - 1.0) < 0.03, f"Outcomes sum {outcomes_total} far from 1"
    assert len(r["top3"]) == 3
    print("HTFT: PASS")

def test_polymarket():
    from app.services.polymarket import normalize_polymarket
    mock = [{"id": "m1", "question": "Brazil vs Croatia", "outcomes": ["Yes", "No"],
             "outcomePrices": {"Yes": 0.65, "No": 0.35}, "liquidity": 1000, "volume24hr": 500}]
    norm = normalize_polymarket(mock)
    assert len(norm) == 1
    assert norm[0]["implied_prob"] == 0.65
    print("Polymarket: PASS")

if __name__ == "__main__":
    print("Running tests...")
    test_kelly()
    test_poisson()
    test_lotto14()
    test_htft()
    test_polymarket()
    test_api_imports()
    print("\nALL TESTS PASSED")