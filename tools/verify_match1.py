"""对比 模型预测 vs MEX vs RSA 真实结果

Usage:
  python tools/verify_match1.py
  python tools/verify_match1.py --home 2 --away 1
  python tools/verify_match1.py --home 0 --away 0 --status ft --record

The snapshot is read from backend/data/snapshots/match1_mex_vs_rsa.json
(由 W3 修完模型时生成，模型版本: poisson+htft 11x11, recommendations ELO-driven).

输出全部中文。在 Windows GBK 控制台也能正常运行。
"""

import argparse
import io
import json
import sys
from pathlib import Path

# Windows GBK 控制台兼容：把 stdout 强制成 utf-8
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = sys.stdout

SNAPSHOT_PATH = Path(__file__).parent.parent / "backend" / "data" / "snapshots" / "match1_mex_vs_rsa.json"


def load_snapshot():
    with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_actual_from_db():
    """如果 DB 里已经录入过结果（ft_home / ft_away 不为 null），返回 (ft_home, ft_away, status)。"""
    sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
    try:
        from app.db.database import SessionLocal
        from app.db.models import Match
        db = SessionLocal()
        m = db.query(Match).filter(Match.id == 1).first()
        db.close()
        if m and m.ft_home is not None and m.ft_away is not None:
            return (m.ft_home, m.ft_away, m.status)
    except Exception as e:
        print(f"  （读取数据库失败：{e}）")
    return None


def determine_1x2(home: int, away: int) -> str:
    if home > away:
        return "主胜"
    if home < away:
        return "客胜"
    return "平局"


def main():
    parser = argparse.ArgumentParser(description="对比 MEX vs RSA 模型预测与真实结果")
    parser.add_argument("--home", type=int, help="主队最终进球数（例 2）")
    parser.add_argument("--away", type=int, help="客队最终进球数（例 1）")
    parser.add_argument("--status", default="ft", choices=["ft", "postponed", "cancelled", "live"],
                        help="比赛状态（默认 ft）")
    parser.add_argument("--record", action="store_true", help="把结果写回数据库")
    args = parser.parse_args()

    snap = load_snapshot()
    m = snap["matches"][0]

    print("=" * 64)
    print(f"  模型预测 vs 真实结果  ·  Match 1  开幕战")
    print(f"  {m['home']} vs {m['away']}   2026-06-11 21:00 北京时间")
    print(f"  ELO：{m['home_elo']} vs {m['away_elo']}   λ：{m['lambda_home']} / {m['lambda_away']}")
    print("=" * 64)
    print(f"  快照生成时间：{snap['snapshot_at']}")
    print(f"  模型版本：{snap.get('model_version', 'unknown')}")
    print()

    print("┌─── 预测 ─────────────────────────────────────────────┐")
    print(f"  1x2：  主胜 {m['p_1x2']['H']*100:.1f}%   平 {m['p_1x2']['D']*100:.1f}%   客胜 {m['p_1x2']['A']*100:.1f}%")
    print(f"  模型主推：{max(m['p_1x2'], key=m['p_1x2'].get)}（{max(m['p_1x2'].values())*100:.1f}%）")
    print(f"  Top 3 比分：{[s for s,_ in m['top_scores'][:3]]}")
    print(f"  半全场 Top 3：{[o for o,_ in m['htft_top3']]}")
    print(f"  赔率（主/平/客）：{m['odds_1x2']['H']} / {m['odds_1x2']['D']} / {m['odds_1x2']['A']}")
    print("└──────────────────────────────────────────────────────┘")
    print()

    print("┌─── Value Bets（模型认为有数学优势的注） ───────────┐")
    print(f"  {'玩法':<10} {'选项':<8} {'赔率':<6} {'p_final':<8} {'edge':<8} {'评价'}")
    for vb in m["value_bets"]:
        eval_str = "有推荐价值" if vb["edge"] > 0.05 else "赔率偏低无价值"
        print(f"  {vb['market']:<10} {vb['selection']:<8} {vb['odds']:<6.2f} {vb['p_final']:<8.4f} {vb['edge']:<+8.3f} {eval_str}")
    print("└──────────────────────────────────────────────────────┘")
    print()

    if args.home is not None and args.away is not None:
        actual = (args.home, args.away, args.status)
    else:
        db_actual = load_actual_from_db()
        if db_actual is None:
            print("⚠️  还没有真实结果。请赛后运行：")
            print("    python tools/verify_match1.py --home <主队进球> --away <客队进球> [--status ft]")
            print("    例：python tools/verify_match1.py --home 2 --away 0")
            print()
            print("或者先在后端 /admin 里录入结果，再重跑本脚本。")
            return
        actual = db_actual

    home, away, status = actual
    actual_1x2 = determine_1x2(home, away)
    print("=" * 64)
    print(f"  真实结果：{m['home']} {home} - {away} {m['away']}    状态：{status}")
    print(f"  1x2 归类：{actual_1x2}")
    print("=" * 64)
    print()

    pred_1x2_key = max(m["p_1x2"], key=m["p_1x2"].get)
    pred_1x2_cn = {"H": "主胜", "D": "平", "A": "客胜"}[pred_1x2_key]
    hit_1x2 = (pred_1x2_key == {"主胜": "H", "平局": "D", "客胜": "A"}[actual_1x2])
    print(f"· 1x2 模型主推：{pred_1x2_cn}  |  真实：{actual_1x2}  |  {'✅ 命中' if hit_1x2 else '❌ 未中'}")
    print()

    top_score = m["top_scores"][0][0]
    actual_score = f"{home}-{away}"
    hit_score = (top_score == actual_score)
    print(f"· 最高概率比分：{top_score}  |  真实：{actual_score}  |  {'✅ 命中' if hit_score else '❌ 未中'}")
    top3_scores = [s for s,_ in m["top_scores"][:3]]
    if actual_score in top3_scores and not hit_score:
        print(f"  （实际比分落在 Top 3，第 {top3_scores.index(actual_score)+1} 位）")
    print()

    print("· Value Bets 盈亏（每注 100 元）：")
    pnl_total = 0
    for vb in m["value_bets"]:
        sel = vb["selection"]
        won = False
        if vb["market"] == "1x2":
            won = (sel == {"主胜": "H", "平局": "D", "客胜": "A"}[actual_1x2])
        elif vb["market"] == "ah":
            sign = sel[0]
            try:
                line = int(sel[2:].rstrip(")"))
            except (ValueError, IndexError):
                continue
            if sign == "H":
                won = (home - away > -line)
            elif sign == "A":
                won = (away - home > -line)
            elif sign == "D":
                won = (home - away == -line)
        pnl = 100 * (vb["odds"] - 1) if won else -100
        pnl_total += pnl if vb["edge"] > 0.05 else 0
        verdict = "✅ 中" if won else "❌ 未中"
        print(f"  {vb['market']:<6} {sel:<8} {verdict}  盈亏={pnl:+.0f}元")
    print(f"  按 edge>5% 筛选后总盈亏：{pnl_total:+.0f}元")
    print()

    if args.record and (args.home is not None and args.away is not None):
        sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
        from app.db.database import SessionLocal
        from app.db.models import Match
        db = SessionLocal()
        m_db = db.query(Match).filter(Match.id == 1).first()
        m_db.ft_home = args.home
        m_db.ft_away = args.away
        m_db.status = args.status
        db.commit()
        db.close()
        print(f"✅ 已写入数据库：{m['home']} {home} - {away} {m['away']}  状态：{args.status}")


if __name__ == "__main__":
    main()
