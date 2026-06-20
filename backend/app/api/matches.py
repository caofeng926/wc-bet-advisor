from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.tz import now as now_bj

from app.db.database import get_db
from app.db.models import Match, Odd, Team
from app.db.schemas import MatchOut, OddOut

router = APIRouter(prefix="/api", tags=["matches"])


def _to_out(m: Match) -> MatchOut:
    out = MatchOut.model_validate(m)
    if m.betting_close_at:
        out.minutes_to_close = int((m.betting_close_at - now_bj()).total_seconds() / 60)
    return out


@router.get("/matches", response_model=list[MatchOut])
def list_matches(
    stage: Optional[str] = Query(None, description="group / R16 / QF / SF / F"),
    status: Optional[str] = Query(None, description="scheduled / ft"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    group: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Match)
    if stage:
        q = q.filter(Match.stage == stage)
    if status:
        q = q.filter(Match.status == status)
    if group:
        q = q.filter(Match.group == group)
    if date_from:
        q = q.filter(Match.kickoff_at >= date_from)
    if date_to:
        q = q.filter(Match.kickoff_at <= date_to)
    q = q.order_by(Match.kickoff_at.asc()).limit(limit)
    return [_to_out(m) for m in q.all()]


@router.get("/matches/{match_id}", response_model=MatchOut)
def get_match(match_id: int, db: Session = Depends(get_db)):
    m = db.query(Match).filter(Match.id == match_id).first()
    if not m:
        raise HTTPException(status_code=404, detail=f"比赛 {match_id} 不存在")
    return _to_out(m)


@router.get("/matches/{match_id}/odds", response_model=list[OddOut])
def get_match_odds(match_id: int, db: Session = Depends(get_db)):
    rows = db.query(Odd).filter(Odd.match_id == match_id).order_by(Odd.bookmaker, Odd.market, Odd.selection).all()
    return [OddOut.model_validate(r) for r in rows]


@router.get("/teams")
def list_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).order_by(Team.group, Team.name_zh).all()
    return [
        {
            "id": t.id, "name_zh": t.name_zh, "name_en": t.name_en,
            "iso3": t.iso3, "iso2": t.iso2, "group": t.group,
            "elo": t.elo, "fifa_rank": t.fifa_rank,
        }
        for t in teams
    ]


@router.get("/admin/countdown")
def admin_countdown(db: Session = Depends(get_db)):
    """返回最近一个未截止的比赛,供前端 banner 用"""
    now = now_bj()
    m = (
        db.query(Match)
        .filter(Match.betting_close_at.isnot(None))
        .filter(Match.betting_close_at > now)
        .order_by(Match.betting_close_at.asc())
        .first()
    )
    if not m:
        return {"status": "all_closed", "next_close_at": None, "seconds_remaining": 0}
    secs = int((m.betting_close_at - now).total_seconds())
    return {
        "status": "selling" if secs > 0 else "closed",
        "next_close_at": m.betting_close_at.isoformat(),
        "match_id": m.id,
        "home": m.home.name_zh,
        "away": m.away.name_zh,
        "seconds_remaining": max(0, secs),
    }
