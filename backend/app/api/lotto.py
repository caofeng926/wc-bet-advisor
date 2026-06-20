"""14 场胜负彩 + 任选九 期号与推荐生成"""
from datetime import datetime
from app.db.tz import now as now_bj
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Match, LottoPeriod
from app.db.schemas import MatchOut, LottoPeriodOut
from app.services.lotto14 import lotto14_search, lotto9_search

router = APIRouter(prefix="/api/lotto", tags=["lotto"])


def _build_period(db: Session, kind: str, issue_no: str, n: int, first_match_kickoff: datetime):
    """根据"前 n 场未来比赛"动态生成期号"""
    rows = (
        db.query(Match)
        .filter(Match.status == "scheduled")
        .filter(Match.kickoff_at > now_bj())
        .order_by(Match.kickoff_at.asc())
        .limit(n)
        .all()
    )
    return {
        "kind": kind,
        "issue_no": issue_no,
        "first_match_kickoff": rows[0].kickoff_at if rows else first_match_kickoff,
        "close_at": rows[0].betting_close_at if rows else first_match_kickoff,
        "matches": [_match_out(m) for m in rows],
    }


def _match_out(m: Match) -> MatchOut:
    out = MatchOut.model_validate(m)
    if m.betting_close_at:
        out.minutes_to_close = int((m.betting_close_at - now_bj()).total_seconds() / 60)
    return out


@router.get("/periods", response_model=list[LottoPeriodOut])
def list_periods(db: Session = Depends(get_db)):
    """列出可投期号(V1 只生成 14 场和任选九两组期号)"""
    periods = (
        db.query(LottoPeriod)
        .filter(LottoPeriod.status.in_(["selling", "scheduled"]))
        .order_by(LottoPeriod.close_at.asc())
        .all()
    )
    out = []
    for p in periods:
        out.append({
            "id": p.id,
            "kind": p.kind,
            "issue_no": p.issue_no,
            "first_match_kickoff": p.first_match_kickoff,
            "close_at": p.close_at,
            "status": p.status,
            "cost_per_bet": 2,
        })
    return out


@router.get("/periods/{period_id}/matches")
def period_matches(period_id: int, db: Session = Depends(get_db)):
    """返回某期号下的 14 场对阵(动态生成)"""
    p = db.query(LottoPeriod).filter(LottoPeriod.id == period_id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"期号 {period_id} 不存在")
    if p.kind == "14场":
        n = 14
    elif p.kind == "任选九":
        n = 9
    else:
        n = 14
    return _build_period(db, p.kind, p.issue_no, n, p.first_match_kickoff)


def _elo_probs(home_elo: int, away_elo: int) -> dict:
    """计算一场比赛的 H/D/A 概率"""
    expected = 1 / (1 + 10 ** (-(home_elo + 80 - away_elo) / 400))
    H = expected
    A = 1 - expected
    D = max(0.15, (1 - abs(2 * expected - 1)) * 0.30)
    s = H + D + A
    return {"H": H / s, "D": D / s, "A": A / s}


def _calc_ev_pct(picks: list, match_probs: list[dict]) -> float:
    """计算一注的 EV%(基于各场概率乘积)"""
    if not picks or not match_probs:
        return 0.0
    combined_p = 1.0
    for i, pick in enumerate(picks):
        if i >= len(match_probs):
            break
        p = match_probs[i]
        if pick in ("H", "D", "A"):
            combined_p *= p.get(pick, 0.33)
        elif pick == "HD":
            combined_p *= (p.get("H", 0) + p.get("D", 0))
        elif pick == "DA":
            combined_p *= (p.get("D", 0) + p.get("A", 0))
        elif pick == "HA":
            combined_p *= (p.get("H", 0) + p.get("A", 0))
    # EV% = (combined_p * 赔率 - 1) * 100, 赔率=2 for single, higher for doubles
    avg_odds = 2.0
    edge = combined_p * avg_odds - 1
    return round(edge * 100, 1)


@router.get("/14场/recommendation")
def lotto14_recommendation(db: Session = Depends(get_db)):
    """14 场推荐:1 注主推 + 6 注复式"""
    rows = (
        db.query(Match)
        .filter(Match.status == "scheduled")
        .filter(Match.kickoff_at > now_bj())
        .order_by(Match.kickoff_at.asc())
        .limit(14)
        .all()
    )
    if len(rows) < 14:
        raise HTTPException(status_code=503, detail="可购比赛数量不足")

    # 计算每场概率
    match_probs = [_elo_probs(m.home.elo, m.away.elo) for m in rows]

    # 用服务层搜索
    main_ticket, backup_tickets = lotto14_search(match_probs)

    main = {
        "picks": main_ticket,
        "stake_count": 1,
        "cost": 2,
        "ev_pct": _calc_ev_pct(main_ticket, match_probs),
        "kind": "main",
    }

    backups = []
    for i, ticket in enumerate(backup_tickets):
        # 计算有多少个双选
        doubles = sum(1 for p in ticket if len(p) > 1)
        backups.append({
            "picks": ticket,
            "stake_count": 1 + doubles,
            "cost": 2 * (1 + doubles),
            "ev_pct": _calc_ev_pct(ticket, match_probs),
            "kind": "backup",
        })

    return {
        "issue_no": "24071",
        "kind": "14场",
        "main": main,
        "backups": backups,
        "matches": [_match_out(m) for m in rows],
    }


@router.get("/任选九/recommendation")
def lotto9_recommendation(db: Session = Depends(get_db)):
    """任选九:从 14 场里挑 9 场,挑信心足的"""
    rows = (
        db.query(Match)
        .filter(Match.status == "scheduled")
        .filter(Match.kickoff_at > now_bj())
        .order_by(Match.kickoff_at.asc())
        .limit(14)
        .all()
    )
    if len(rows) < 9:
        raise HTTPException(status_code=503, detail="可购比赛数量不足")

    # 计算每场概率
    match_probs = [_elo_probs(m.home.elo, m.away.elo) for m in rows]

    # 用服务层搜索
    main_ticket, backup_tickets = lotto9_search(match_probs)

    main = {
        "picks": main_ticket,
        "stake_count": 1,
        "cost": 2,
        "ev_pct": _calc_ev_pct(main_ticket, match_probs),
        "kind": "main",
    }

    backups = []
    for ticket in backup_tickets:
        doubles = sum(1 for p in ticket if len(p) > 1)
        backups.append({
            "picks": ticket,
            "stake_count": 1 + doubles,
            "cost": 2 * (1 + doubles),
            "ev_pct": _calc_ev_pct(ticket, match_probs),
            "kind": "backup",
        })

    # 取前9场作为matches(与已选择的9场顺序一致)
    selected_rows = rows[:9]

    return {
        "issue_no": "24072",
        "kind": "任选九",
        "main": main,
        "backups": backups,
        "matches": [_match_out(r) for r in selected_rows],
    }
