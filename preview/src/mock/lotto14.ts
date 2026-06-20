import { MATCHES } from "./matches";

// 14 场胜负彩 - 模拟 24071 期
export const LOTTO_ISSUE = {
  kind: "14场",
  season: "2026",
  issue_no: "24071",
  first_match_kickoff: MATCHES[0].kickoff_at,
  close_at: MATCHES[0].betting_close_at,
  cost_per_bet: 2,
};

export interface LottoRow {
  index: number;
  home_zh: string;
  away_zh: string;
  home_iso3: string;
  away_iso3: string;
  p: { H: number; D: number; A: number };
}

const EXTRA_TEAMS: Array<[string, string, string, string]> = [
  ["ENG", "英格兰", "IRN", "伊朗"],
  ["USA", "美国",   "WAL", "威尔士"],
  ["ITA", "意大利", "ARG", "阿根廷"],
  ["NED", "荷兰",   "SEN", "塞内加尔"],
  ["MEX", "墨西哥", "POL", "波兰"],
  ["KOR", "韩国",   "GHA", "加纳"],
  ["URU", "乌拉圭", "POR", "葡萄牙"],
  ["SUI", "瑞士",   "CMR", "喀麦隆"],
];

function synthProbs(seed: number): { H: number; D: number; A: number } {
  const r = Math.sin(seed * 17.3) * 10000;
  const frac = r - Math.floor(r);
  const h = 0.35 + frac * 0.4;
  const a = 0.15 + (1 - frac) * 0.35;
  const d = 1 - h - a;
  return { H: +h.toFixed(2), D: +Math.max(0.10, d).toFixed(2), A: +a.toFixed(2) };
}

export const LOTTO_ROWS: LottoRow[] = (() => {
  const rows: LottoRow[] = [];
  for (let i = 0; i < 6; i++) {
    const m = MATCHES[i];
    const eloH = m.home.elo;
    const eloA = m.away.elo;
    const expected = 1 / (1 + Math.pow(10, -(eloH + 80 - eloA) / 400));
    const H = expected;
    const A = 1 - expected;
    const D = Math.max(0.15, (1 - Math.abs(2 * expected - 1)) * 0.30);
    const sum = H + D + A;
    rows.push({
      index: i + 1,
      home_zh: m.home.name_zh,
      away_zh: m.away.name_zh,
      home_iso3: m.home.iso3,
      away_iso3: m.away.iso3,
      p: {
        H: +(H / sum).toFixed(2),
        D: +(D / sum).toFixed(2),
        A: +(A / sum).toFixed(2),
      },
    });
  }
  for (let i = 0; i < 8; i++) {
    const t = EXTRA_TEAMS[i];
    rows.push({
      index: 7 + i,
      home_zh: t[1],
      away_zh: t[3],
      home_iso3: t[0],
      away_iso3: t[2],
      p: synthProbs(i + 1),
    });
  }
  return rows;
})();

export interface LottoTicket {
  picks: string[];
  stake_count: number;
  cost: number;
  ev_pct: number;
  kind: "main" | "backup";
}

export function generateLottoTickets(): { main: LottoTicket; backups: LottoTicket[] } {
  const main_picks = LOTTO_ROWS.map((r) => {
    const keys = Object.keys(r.p) as Array<"H" | "D" | "A">;
    return keys.sort((a, b) => r.p[b] - r.p[a])[0];
  });
  const main: LottoTicket = {
    picks: main_picks,
    stake_count: 1,
    cost: 2,
    ev_pct: +(
      LOTTO_ROWS.reduce((acc, r, i) => acc + r.p[main_picks[i] as "H"], 0) /
      LOTTO_ROWS.length *
      100
    ).toFixed(1),
    kind: "main",
  };

  const backups: LottoTicket[] = [];
  for (let b = 0; b < 6; b++) {
    const picks: string[] = [];
    let extra = 0;
    LOTTO_ROWS.forEach((r, i) => {
      if ((b + i) % 3 === 0 && r.p.H < 0.6) {
        picks.push("HD");
        extra += 1;
      } else if ((b + i) % 3 === 1 && r.p.A < 0.6) {
        picks.push("DA");
        extra += 1;
      } else {
        const keys = Object.keys(r.p) as Array<"H" | "D" | "A">;
        const maxKey = keys.sort((a, c) => r.p[c] - r.p[a])[0];
        picks.push(maxKey);
      }
    });
    backups.push({
      picks,
      stake_count: 1 + extra,
      cost: 2 * (1 + extra),
      ev_pct: +(
        LOTTO_ROWS.reduce((acc, r, i) => {
          const pick = picks[i];
          let s = 0;
          if (pick.includes("H")) s += r.p.H;
          if (pick.includes("D")) s += r.p.D;
          if (pick.includes("A")) s += r.p.A;
          return acc + s;
        }, 0) /
        LOTTO_ROWS.length *
        100
      ).toFixed(1),
      kind: "backup",
    });
  }
  return { main, backups };
}
