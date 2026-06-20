"""Polymarket integration API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.tz import now as now_bj

from app.db.database import get_db
from app.db.models import Match
from app.services.polymarket import fetch_match_markets, normalize_polymarket

router = APIRouter(prefix="/api/polymarket", tags=["polymarket"])


@router.get("/{match_id}")
def polymarket_for_match(match_id: int, db: Session = Depends(get_db)):
    """返回指定比赛的 Polymarket 市场数据。"""
    m = db.query(Match).filter(Match.id == match_id).first()
    if not m:
        raise HTTPException(404, "比赛不存在")

    markets = fetch_match_markets(m.home.name_en, m.away.name_en)
    normalized = normalize_polymarket(markets)

    return {
        "match_id": match_id,
        "home": m.home.name_en,
        "away": m.away.name_en,
        "markets": normalized,
        "fetched_at": now_bj().isoformat(),
    }