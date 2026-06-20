from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Float, Text, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name_zh = Column(String(64), nullable=False)
    name_en = Column(String(64), nullable=False)
    iso3 = Column(String(3), unique=True, nullable=False, index=True)
    iso2 = Column(String(2), nullable=False)
    fifa_rank = Column(Integer, nullable=True)
    elo = Column(Integer, default=1500)
    group = Column(String(1), nullable=True)
    confederation = Column(String(16), nullable=True)
    is_host = Column(Integer, default=0)


class SyncLog(Base):
    __tablename__ = "sync_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    synced_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    pool_code = Column(String(32), nullable=False)
    match_count = Column(Integer, nullable=False)
    status = Column(String(16), nullable=False)  # ok / error
    error_msg = Column(Text, nullable=True)


class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(64), unique=True, nullable=True, index=True)
    stage = Column(String(16), nullable=False)
    group = Column(String(1), nullable=True)
    matchday = Column(Integer, nullable=True)
    venue = Column(String(128), nullable=True)
    kickoff_at = Column(DateTime, nullable=False, index=True)
    betting_close_at = Column(DateTime, nullable=True)
    betting_close_source = Column(String(8), default="rule")
    status = Column(String(16), default="scheduled", index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    ft_home = Column(Integer, nullable=True)
    ft_away = Column(Integer, nullable=True)

    home = relationship("Team", foreign_keys=[home_team_id])
    away = relationship("Team", foreign_keys=[away_team_id])
    odds = relationship("Odd", back_populates="match", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_match_kickoff_status", "kickoff_at", "status"),
    )


class Odd(Base):
    __tablename__ = "odds"
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    bookmaker = Column(String(32), nullable=False)
    market = Column(String(8), nullable=False)  # 1x2 / ah / ou / cs
    selection = Column(String(8), nullable=False)  # H/D/A or H(-1)/A(+1) or 1-0
    line = Column(Float, nullable=True)
    odds = Column(Float, nullable=False)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    vig_pct = Column(Float, nullable=True)

    match = relationship("Match", back_populates="odds")

class Slip(Base):
    __tablename__ = "slips"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    kind = Column(String(32), default="single")  # single/parlay/lotto14/lotto9
    selections_json = Column(Text, nullable=False)   # JSON: [{match_id, market, pick, odds}, ...]
    total_odds = Column(Float, nullable=False)
    stake = Column(Float, nullable=False)
    cost = Column(Float, default=0.0)               # 成本(对胜负彩)
    notes = Column(Text, nullable=True)
    result = Column(String(16), default="pending")  # pending/win/lose/void/partial
    payout = Column(Float, default=0.0)
    pnl = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    settled_at = Column(DateTime, nullable=True)


class LottoPeriod(Base):
    __tablename__ = "lotto_periods"
    id = Column(Integer, primary_key=True, autoincrement=True)
    kind = Column(String(16), nullable=False)  # "14场" / "任选九" / "6半全" / "4进球"
    issue_no = Column(String(16), nullable=False)
    first_match_kickoff = Column(DateTime, nullable=False)
    close_at = Column(DateTime, nullable=False)
    status = Column(String(16), default="selling")
    draw_result = Column(Text, nullable=True)
    source = Column(String(16), default="auto")
