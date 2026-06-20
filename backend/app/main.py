import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import init_db, SessionLocal
from app.db.models import LottoPeriod
from app.api.matches import router as matches_router
from app.api.admin import router as admin_router
from app.api.lotto import router as lotto_router
from app.api.parlay import router as parlay_router
from app.api.polymarket import router as polymarket_router
from app.api.football import router as football_router
from app.api.slips import router as slips_router
from app.api.recommendations import router as recommendations_router

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("wc-bet")

app = FastAPI(
    title="WC-Bet-Advisor API",
    version="0.2.0",
    description="2026 世界杯体彩竞猜购彩建议程序 — 后端 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches_router)
app.include_router(admin_router)
app.include_router(lotto_router)
app.include_router(parlay_router)
app.include_router(polymarket_router)
app.include_router(football_router)
app.include_router(slips_router)
app.include_router(recommendations_router)


def _ensure_lotto_periods():
    """启动时确保至少有 1 个 14 场 + 1 个任选九期号"""
    db = SessionLocal()
    try:
        from datetime import datetime
        from app.db.models import Match
        first = (
            db.query(Match)
            .filter(Match.status == "scheduled", Match.kickoff_at > datetime.utcnow())
            .order_by(Match.kickoff_at.asc())
            .first()
        )
        if not first:
            return
        for kind, issue_no in [("14场", "26071"), ("任选九", "26072")]:
            p = db.query(LottoPeriod).filter(LottoPeriod.kind == kind, LottoPeriod.issue_no == issue_no).first()
            if not p:
                db.add(LottoPeriod(
                    kind=kind, issue_no=issue_no,
                    first_match_kickoff=first.kickoff_at,
                    close_at=first.betting_close_at,
                    status="selling", source="auto",
                ))
                db.commit()
                logger.info("Created lotto period: %s %s", kind, issue_no)
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()
    _ensure_lotto_periods()
    logger.info("DB initialized at %s", settings.DATABASE_URL)


@app.get("/")
def root():
    return {"app": "WC-Bet-Advisor", "version": "0.2.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
