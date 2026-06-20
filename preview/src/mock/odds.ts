// 3 家博彩公司赔率(贴近真实盘口)
export interface OddsRow {
  match_id: number;
  bookmaker: string;
  market: "1x2" | "ah" | "ou" | "cs";
  selection: string;     // H/D/A, H(-1)/A(+1), 1-0, 2-1, ...
  odds: number;
  line?: number;         // 让球 / 大小球
}

// 胜平负 + 让球
export const ODDS: OddsRow[] = [
  // match 1 巴西 vs 克罗地亚
  { match_id: 1, bookmaker: "Pinnacle", market: "1x2", selection: "H", odds: 1.55 },
  { match_id: 1, bookmaker: "Pinnacle", market: "1x2", selection: "D", odds: 4.20 },
  { match_id: 1, bookmaker: "Pinnacle", market: "1x2", selection: "A", odds: 6.50 },
  { match_id: 1, bookmaker: "Bet365",   market: "1x2", selection: "H", odds: 1.50 },
  { match_id: 1, bookmaker: "Bet365",   market: "1x2", selection: "D", odds: 4.00 },
  { match_id: 1, bookmaker: "Bet365",   market: "1x2", selection: "A", odds: 6.00 },
  { match_id: 1, bookmaker: "手工-A",   market: "1x2", selection: "H", odds: 1.85 },
  { match_id: 1, bookmaker: "手工-A",   market: "1x2", selection: "D", odds: 3.40 },
  { match_id: 1, bookmaker: "手工-A",   market: "1x2", selection: "A", odds: 4.20 },
  { match_id: 1, bookmaker: "Pinnacle", market: "ah",  selection: "H(-1)", odds: 2.30, line: -1 },
  { match_id: 1, bookmaker: "Pinnacle", market: "ah",  selection: "A(+1)", odds: 1.65, line: 1 },
  { match_id: 1, bookmaker: "Bet365",   market: "ah",  selection: "H(-1)", odds: 2.25, line: -1 },
  { match_id: 1, bookmaker: "Bet365",   market: "ah",  selection: "A(+1)", odds: 1.60, line: 1 },

  // match 2 西班牙 vs 哥斯达黎加
  { match_id: 2, bookmaker: "Pinnacle", market: "1x2", selection: "H", odds: 1.25 },
  { match_id: 2, bookmaker: "Pinnacle", market: "1x2", selection: "D", odds: 6.00 },
  { match_id: 2, bookmaker: "Pinnacle", market: "1x2", selection: "A", odds: 13.0 },
  { match_id: 2, bookmaker: "Bet365",   market: "1x2", selection: "H", odds: 1.22 },
  { match_id: 2, bookmaker: "Bet365",   market: "1x2", selection: "D", odds: 5.80 },
  { match_id: 2, bookmaker: "Bet365",   market: "1x2", selection: "A", odds: 12.5 },
  { match_id: 2, bookmaker: "手工-A",   market: "1x2", selection: "H", odds: 1.30 },
  { match_id: 2, bookmaker: "手工-A",   market: "1x2", selection: "D", odds: 5.50 },
  { match_id: 2, bookmaker: "手工-A",   market: "1x2", selection: "A", odds: 11.0 },
  { match_id: 2, bookmaker: "Pinnacle", market: "ah",  selection: "H(-2)", odds: 3.40, line: -2 },
  { match_id: 2, bookmaker: "Pinnacle", market: "ah",  selection: "A(+2)", odds: 1.30, line: 2 },
  { match_id: 2, bookmaker: "Bet365",   market: "ah",  selection: "H(-2)", odds: 3.30, line: -2 },
  { match_id: 2, bookmaker: "Bet365",   market: "ah",  selection: "A(+2)", odds: 1.28, line: 2 },

  // match 3 阿根廷 vs 沙特(已结束,无新赔率)

  // match 4 摩洛哥 vs 葡萄牙
  { match_id: 4, bookmaker: "Pinnacle", market: "1x2", selection: "H", odds: 4.50 },
  { match_id: 4, bookmaker: "Pinnacle", market: "1x2", selection: "D", odds: 3.40 },
  { match_id: 4, bookmaker: "Pinnacle", market: "1x2", selection: "A", odds: 1.85 },
  { match_id: 4, bookmaker: "Bet365",   market: "1x2", selection: "H", odds: 4.30 },
  { match_id: 4, bookmaker: "Bet365",   market: "1x2", selection: "D", odds: 3.30 },
  { match_id: 4, bookmaker: "Bet365",   market: "1x2", selection: "A", odds: 1.80 },
  { match_id: 4, bookmaker: "手工-A",   market: "1x2", selection: "H", odds: 4.20 },
  { match_id: 4, bookmaker: "手工-A",   market: "1x2", selection: "D", odds: 3.20 },
  { match_id: 4, bookmaker: "手工-A",   market: "1x2", selection: "A", odds: 1.78 },
  { match_id: 4, bookmaker: "Pinnacle", market: "ah",  selection: "A(-1)", odds: 3.20, line: -1 },
  { match_id: 4, bookmaker: "Pinnacle", market: "ah",  selection: "H(+1)", odds: 1.30, line: 1 },
  { match_id: 4, bookmaker: "Pinnacle", market: "ah",  selection: "H(+2)", odds: 1.05, line: 2 },

  // match 5 法国 vs 丹麦
  { match_id: 5, bookmaker: "Pinnacle", market: "1x2", selection: "H", odds: 1.65 },
  { match_id: 5, bookmaker: "Pinnacle", market: "1x2", selection: "D", odds: 3.80 },
  { match_id: 5, bookmaker: "Pinnacle", market: "1x2", selection: "A", odds: 5.50 },
  { match_id: 5, bookmaker: "Bet365",   market: "1x2", selection: "H", odds: 1.60 },
  { match_id: 5, bookmaker: "Bet365",   market: "1x2", selection: "D", odds: 3.75 },
  { match_id: 5, bookmaker: "Bet365",   market: "1x2", selection: "A", odds: 5.20 },
  { match_id: 5, bookmaker: "手工-A",   market: "1x2", selection: "H", odds: 1.75 },
  { match_id: 5, bookmaker: "手工-A",   market: "1x2", selection: "D", odds: 3.60 },
  { match_id: 5, bookmaker: "手工-A",   market: "1x2", selection: "A", odds: 4.80 },

  // match 6 德国 vs 日本
  { match_id: 6, bookmaker: "Pinnacle", market: "1x2", selection: "H", odds: 2.10 },
  { match_id: 6, bookmaker: "Pinnacle", market: "1x2", selection: "D", odds: 3.40 },
  { match_id: 6, bookmaker: "Pinnacle", market: "1x2", selection: "A", odds: 3.60 },
  { match_id: 6, bookmaker: "Bet365",   market: "1x2", selection: "H", odds: 2.05 },
  { match_id: 6, bookmaker: "Bet365",   market: "1x2", selection: "D", odds: 3.30 },
  { match_id: 6, bookmaker: "Bet365",   market: "1x2", selection: "A", odds: 3.50 },
  { match_id: 6, bookmaker: "手工-A",   market: "1x2", selection: "H", odds: 1.95 },
  { match_id: 6, bookmaker: "手工-A",   market: "1x2", selection: "D", odds: 3.50 },
  { match_id: 6, bookmaker: "手工-A",   market: "1x2", selection: "A", odds: 4.50 },
];

export function oddsForMatch(matchId: number): OddsRow[] {
  return ODDS.filter((o) => o.match_id === matchId);
}
