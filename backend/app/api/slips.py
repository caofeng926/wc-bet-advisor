import json
from typing import List, Optional
from app.db.tz import now as now_bj
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Slip
from app.db.schemas import SlipIn, SettleIn, PnlSummary

router = APIRouter(prefix="/api/slips", tags=["slips"])


def _to_out(s: Slip) -> dict:
    return {
        "id": s.id,
        "title": s.title,
        "kind": s.kind,
        "selections": json.loads(s.selections_json),
        "total_odds": s.total_odds,
        "stake": s.stake,
        "cost": s.cost,
        "notes": s.notes,
        "result": s.result,
        "payout": s.payout,
        "pnl": s.pnl,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "settled_at": s.settled_at.isoformat() if s.settled_at else None,
    }


@router.get("", response_model=List[dict])
def list_slips(
    result: Optional[str] = None,
    kind: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(Slip).order_by(Slip.created_at.desc())
    if result:
        q = q.filter(Slip.result == result)
    if kind:
        q = q.filter(Slip.kind == kind)
    return [_to_out(s) for s in q.limit(limit).all()]


@router.post("", response_model=dict, status_code=201)
def create_slip(payload: SlipIn, db: Session = Depends(get_db)):
    s = Slip(
        title=payload.title,
        kind=payload.kind,
        selections_json=json.dumps(payload.selections, ensure_ascii=False),
        total_odds=payload.total_odds,
        stake=payload.stake,
        cost=payload.cost,
        notes=payload.notes,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return _to_out(s)


@router.post("/{slip_id}/settle", response_model=dict)
def settle_slip(slip_id: int, payload: SettleIn, db: Session = Depends(get_db)):
    s = db.query(Slip).filter(Slip.id == slip_id).first()
    if not s:
        raise HTTPException(404, "方案不存在")
    s.result = payload.result
    s.payout = payload.payout
    s.pnl = payload.payout - s.stake - s.cost
    s.settled_at = now_bj()
    db.commit()
    db.refresh(s)
    return _to_out(s)


@router.delete("/{slip_id}", status_code=204)
def delete_slip(slip_id: int, db: Session = Depends(get_db)):
    s = db.query(Slip).filter(Slip.id == slip_id).first()
    if not s:
        raise HTTPException(404, "方案不存在")
    db.delete(s)
    db.commit()
    return None


@router.get("/pnl/summary", response_model=PnlSummary)
def pnl_summary(db: Session = Depends(get_db)):
    slips = db.query(Slip).all()
    total_stake = 0.0
    total_payout = 0.0
    settled = 0
    pending = 0
    hit = 0
    by_market: dict = {}
    for s in slips:
        total_stake += s.stake + s.cost
        if s.result == "pending":
            pending += 1
            continue
        settled += 1
        total_payout += s.payout
        if s.result == "win":
            hit += 1
        by_market.setdefault(s.kind, {"stake": 0.0, "payout": 0.0, "count": 0, "hit": 0})
        by_market[s.kind]["stake"] += s.stake + s.cost
        by_market[s.kind]["payout"] += s.payout
        by_market[s.kind]["count"] += 1
        if s.result == "win":
            by_market[s.kind]["hit"] += 1

    pnl = total_payout - total_stake
    roi = (pnl / total_stake * 100) if total_stake > 0 else 0
    hit_rate = (hit / settled * 100) if settled > 0 else 0
    for m, v in by_market.items():
        v["pnl"] = round(v["payout"] - v["stake"], 2)
        v["roi_pct"] = round((v["pnl"] / v["stake"] * 100) if v["stake"] > 0 else 0, 2)
        v["stake"] = round(v["stake"], 2)
        v["payout"] = round(v["payout"], 2)
        v["hit_rate_pct"] = round((v["hit"] / v["count"] * 100) if v["count"] > 0 else 0, 2)

    return PnlSummary(
        total_stake=round(total_stake, 2),
        total_payout=round(total_payout, 2),
        total_pnl=round(pnl, 2),
        roi_pct=round(roi, 2),
        hit_rate_pct=round(hit_rate, 2),
        settled_count=settled,
        pending_count=pending,
        by_market=by_market,
    )
