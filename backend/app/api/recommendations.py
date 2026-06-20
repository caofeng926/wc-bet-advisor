from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.tz import now as now_bj

from app.db.database import get_db
from app.db.models import Match
from app.services.poisson import predict_goals

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


def _p_1x2(elo_home: int, elo_away: int) -> dict[str, float]:
    """用泊松从 ELO 推算 H/D/A 概率"""
    p = predict_goals(elo_home, elo_away)
    matrix = p["score_matrix"]
    pH = pD = pA = 0.0
    for i in range(6):
        for j in range(6):
            if i > j:
                pH += matrix[i][j]
            elif i < j:
                pA += matrix[i][j]
            else:
                pD += matrix[i][j]
    return {"H": pH, "D": pD, "A": pA}


def _p_for_selection(elo_home: int, elo_away: int, market: str, selection: str) -> float:
    """根据玩法和选项返回模型概率"""
    p123 = _p_1x2(elo_home, elo_away)
    if market == "1x2":
        return p123.get(selection, 0.0)

    # 让球胜平负 (AH): selection 形如 "H(-1)" / "A(+1)" / "D(-1)"
    if market == "ah":
        p = predict_goals(elo_home, elo_away)
        matrix = p["score_matrix"]
        if selection.startswith("H("):
            line = int(selection[2:].rstrip(")"))
            return sum(matrix[i][j] for i in range(6) for j in range(6) if i - j > -line)
        if selection.startswith("A("):
            line = int(selection[2:].rstrip(")"))
            return sum(matrix[i][j] for i in range(6) for j in range(6) if j - i > -line)
        if selection.startswith("D("):
            line = int(selection[2:].rstrip(")"))
            return sum(matrix[i][j] for i in range(6) for j in range(6) if i - j == -line)

    # 默认退回到 1x2
    return p123.get(selection, 0.0)


def _value_bets_for_match(match: Match) -> List[Dict[str, Any]]:
    """对一场比赛的所有市场算 edge。1x2 和 AH 用 ELO+泊松，其它市场跳过。"""
    out = []
    for o in match.odds:
        if o.bookmaker != "手工-A":
            continue
        if o.market not in ("1x2", "ah"):
            continue
        p_final = _p_for_selection(match.home.elo, match.away.elo, o.market, o.selection)
        if p_final <= 0:
            continue
        p_mkt = 1 / o.odds
        edge = p_final * o.odds - 1
        if edge > 0.05:
            b = max(o.odds - 1, 0.01)
            kelly = max(0.0, (p_final * o.odds - (1 - p_final)) / b * 0.25)
            out.append({
                "match_id": match.id,
                "home": match.home.name_zh,
                "away": match.away.name_zh,
                "kickoff_at": match.kickoff_at.isoformat(),
                "minutes_to_close": int((match.betting_close_at - now_bj()).total_seconds() / 60) if match.betting_close_at else None,
                "market": o.market,
                "selection": o.selection,
                "odds": o.odds,
                "p_market": round(p_mkt, 3),
                "p_final": round(p_final, 3),
                "edge": round(edge, 3),
                "kelly": round(kelly, 4),
            })
    return out


@router.get("/today", response_model=List[Dict[str, Any]])
def today_recommendations(
    min_edge: float = Query(0.05, ge=0, le=1),
    market: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """今日推荐池。所有 edge >= min_edge 的单注。"""
    now = now_bj()
    matches = (
        db.query(Match)
        .filter(Match.betting_close_at > now)
        .order_by(Match.kickoff_at.asc())
        .limit(limit * 2)
        .all()
    )
    items: List[Dict[str, Any]] = []
    for m in matches:
        for vb in _value_bets_for_match(m):
            if vb["edge"] < min_edge:
                continue
            if market and vb["market"] != market:
                continue
            items.append(vb)
        if len(items) >= limit:
            break
    return items[:limit]


@router.get("/parlay-candidates", response_model=List[Dict[str, Any]])
def parlay_candidates(
    min_edge: float = Query(0.05, ge=0, le=1),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
):
    """串关候选：单注 edge 高的场次，且分散在不同小组/日期。"""
    now = now_bj()
    matches = (
        db.query(Match)
        .filter(Match.betting_close_at > now)
        .order_by(Match.kickoff_at.asc())
        .all()
    )
    candidates = []
    seen_groups = set()
    seen_dates = set()
    for m in matches:
        vb_list = _value_bets_for_match(m)
        if not vb_list:
            continue
        for vb in vb_list:
            if vb["edge"] < min_edge:
                continue
            grp = m.group or "knockout"
            date = m.kickoff_at.date().isoformat()
            if grp in seen_groups and date in seen_dates:
                continue
            candidates.append({
                **vb,
                "group": grp,
                "kickoff_date": date,
            })
            seen_groups.add(grp)
            seen_dates.add(date)
        if len(candidates) >= limit:
            break
    return candidates[:limit]


@router.get("/poisson/{match_id}", response_model=Dict[str, Any])
def poisson_prediction(match_id: int, db: Session = Depends(get_db)):
    """基于泊松的比分 / 总进球预测。"""
    m = db.query(Match).filter(Match.id == match_id).first()
    if not m:
        raise HTTPException(404, "比赛不存在")
    result = predict_goals(m.home.elo, m.away.elo)
    result["match_id"] = m.id
    result["home"] = m.home.name_zh
    result["away"] = m.away.name_zh
    return result


@router.get("/htft/{match_id}", response_model=Dict[str, Any])
def htft_prediction(match_id: int, db: Session = Depends(get_db)):
    """半全场预测，基于两段泊松模型。"""
    m = db.query(Match).filter(Match.id == match_id).first()
    if not m:
        raise HTTPException(404, "比赛不存在")
    from app.services.htft import predict_htft
    result = predict_htft(m.home.elo, m.away.elo)
    result["match_id"] = m.id
    result["home"] = m.home.name_zh
    result["away"] = m.away.name_zh
    return result
