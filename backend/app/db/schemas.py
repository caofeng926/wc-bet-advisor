from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TeamOut(BaseModel):
    id: int
    name_zh: str
    name_en: str
    iso3: str
    iso2: str
    group: Optional[str] = None
    elo: int
    fifa_rank: Optional[int] = None

    class Config:
        from_attributes = True


class MatchOut(BaseModel):
    id: int
    stage: str
    group: Optional[str] = None
    matchday: Optional[int] = None
    venue: Optional[str] = None
    kickoff_at: datetime
    betting_close_at: Optional[datetime] = None
    status: str
    home: TeamOut
    away: TeamOut
    ft_home: Optional[int] = None
    ft_away: Optional[int] = None
    minutes_to_close: Optional[int] = None

    class Config:
        from_attributes = True


class LottoPeriodOut(BaseModel):
    id: int
    kind: str
    issue_no: str
    first_match_kickoff: datetime
    close_at: datetime
    status: str
    cost_per_bet: int = 2

    class Config:
        from_attributes = True


class OddOut(BaseModel):
    id: int
    match_id: int
    bookmaker: str
    market: str
    selection: str
    line: Optional[float] = None
    odds: float
    ts: datetime
    vig_pct: Optional[float] = None

    class Config:
        from_attributes = True


class ParlayLegIn(BaseModel):
    match_id: int
    market: str = "1x2"
    selection: str = "H"
    odds: float


class ParlayCalculateIn(BaseModel):
    legs: list[ParlayLegIn]
    bankroll: float = 1000.0
    kelly_fraction: float = 0.25


class ParlayCalculateOut(BaseModel):
    total_odds: float
    combined_prob: float
    combined_edge: float
    suggested_stake: float
    expected_value: float
    correlation_penalty: float
    warnings: list[str] = []


class ParlayCandidateOut(BaseModel):
    match_id: int
    home: str
    away: str
    kickoff_at: str
    group: str
    kickoff_date: str
    market: str
    selection: str
    odds: float
    p_final: float
    edge: float
    p_match: float  # 同组/同时间的相关性


class ParlayCandidatesOut(BaseModel):
    candidates: list[ParlayCandidateOut]
    min_edge: float


class OddsImportIn(BaseModel):
    bookmaker: str = Field(..., description="e.g. Pinnacle / 手工-A")
    market: str = Field(..., description="1x2 / ah / ou / cs")
    rows: list["OddImportRow"]


class OddImportRow(BaseModel):
    match_external_id: str = Field(..., description="matches.external_id")
    selection: str
    odds: float
    line: Optional[float] = None


class ImportResult(BaseModel):
    inserted: int
    updated: int
    errors: list[str] = []


class SlipIn(BaseModel):
    title: str
    kind: str = "single"
    selections: list[dict]
    total_odds: float
    stake: float
    cost: float = 0.0
    notes: Optional[str] = None


class SettleIn(BaseModel):
    result: str
    payout: float


class PnlSummary(BaseModel):
    total_stake: float
    total_payout: float
    total_pnl: float
    roi_pct: float
    hit_rate_pct: float
    settled_count: int
    pending_count: int
    by_market: dict


class SyncLogOut(BaseModel):
    id: int
    synced_at: datetime
    pool_code: str
    match_count: int
    status: str
    error_msg: str | None

    class Config:
        from_attributes = True


class CrsRecommendOut(BaseModel):
    match_id: int
    home: str
    away: str
    kickoff_at: str
    top_scores: list[dict]  # [{score: str, p_poisson: float, odds: float, edge: float}]
    best_bet: str | None
    best_edge: float
    single: int  # 1=单关，0=仅过关

class TtgRecommendOut(BaseModel):
    match_id: int
    home: str
    away: str
    kickoff_at: str
    lambda_total: float
    goals: list[dict]  # [{goals: str, p_poisson: float, odds: float, edge: float}]
    best_bet: str | None
    best_edge: float
    single: int

class HafuRecommendOut(BaseModel):
    match_id: int
    home: str
    away: str
    kickoff_at: str
    outcomes: list[dict]  # [{outcome: str, label: str, p_htft: float, odds: float, edge: float}]
    top3: list[dict]
    best_bet: str | None
    best_edge: float
    single: int

class ChampionRecommendOut(BaseModel):
    pool_code: str
    items: list[dict]  # [{team: str, odds: float, elo_rank: int, edge: float, p_elo: float, implied: float}]
    fetched_at: str
    data_source: str = "sporttery_api"  # "sporttery_api" 真实赔率 / "elo_fallback" ELO 推导

class FootballTodayBest(BaseModel):
    market: str
    selection: str
    label: str = ""
    odds: float
    p_model: float
    edge: float
    single: int = 0


class FootballTodayMatch(BaseModel):
    match_id: int
    home: str
    away: str
    kickoff_at: str
    best_crs: FootballTodayBest | None = None
    best_ttg: FootballTodayBest | None = None
    best_hafu: FootballTodayBest | None = None


class FootballTodayOut(BaseModel):
    date: str
    fetched_at: str
    source: str
    matches: list[FootballTodayMatch]
