// 轻量 API 客户端 - 调后端
const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export interface TeamApi {
  id: number;
  name_zh: string;
  name_en: string;
  iso3: string;
  iso2: string;
  group: string | null;
  elo: number;
  fifa_rank: number | null;
}

export interface MatchApi {
  id: number;
  stage: string;
  group: string | null;
  matchday: number | null;
  venue: string | null;
  kickoff_at: string;
  betting_close_at: string | null;
  status: string;
  home: TeamApi;
  away: TeamApi;
  ft_home: number | null;
  ft_away: number | null;
  minutes_to_close: number | null;
}

export interface OddApi {
  id: number;
  match_id: number;
  bookmaker: string;
  market: string;
  selection: string;
  line: number | null;
  odds: number;
  ts: string;
  vig_pct: number | null;
}

export interface CountdownApi {
  status: string;
  next_close_at: string | null;
  match_id?: number;
  home?: string;
  away?: string;
  seconds_remaining: number;
}

export interface ValueBet {
  match_id: number;
  home: string;
  away: string;
  kickoff_at: string;
  minutes_to_close: number | null;
  market: string;
  selection: string;
  odds: number;
  p_market: number;
  p_final: number;
  edge: number;
  kelly: number;
}

export interface ParlayCandidate extends ValueBet {
  group: string;
  kickoff_date: string;
  p_match: number;
}

export interface LottoRow {
  match_id: number;
  home: string;
  away: string;
  kickoff_at: string;
  picks: string[];
  p_each: Record<string, number>;
  best_pick: string;
  best_p: number;
}

export interface LottoTicket {
  picks: string[];
  stake_count: number;
  cost: number;
  ev_pct: number;
  kind: "main" | "backup";
}

export interface LottoRecommendation {
  issue_no: string;
  kind: string;
  main: LottoTicket;
  backups: LottoTicket[];
  matches: MatchApi[];
}

export interface PoissonPrediction {
  match_id: number;
  home: string;
  away: string;
  lambda_home: number;
  lambda_away: number;
  score_matrix: number[][];
  top_scores: [string, number][];
  goals_distribution: Record<string, number>;
}

export interface HtftPrediction {
  match_id: number;
  home: string;
  away: string;
  ht1_probs: Record<string, number>;
  ht2_probs: Record<string, number>;
  outcomes: Record<string, number>;
  top3: [string, number][];
}

export interface PolymarketMarket {
  market_id: string;
  question: string;
  outcome_yes: string;
  outcome_no: string;
  price_yes: number;
  price_no: number;
  implied_prob: number;
  liquidity: number;
  volume_24h: number;
}

export interface PolymarketResponse {
  match_id: number;
  home: string;
  away: string;
  markets: PolymarketMarket[];
  fetched_at: string;
}

export interface SlipApi {
  id: number;
  title: string;
  kind: string;
  selections: Record<string, unknown>[];
  total_odds: number;
  stake: number;
  cost: number;
  notes: string | null;
  result: string;
  payout: number;
  pnl: number;
  created_at: string;
  settled_at: string | null;
}

export interface PnlSummary {
  total_stake: number;
  total_payout: number;
  total_pnl: number;
  roi_pct: number;
  hit_rate_pct: number;
  settled_count: number;
  pending_count: number;
  by_market: Record<string, number>;
}

// --- 足球玩法推荐类型 ---
export interface CrsItem {
  score: string;
  p_poisson: number;
  odds: number;
  edge: number;
}

export interface CrsRecommendOut {
  match_id: number;
  home: string;
  away: string;
  kickoff_at: string;
  top_scores: CrsItem[];
  best_bet: string | null;
  best_edge: number;
  single: number;
}

export interface TtgItem {
  goals: string;
  p_poisson: number;
  odds: number;
  edge: number;
}

export interface TtgRecommendOut {
  match_id: number;
  home: string;
  away: string;
  kickoff_at: string;
  lambda_total: number;
  goals: TtgItem[];
  best_bet: string | null;
  best_edge: number;
  single: number;
}

export interface HafuItem {
  outcome: string;
  label: string;
  p_htft: number;
  odds: number;
  edge: number;
}

export interface HafuRecommendOut {
  match_id: number;
  home: string;
  away: string;
  kickoff_at: string;
  outcomes: HafuItem[];
  top3: HafuItem[];
  best_bet: string | null;
  best_edge: number;
  single: number;
}

export interface ChampionItem {
  team: string;
  odds: number;
  elo_rank: number;
  edge: number;
  p_elo: number;
  implied: number;
}

export interface ChampionRecommendOut {
  pool_code: string;
  items: ChampionItem[];
  fetched_at: string;
}

