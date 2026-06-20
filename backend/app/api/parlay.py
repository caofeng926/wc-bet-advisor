"""串关构造器:贪心选 edge 高的 + 相关性惩罚"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.tz import now as now_bj

from app.db.database import get_db
from app.db.models import Match, Odd
from app.db.schemas import (
    ParlayCandidateOut, ParlayCandidatesOut,
    ParlayCalculateIn, ParlayCalculateOut,
)

router = APIRouter(prefix="/api/parlay", tags=["parlay"])


def _best_odds(db: Session, match_id: int, market: str, selection: str) -> float:
    rows = (
        db.query(Odd)
        .filter(Odd.match_id == match_id, Odd.market == market, Odd.selection == selection)
        .all()
    )
    if not rows:
        return 0
    return min(r.odds for r in rows)


def _model_probs(elo_diff: int) -> dict:
    """统一模型:与 seed 同源的概率估算
    返回归一化后的 H/D/A 概率
    """
    # 加主场加成
    expected_h = 1 / (1 + 10 ** (-(elo_diff + 80) / 400))
    expected_a = 1 - expected_h
    # 平局概率公式(同 seed)
    p_d = (1 - abs(2 * expected_h - 1)) * 0.30
    # 8% 下限(同 seed)
    if p_d < 0.08:
        p_d = 0.08
    s = expected_h + expected_a
    expected_h = expected_h / s * (1 - p_d)
    expected_a = expected_a / s * (1 - p_d)
    return {"H": expected_h, "D": p_d, "A": expected_a}


@router.get("/candidates", response_model=ParlayCandidatesOut)
def list_candidates(
    min_edge: float = Query(0.05),
    db: Session = Depends(get_db),
):
    """返回所有 edge >= 阈值的单注候选"""
    now = now_bj()
    matches = (
        db.query(Match)
        .filter(Match.status == "scheduled", Match.kickoff_at > now)
        .order_by(Match.kickoff_at.asc())
        .all()
    )
    out = []
    for m in matches:
        elo_diff = m.home.elo - m.away.elo
        probs = _model_probs(elo_diff)
        for sel in ["H", "D", "A"]:
            odds = _best_odds(db, m.id, "1x2", sel)
            if odds <= 1:
                continue
            p = probs[sel]
            edge = p * odds - 1
            if edge >= min_edge:
                out.append(ParlayCandidateOut(
                    match_id=m.id, home=m.home.iso3, away=m.away.iso3,
                    kickoff_at=m.kickoff_at.isoformat(),
                    group=m.group or "knockout",
                    kickoff_date=m.kickoff_at.date().isoformat(),
                    market="1x2", selection=sel,
                    odds=odds, p_final=round(p, 3), edge=round(edge, 3),
                    p_match=0,
                ))
        # 让球
        for sel, line, sign in [("H(-1)", -1, 1), ("A(+1)", 1, -1)]:
            odds = _best_odds(db, m.id, "ah", sel)
            if odds <= 1:
                continue
            # 让球后用 1.5x elo 差
            p = _model_probs(elo_diff * 1.5 * sign)["H" if sel.startswith("H") else "A"] * 0.7
            edge = p * odds - 1
            if edge >= min_edge:
                out.append(ParlayCandidateOut(
                    match_id=m.id, home=m.home.iso3, away=m.away.iso3,
                    kickoff_at=m.kickoff_at.isoformat(),
                    group=m.group or "knockout",
                    kickoff_date=m.kickoff_at.date().isoformat(),
                    market="ah", selection=sel,
                    odds=odds, p_final=round(p, 3), edge=round(edge, 3),
                    p_match=0,
                ))
    return ParlayCandidatesOut(candidates=out, min_edge=min_edge)


@router.post("/calculate", response_model=ParlayCalculateOut)
def calculate(payload: ParlayCalculateIn, db: Session = Depends(get_db)):
    if not payload.legs:
        return ParlayCalculateOut(
            total_odds=1, combined_prob=1, combined_edge=0,
            suggested_stake=0, expected_value=0,
            correlation_penalty=1, warnings=["未选中任何比赛"],
        )
    if len(payload.legs) > 6:
        return ParlayCalculateOut(
            total_odds=1, combined_prob=1, combined_edge=0,
            suggested_stake=0, expected_value=0,
            correlation_penalty=1, warnings=["最多支持6关"],
        )
    total_odds = 1.0
    combined_p = 1.0
    warnings: list[str] = []
    match_ids = [leg.match_id for leg in payload.legs]
    matches = {m.id: m for m in db.query(Match).filter(Match.id.in_(match_ids)).all()}
    penalty = 1.0
    for i, a in enumerate(payload.legs):
        for b in payload.legs[i + 1:]:
            ma, mb = matches.get(a.match_id), matches.get(b.match_id)
            if not ma or not mb:
                continue
            if ma.group and ma.group == mb.group and ma.stage == "group":
                penalty *= 0.85
                warnings.append(f"同组相关: {ma.home.iso3}vs{ma.away.iso3} 与 {mb.home.iso3}vs{mb.away.iso3}")
            time_diff = abs((ma.kickoff_at - mb.kickoff_at).total_seconds())
            if time_diff < 6 * 3600:
                penalty *= 0.92
    for leg in payload.legs:
        total_odds *= leg.odds
        combined_p *= 1 / leg.odds
    combined_p = combined_p * (2 - penalty)
    combined_edge = combined_p * total_odds - 1
    if combined_edge > 0:
        k = min(combined_edge * payload.kelly_fraction, 0.10)
    else:
        k = 0
    suggested_stake = round(payload.bankroll * k, 2)
    ev = round(combined_p * suggested_stake * (total_odds - 1) - (1 - combined_p) * suggested_stake, 2)
    return ParlayCalculateOut(
        total_odds=round(total_odds, 2),
        combined_prob=round(combined_p, 4),
        combined_edge=round(combined_edge, 3),
        suggested_stake=suggested_stake,
        expected_value=ev,
        correlation_penalty=round(penalty, 3),
        warnings=warnings[:5],
    )
