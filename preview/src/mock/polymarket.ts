// Polymarket 公开市场价格(0-1),几乎无抽水
export interface PolPrice {
  match_id: number;
  market_type: "match" | "advance";
  team_iso3: string;
  outcome: "Yes" | "No";
  price: number;        // 0-1
  volume_24h: number;
  liquidity: number;
}

export const POLYMARKET: PolPrice[] = [
  // match 2 西班牙 vs 哥斯达黎加 - 西晋级下一轮
  { match_id: 2, market_type: "advance", team_iso3: "ESP", outcome: "Yes", price: 0.92, volume_24h: 85000, liquidity: 32000 },
  { match_id: 2, market_type: "advance", team_iso3: "ESP", outcome: "No",  price: 0.08, volume_24h: 85000, liquidity: 32000 },
  // match 4 摩洛哥 vs 葡萄牙 - 摩晋级
  { match_id: 4, market_type: "advance", team_iso3: "MAR", outcome: "Yes", price: 0.42, volume_24h: 120000, liquidity: 48000 },
  { match_id: 4, market_type: "advance", team_iso3: "MAR", outcome: "No",  price: 0.58, volume_24h: 120000, liquidity: 48000 },
  // match 4 葡萄牙晋级
  { match_id: 4, market_type: "advance", team_iso3: "POR", outcome: "Yes", price: 0.58, volume_24h: 120000, liquidity: 48000 },
  { match_id: 4, market_type: "advance", team_iso3: "POR", outcome: "No",  price: 0.42, volume_24h: 120000, liquidity: 48000 },
];

export function polForMatch(matchId: number): PolPrice[] {
  return POLYMARKET.filter((p) => p.match_id === matchId);
}