export interface FootballTodayBest {
  market: string;
  selection: string;
  label: string;
  odds: number;
  p_model: number;
  edge: number;
  single: number;
}

export interface FootballTodayMatch {
  match_id: number;
  home: string;
  away: string;
  kickoff_at: string;
  best_crs: FootballTodayBest | null;
  best_ttg: FootballTodayBest | null;
  best_hafu: FootballTodayBest | null;
}

export interface FootballTodayOut {
  date: string;
  fetched_at: string;
  source: string;
  matches: FootballTodayMatch[];
}

export interface FootballTodayOut {
  date: string;
  matches: FootballTodayMatch[];
}

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`);
  if (!r.ok) throw new Error(`GET ${path} 返回状态码 ${r.status}`);
  return r.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`POST ${path} 返回状态码 ${r.status}`);
  return r.json();
}

async function del<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`, { method: "DELETE" });
  if (!r.ok) throw new Error(`DELETE ${path} 返回状态码 ${r.status}`);
  return r.ok ? ({} as T) : r.json();
}

export const api = {
  listMatches: (params: { stage?: string; status?: string; group?: string; limit?: number } = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => v != null && q.set(k, String(v)));
    return get<MatchApi[]>(`/api/matches?${q.toString()}`);
  },
  getMatch: (id: number) => get<MatchApi>(`/api/matches/${id}`),
  getMatchOdds: (id: number) => get<OddApi[]>(`/api/matches/${id}/odds`),
  getCountdown: () => get<CountdownApi>(`/api/admin/countdown`),
  getValueBets: (minEdge = 0.05, market?: string) => {
    const q = new URLSearchParams();
    q.set("min_edge", String(minEdge));
    if (market) q.set("market", market);
    return get<ValueBet[]>(`/api/recommendations/today?${q.toString()}`);
  },
  getParlayCandidates: (minEdge = 0.05) =>
    get<{candidates: ParlayCandidate[]; min_edge: number }>(`/api/parlay/candidates?min_edge=${minEdge}`).then(r => r.candidates),
  getPoisson: (matchId: number) =>
    get<PoissonPrediction>(`/api/recommendations/poisson/${matchId}`),
  getHtft: (matchId: number) =>
    get<HtftPrediction>(`/api/recommendations/htft/${matchId}`),
  getPolymarket: (matchId: number) =>
    get<PolymarketResponse>(`/api/polymarket/${matchId}`),
  getLotto14: () => get<LottoRecommendation>(`/api/lotto/14场/recommendation`),
  getLotto9: () => get<LottoRecommendation>(`/api/lotto/任选九/recommendation`),
  listSlips: (result?: string, kind?: string) => {
    const q = new URLSearchParams();
    if (result) q.set("result", result);
    if (kind) q.set("kind", kind);
    return get<SlipApi[]>(`/api/slips?${q.toString()}`);
  },
  createSlip: (body: { title: string; kind: string; selections: Record<string, unknown>[]; total_odds: number; stake: number; cost?: number; notes?: string }) =>
    post<SlipApi>(`/api/slips`, body),
  settleSlip: (id: number, result: string, payout: number) =>
    post<SlipApi>(`/api/slips/${id}/settle`, { result, payout }),
  deleteSlip: (id: number) => del<void>(`/api/slips/${id}`),
  getPnlSummary: () => get<PnlSummary>(`/api/slips/pnl/summary`),
  importOdds: (body: {
    bookmaker: string;
    market: string;
    rows: { match_external_id: string; selection: string; odds: number; line?: number }[];
  }) => post<{ inserted: number; updated: number; errors: string[] }>(`/api/admin/odds/import`, body),
  health: () => get<{ status: string }>(`/health`),
  // 足球玩法推荐
  getFootballToday: (date?: string) =>
    get<FootballTodayOut>(`/api/football/today${date ? `?date=${date}` : ""}`),
  getScoreRecommend: (date?: string) =>
    get<CrsRecommendOut[]>(`/api/football/crs${date ? `?date=${date}` : ""}`),
  getTotalGoalsRecommend: (date?: string) =>
    get<TtgRecommendOut[]>(`/api/football/ttg${date ? `?date=${date}` : ""}`),
  getHtftRecommend: (date?: string) =>
    get<HafuRecommendOut[]>(`/api/football/hafu${date ? `?date=${date}` : ""}`),
  getChampionRecommend: (pool: "冠军" | "冠亚军") =>
    get<ChampionRecommendOut>(`/api/football/champion?pool=${pool}`),
};

export const API_BASE = BASE;
