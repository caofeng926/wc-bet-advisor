import { kellyFraction } from "../lib/kelly";
import { oddsForMatch } from "./odds";
import { polForMatch } from "./polymarket";

export interface ModelPrediction {
  match_id: number;
  market: "1x2" | "ah";
  selection: string;
  odds: number;
  p_elo: number;
  p_form: number;
  p_market: number;
  p_polymarket: number;
  p_final: number;
  edge: number;
  kelly: number;
  recommended: boolean;
  reasons: string[];
}

// 融合权重(可在 Settings 调)
const W = { elo: 0.4, form: 0.2, market: 0.2, polymarket: 0.2 };

// 用 ELO 估算胜平负基础概率
function eloProbs(homeElo: number, awayElo: number, homeAdv = 100): { H: number; D: number; A: number } {
  const expected = 1 / (1 + Math.pow(10, -(homeElo + homeAdv - awayElo) / 400));
  // 简单模型:主胜 ~ 期望;平局 ~ (1-|2*expected-1|)*0.30
  const H = expected;
  const A = 1 - expected;
  const D = Math.max(0, (1 - Math.abs(2 * expected - 1)) * 0.30);
  const sum = H + D + A;
  return { H: H / sum, D: D / sum, A: A / sum };
}

// 提取"手工-A"的赔率作代表盘口(国内体彩口径)
function representativeOdds(matchId: number, market: "1x2" | "ah"): Record<string, number> {
  const rows = oddsForMatch(matchId).filter((o) => o.market === market && o.bookmaker === "手工-A");
  const out: Record<string, number> = {};
  rows.forEach((r) => (out[r.selection] = r.odds));
  return out;
}

// 把赔率归一化算市场隐含概率
function impliedProbs(odds: Record<string, number>): Record<string, number> {
  const inv: Record<string, number> = {};
  let sum = 0;
  Object.entries(odds).forEach(([k, v]) => {
    inv[k] = 1 / v;
    sum += 1 / v;
  });
  // 扣水(假设 8% 抽水)
  const total = sum * 1.08;
  Object.keys(inv).forEach((k) => (inv[k] = inv[k] / total));
  return inv;
}

function polProbFor(matchId: number, market: "1x2" | "ah", selection: string): number {
  // Polymarket 在 V1 主要是 advance 市场,这里做简化映射
  const pols = polForMatch(matchId);
  if (pols.length === 0) return 0;
  if (market === "1x2") {
    if (selection === "H") {
      const p = pols.find((p) => p.team_iso3 === "MAR" && p.outcome === "Yes");
      return p?.price ?? 0;
    }
    if (selection === "A") {
      const p = pols.find((p) => p.team_iso3 === "POR" && p.outcome === "Yes");
      return p?.price ?? 0;
    }
  }
  return 0;
}

// 为每场比赛生成预测
function buildForMatch(matchId: number, homeElo: number, awayElo: number, market: "1x2" | "ah"): ModelPrediction[] {
  const elo = eloProbs(homeElo, awayElo);
  const rep = representativeOdds(matchId, market);
  const mkt = impliedProbs(rep);
  const out: ModelPrediction[] = [];

  Object.keys(rep).forEach((sel) => {
    const odds = rep[sel];
    const pElo = (elo as Record<string, number>)[sel.charAt(0)] ?? 0;
    const pMkt = mkt[sel] ?? 0;
    const pForm = pElo; // 简化:近期状态与 ELO 强相关
    const pPol = polProbFor(matchId, market, sel);
    // 融合(Polymarket 缺失时按权重重新归一)
    const totalW =
      W.elo + W.form + W.market + (pPol > 0 ? W.polymarket : 0);
    const wMkt = pPol > 0 ? W.market : W.market + W.polymarket;
    const pFinal =
      (W.elo * pElo + W.form * pForm + wMkt * pMkt + (pPol > 0 ? W.polymarket * pPol : 0)) /
      totalW;
    const edge = pFinal * odds - 1;
    const kelly = Math.max(0, kellyFraction(pFinal, odds));
    const recommended = edge >= 0.05 && kelly > 0.005 && pFinal >= 0.10;

    const reasons: string[] = [];
    if (pPol > 0) {
      const pol_dis = Math.abs(pPol - pMkt);
      if (pol_dis > 0.08) reasons.push(`Polymarket 与市场分歧 ${(pol_dis * 100).toFixed(0)}%`);
    }
    if (Math.abs(homeElo - awayElo) > 150) {
      reasons.push(`ELO 差 ${homeElo - awayElo} (${homeElo > awayElo ? "主" : "客"} 强)`);
    }
    if (edge > 0.15) reasons.push(`edge ${(edge * 100).toFixed(0)}% 显著`);

    out.push({
      match_id: matchId,
      market,
      selection: sel,
      odds,
      p_elo: pElo,
      p_form: pForm,
      p_market: pMkt,
      p_polymarket: pPol,
      p_final: pFinal,
      edge,
      kelly,
      recommended,
      reasons,
    });
  });

  return out;
}

// 缓存
const cache: Record<string, ModelPrediction[]> = {};

export function getPredictions(matchId: number, homeElo: number, awayElo: number): ModelPrediction[] {
  const key = `${matchId}`;
  if (cache[key]) return cache[key];
  const x12 = buildForMatch(matchId, homeElo, awayElo, "1x2");
  const ah = buildForMatch(matchId, homeElo, awayElo, "ah");
  cache[key] = [...x12, ...ah];
  return cache[key];
}

export function getTopPick(matchId: number, homeElo: number, awayElo: number): ModelPrediction | null {
  const all = getPredictions(matchId, homeElo, awayElo).filter((p) => p.recommended);
  if (all.length === 0) return null;
  return all.sort((a, b) => b.edge - a.edge)[0];
}

