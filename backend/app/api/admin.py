from app.db.tz import now as now_bj
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Match, Odd, SyncLog
from app.db.schemas import OddsImportIn, ImportResult

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/odds/import", response_model=ImportResult)
def import_odds(payload: OddsImportIn, db: Session = Depends(get_db)):
    """手工导入/覆盖赔率。按 (match_id, bookmaker, market, selection) 去重更新。"""
    inserted = 0
    updated = 0
    errors = []
    for row in payload.rows:
        m = db.query(Match).filter(Match.external_id == row.match_external_id).first()
        if not m:
            errors.append(f"match_external_id={row.match_external_id} not found")
            continue
        existing = (
            db.query(Odd)
            .filter(
                Odd.match_id == m.id,
                Odd.bookmaker == payload.bookmaker,
                Odd.market == payload.market,
                Odd.selection == row.selection,
            )
            .first()
        )
        if existing:
            existing.odds = row.odds
            existing.line = row.line
            existing.ts = now_bj()
            updated += 1
        else:
            db.add(Odd(
                match_id=m.id,
                bookmaker=payload.bookmaker,
                market=payload.market,
                selection=row.selection,
                odds=row.odds,
                line=row.line,
                ts=now_bj(),
            ))
            inserted += 1
    db.commit()
    return ImportResult(inserted=inserted, updated=updated, errors=errors)


@router.post("/sync")
def trigger_sync(db: Session = Depends(get_db)):
    """手动触发 sporttery.cn 全量数据同步"""
    from app.services import sporttery
    try:
        data = sporttery.fetch("hhad,had")
        match_list = data.get("matchList", [])
        count = len(match_list)

        # 保存同步记录
        log = SyncLog(
            pool_code="hhad,had",
            match_count=count,
            status="ok",
            error_msg=None,
        )
        db.add(log)
        db.commit()

        return {"status": "ok", "synced": count, "pool": "hhad,had"}
    except Exception as e:
        # 失败时也记录
        log = SyncLog(
            pool_code="hhad,had",
            match_count=0,
            status="error",
            error_msg=str(e),
        )
        db.add(log)
        db.commit()
        raise
