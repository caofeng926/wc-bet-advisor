"""
MEX vs RSA 赛后回测模板

用法:
1. 等 FIFA 官方公布 MEX vs RSA 真实比分 (预计 2026-06-13 早上 5 点后)
2. 把真实比分填到 RESULT_H / RESULT_A 两个变量
3. 跑脚本: python tests/test_backtest_mex_rsa.py

本模板会:
- 加载 W3 收尾时的预测快照
- 对比预测 vs 真实结果
- 计算 Brier score, 命中率, ROI
"""
import json
import io
import sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = sys.stdout

# 真实结果占位 - 比赛结束后填入
RESULT_H = None
RESULT_A = None

SNAPSHOT_PATH = Path(__file__).parent.parent / "data" / "snapshots" / "match1_mex_vs_rsa.json"
with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
    SNAP = json.load(f)
MATCH = SNAP["matches"][0]


def _outcome(h, a):
    if h > a:
        return "H"
    if h < a:
        return "A"
    return "D"


def _score_str(h, a):
    return f"{h}-{a}"


def _brier(probs, actual):
    return sum((probs[k] - actual[k]) ** 2 for k in probs)


def run_backtest():
    print("=" * 70)
    print("MEX vs RSA 赛后回测")
    print("=" * 70)
    print(f"  快照时间: {SNAP['snapshot_at']}")
    print(f"  模型版本: {SNAP['model_version']}")
    print(f"  比赛: {MATCH['home']} vs {MATCH['away']}")
    print(f"  开赛: {MATCH['kickoff_at']}")
    print()

    if RESULT_H is None or RESULT_A is None:
        print("[PENDING] 真实结果未填入 (RESULT_H / RESULT_A)")
        print()
        print("请在比赛结束后修改本脚本顶部:")
        print("  RESULT_H = ?  # 主场进球 (MEX)")
        print("  RESULT_A = ?  # 客场进球 (RSA)")
        print("然后重跑: python tests/test_backtest_mex_rsa.py")
        print()
        print("=" * 70)
        print("当前模型预测摘要 (等待真实结果验证)")
        print("=" * 70)
        print()
        print(f"  1x2:  H={MATCH['p_1x2']['H']:.3f}  D={MATCH['p_1x2']['D']:.3f}  A={MATCH['p_1x2']['A']:.3f}")
        print(f"  Top 5 比分: {MATCH['top_scores']}")
        print(f"  HTFT Top 3: {MATCH['htft_top3']}")
        print()
        print(f"  市场赔率: H={MATCH['odds_1x2']['H']}  D={MATCH['odds_1x2']['D']}  A={MATCH['odds_1x2']['A']}")
        best_vb = max(MATCH['value_bets'], key=lambda x: x['edge'])
        print(f"  价值最大: {best_vb}")
        return

    # 有真实结果
    print(f"  真实结果: {MATCH['home']} {RESULT_H} - {RESULT_A} {MATCH['away']}")
    print(f"  真实 1x2: {_outcome(RESULT_H, RESULT_A)}")
    print()

    actual = {"H": 0, "D": 0, "A": 0}
    actual[_outcome(RESULT_H, RESULT_A)] = 1
    brier = _brier(MATCH["p_1x2"], actual)
    print(f"  1x2 Brier Score: {brier:.4f}  (0=完美, 2=最差, <0.5=好)")

    real_score = _score_str(RESULT_H, RESULT_A)
    in_top5 = any(s == real_score for s, _ in MATCH["top_scores"])
    if in_top5:
        idx = next(i for i, (s, _) in enumerate(MATCH["top_scores"]) if s == real_score)
        print(f"  [OK] 真实比分 {real_score} 在 Top 5 (排名 #{idx+1})")
    else:
        print(f"  [MISS] 真实比分 {real_score} 不在 Top 5")

    print()
    print("  --- 价值投注结算 ---")
    total_pnl = 0
    for vb in MATCH["value_bets"]:
        mkt, sel, odds = vb["market"], vb["selection"], vb["odds"]
        won = False
        if mkt == "1x2":
            if sel == "H":
                won = RESULT_H > RESULT_A
            elif sel == "D":
                won = RESULT_H == RESULT_A
            elif sel == "A":
                won = RESULT_H < RESULT_A
        elif mkt == "ah":
            if sel.startswith("H("):
                line = int(sel[2:].rstrip(")"))
                won = (RESULT_H - RESULT_A) > -line
            elif sel.startswith("A("):
                line = int(sel[2:].rstrip(")"))
                won = (RESULT_A - RESULT_H) > -line
        pnl = (odds - 1) if won else -1
        total_pnl += pnl
        status = "WIN" if won else "LOSE"
        print(f"    {mkt:5} {sel:8} @{odds:5}  edge={vb['edge']:+.3f}  -> {status} (pnl={pnl:+.2f}u)")
    print(f"  总 PnL: {total_pnl:+.2f}u (假设每注 1u)")
    print("=" * 70)


if __name__ == "__main__":
    run_backtest()
