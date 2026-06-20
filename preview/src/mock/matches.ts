export type MatchStatus = "scheduled" | "live" | "ft" | "postponed";

export interface Team {
  iso3: string;
  name_zh: string;
  name_en: string;
  fifa_rank: number;
  elo: number;
  group?: string;
}

export interface Match {
  id: number;
  home: Team;
  away: Team;
  stage: string;
  group?: string;
  kickoff_at: string;       // ISO
  betting_close_at: string; // ISO
  venue: string;
  status: MatchStatus;
  ft_home?: number;
  ft_away?: number;
}

// 截止时间设置:"今天"是用户视角的 2026-06-12
const TODAY = new Date("2026-06-12T00:00:00+08:00");
function hoursFromToday(h: number): string {
  const d = new Date(TODAY);
  d.setHours(d.getHours() + h);
  return d.toISOString();
}

export const MATCHES: Match[] = [
  {
    id: 1,
    home: { iso3: "BRA", name_zh: "巴西", name_en: "Brazil", fifa_rank: 5, elo: 2050, group: "G" },
    away: { iso3: "CRO", name_zh: "克罗地亚", name_en: "Croatia", fifa_rank: 10, elo: 1880, group: "G" },
    stage: "小组赛",
    group: "G",
    kickoff_at: hoursFromToday(9),
    betting_close_at: hoursFromToday(8.92),
    venue: "MetLife Stadium, New York",
    status: "scheduled",
  },
  {
    id: 2,
    home: { iso3: "ESP", name_zh: "西班牙", name_en: "Spain", fifa_rank: 8, elo: 1900, group: "E" },
    away: { iso3: "CRC", name_zh: "哥斯达黎加", name_en: "Costa Rica", fifa_rank: 31, elo: 1620, group: "E" },
    stage: "小组赛",
    group: "E",
    kickoff_at: hoursFromToday(12),
    betting_close_at: hoursFromToday(11.92),
    venue: "Estadio Azteca, Mexico City",
    status: "scheduled",
  },
  {
    id: 3,
    home: { iso3: "ARG", name_zh: "阿根廷", name_en: "Argentina", fifa_rank: 1, elo: 2120, group: "C" },
    away: { iso3: "KSA", name_zh: "沙特阿拉伯", name_en: "Saudi Arabia", fifa_rank: 49, elo: 1580, group: "C" },
    stage: "小组赛",
    group: "C",
    kickoff_at: hoursFromToday(15),
    betting_close_at: hoursFromToday(0),  // 已截止
    venue: "Lusail Stadium, Lusail",
    status: "ft",
    ft_home: 1,
    ft_away: 2,
  },
  {
    id: 4,
    home: { iso3: "MAR", name_zh: "摩洛哥", name_en: "Morocco", fifa_rank: 13, elo: 1730 },
    away: { iso3: "POR", name_zh: "葡萄牙", name_en: "Portugal", fifa_rank: 6, elo: 1870 },
    stage: "1/8 决赛",
    kickoff_at: hoursFromToday(18),
    betting_close_at: hoursFromToday(17.92),
    venue: "Al Bayt Stadium, Al Khor",
    status: "scheduled",
  },
  {
    id: 5,
    home: { iso3: "FRA", name_zh: "法国", name_en: "France", fifa_rank: 2, elo: 2090, group: "D" },
    away: { iso3: "DEN", name_zh: "丹麦", name_en: "Denmark", fifa_rank: 19, elo: 1750, group: "D" },
    stage: "小组赛",
    group: "D",
    kickoff_at: hoursFromToday(24),
    betting_close_at: hoursFromToday(23.92),
    venue: "Stadium 974, Doha",
    status: "scheduled",
  },
  {
    id: 6,
    home: { iso3: "GER", name_zh: "德国", name_en: "Germany", fifa_rank: 14, elo: 1820, group: "E" },
    away: { iso3: "JPN", name_zh: "日本", name_en: "Japan", fifa_rank: 20, elo: 1740, group: "E" },
    stage: "小组赛",
    group: "E",
    kickoff_at: hoursFromToday(30),
    betting_close_at: hoursFromToday(29.92),
    venue: "Khalifa International, Doha",
    status: "scheduled",
  },
];

export function getMatch(id: number): Match | undefined {
  return MATCHES.find((m) => m.id === id);
}

// 最近一个未截止的比赛,用于顶部倒计时 banner
export function getNextClosingMatch(): Match {
  const open = MATCHES.filter((m) => new Date(m.betting_close_at).getTime() > Date.now());
  if (open.length === 0) return MATCHES[0];
  return open.sort(
    (a, b) =>
      new Date(a.betting_close_at).getTime() - new Date(b.betting_close_at).getTime()
  )[0];
}
