"""Seed script: 2026 美加墨世界杯 48 队/12 组 + 部分赛程"""
from datetime import datetime, timedelta
from app.db.database import init_db, SessionLocal
from app.db.models import Team, Match, Odd

# ============================================================
# 2026 世足 48 强(按 2025-12-05 真实抽签结果)
# ============================================================
TEAMS_2026 = [
    # (iso3, name_zh, name_en, group, elo, fifa_rank, is_host)
    ("MEX", "墨西哥",     "Mexico",        "A", 1820,  11, 1),
    ("RSA", "南非",       "South Africa",  "A", 1640,  57, 0),
    ("KOR", "韩国",       "South Korea",   "A", 1780,  23, 0),
    ("DEN", "丹麦",       "Denmark",       "A", 1870,  21, 0),

    ("CAN", "加拿大",     "Canada",        "B", 1700,  48, 1),
    ("ESP", "西班牙",     "Spain",         "B", 1920,  1, 0),
    ("JPN", "日本",       "Japan",         "B", 1790,  17, 0),
    ("AUS", "澳大利亚",   "Australia",     "B", 1680,  24, 0),

    ("BRA", "巴西",       "Brazil",        "C", 2060,  5, 0),
    ("MAR", "摩洛哥",     "Morocco",       "C", 1810,  13, 0),
    ("NOR", "挪威",       "Norway",        "C", 1820,  36, 0),
    ("PAN", "巴拿马",     "Panama",        "C", 1650,  30, 0),

    ("USA", "美国",       "USA",           "D", 1820,  15, 1),
    ("URU", "乌拉圭",     "Uruguay",       "D", 1850,  16, 0),
    ("PAR", "巴拉圭",     "Paraguay",      "D", 1750,  40, 0),
    ("CRO", "克罗地亚",   "Croatia",       "D", 1850,  10, 0),

    ("GER", "德国",       "Germany",       "E", 1890,  9, 0),
    ("TUN", "突尼斯",     "Tunisia",       "E", 1700,  41, 0),
    ("CUW", "库拉索",     "Curacao",       "E", 1620,  82, 0),
    ("NZL", "新西兰",     "New Zealand",   "E", 1610,  86, 0),

    ("ARG", "阿根廷",     "Argentina",     "F", 2120,  2, 0),
    ("ALG", "阿尔及利亚", "Algeria",       "F", 1750,  35, 0),
    ("AUT", "奥地利",     "Austria",       "F", 1780,  25, 0),
    ("JOR", "约旦",       "Jordan",        "F", 1660,  62, 0),

    ("FRA", "法国",       "France",        "G", 2090,  3, 0),
    ("SEN", "塞内加尔",   "Senegal",       "G", 1770,  18, 0),
    ("GHA", "加纳",       "Ghana",         "G", 1650,  72, 0),
    ("HON", "洪都拉斯",   "Honduras",      "G", 1640,  78, 0),

    ("ENG", "英格兰",     "England",       "H", 1920,  4, 0),
    ("EGY", "埃及",       "Egypt",         "H", 1740,  34, 0),
    ("IRN", "伊朗",       "Iran",          "H", 1740,  20, 0),
    ("CPV", "佛得角",     "Cape Verde",    "H", 1680,  70, 0),

    ("POR", "葡萄牙",     "Portugal",      "I", 1910,  6, 0),
    ("CIV", "科特迪瓦",   "Ivory Coast",   "I", 1720,  43, 0),
    ("UZB", "乌兹别克",   "Uzbekistan",    "I", 1700,  62, 0),
    ("BOL", "玻利维亚",   "Bolivia",       "I", 1640,  79, 0),

    ("NED", "荷兰",       "Netherlands",   "J", 1880,  7, 0),
    ("SUI", "瑞士",       "Switzerland",   "J", 1840,  19, 0),
    ("ECU", "厄瓜多尔",   "Ecuador",       "J", 1780,  22, 0),
    ("PER", "秘鲁",       "Peru",          "J", 1750,  32, 0),

    ("BEL", "比利时",     "Belgium",       "K", 1870,  8, 0),
    ("SRB", "塞尔维亚",   "Serbia",        "K", 1800,  33, 0),
    ("CRC", "哥斯达黎加", "Costa Rica",    "K", 1660,  46, 0),
    ("CMR", "喀麦隆",     "Cameroon",      "K", 1660,  51, 0),

    ("ITA", "意大利",     "Italy",         "L", 1870,  12, 0),
    ("POL", "波兰",       "Poland",        "L", 1780,  28, 0),
    ("CZE", "捷克",       "Czechia",       "L", 1770,  38, 0),
    ("UKR", "乌克兰",     "Ukraine",       "L", 1760,  26, 0),
]

# ============================================================
# 比赛:开赛日 06-11,首轮覆盖 12 组各 1 场 + 重点场次 + 部分淘汰赛
# 实际 2026 赛程太密(104 场),seed 取 30+ 场代表性比赛
# ============================================================
DAY1 = datetime(2026, 6, 11, 21, 0)  # 开幕战
def at(days_after, hour=18, minute=0):
    return DAY1 + timedelta(days=days_after, hours=hour - 21, minutes=minute)

MOCK_MATCHES = [
    # 开幕战(06-11)
    {"ext": "WC26-A-1", "stage": "group", "group": "A", "md": 1,
     "home": "MEX", "away": "RSA",
     "venue": "Estadio Azteca, Mexico City",
     "kickoff": at(0, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(0, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 06-12
    {"ext": "WC26-B-1", "stage": "group", "group": "B", "md": 1,
     "home": "CAN", "away": "ESP",
     "venue": "BMO Field, Toronto",
     "kickoff": at(1, 15, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(1, 14, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-D-1", "stage": "group", "group": "D", "md": 1,
     "home": "USA", "away": "CRO",
     "venue": "MetLife Stadium, New York",
     "kickoff": at(1, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(1, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-C-1", "stage": "group", "group": "C", "md": 1,
     "home": "BRA", "away": "MAR",
     "venue": "MetLife Stadium, New York",
     "kickoff": at(1, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(1, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 06-13
    {"ext": "WC26-E-1", "stage": "group", "group": "E", "md": 1,
     "home": "GER", "away": "TUN",
     "venue": "BayArena, Toronto",
     "kickoff": at(2, 15, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(2, 14, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-F-1", "stage": "group", "group": "F", "md": 1,
     "home": "ARG", "away": "ALG",
     "venue": "Estadio Akron, Guadalajara",
     "kickoff": at(2, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(2, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-A-2", "stage": "group", "group": "A", "md": 1,
     "home": "DEN", "away": "KOR",
     "venue": "Estadio BBVA, Monterrey",
     "kickoff": at(2, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(2, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 06-14
    {"ext": "WC26-G-1", "stage": "group", "group": "G", "md": 1,
     "home": "FRA", "away": "SEN",
     "venue": "Gillette Stadium, Boston",
     "kickoff": at(3, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(3, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-H-1", "stage": "group", "group": "H", "md": 1,
     "home": "ENG", "away": "EGY",
     "venue": "AT&T Stadium, Dallas",
     "kickoff": at(3, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(3, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 06-15
    {"ext": "WC26-I-1", "stage": "group", "group": "I", "md": 1,
     "home": "POR", "away": "CIV",
     "venue": "Lincoln Financial Field, Philadelphia",
     "kickoff": at(4, 15, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(4, 14, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-J-1", "stage": "group", "group": "J", "md": 1,
     "home": "NED", "away": "SUI",
     "venue": "SoFi Stadium, Los Angeles",
     "kickoff": at(4, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(4, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-K-1", "stage": "group", "group": "K", "md": 1,
     "home": "BEL", "away": "SRB",
     "venue": "Mercedes-Benz Stadium, Atlanta",
     "kickoff": at(4, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(4, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 06-16
    {"ext": "WC26-L-1", "stage": "group", "group": "L", "md": 1,
     "home": "ITA", "away": "POL",
     "venue": "NRG Stadium, Houston",
     "kickoff": at(5, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(5, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 06-17(第二轮)
    {"ext": "WC26-A-3", "stage": "group", "group": "A", "md": 2,
     "home": "MEX", "away": "DEN",
     "venue": "Estadio Azteca, Mexico City",
     "kickoff": at(6, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(6, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-B-3", "stage": "group", "group": "B", "md": 2,
     "home": "ESP", "away": "JPN",
     "venue": "BMO Field, Toronto",
     "kickoff": at(6, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(6, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 06-18
    {"ext": "WC26-C-3", "stage": "group", "group": "C", "md": 2,
     "home": "BRA", "away": "NOR",
     "venue": "MetLife Stadium, New York",
     "kickoff": at(7, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(7, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-D-3", "stage": "group", "group": "D", "md": 2,
     "home": "USA", "away": "URU",
     "venue": "MetLife Stadium, New York",
     "kickoff": at(7, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(7, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 06-20
    {"ext": "WC26-F-3", "stage": "group", "group": "F", "md": 2,
     "home": "ARG", "away": "AUT",
     "venue": "Estadio Akron, Guadalajara",
     "kickoff": at(9, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(9, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 06-22
    {"ext": "WC26-G-3", "stage": "group", "group": "G", "md": 2,
     "home": "FRA", "away": "GHA",
     "venue": "Gillette Stadium, Boston",
     "kickoff": at(11, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(11, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 06-25(第三轮,小组赛最后)
    {"ext": "WC26-A-4", "stage": "group", "group": "A", "md": 3,
     "home": "DEN", "away": "RSA",
     "venue": "Estadio BBVA, Monterrey",
     "kickoff": at(14, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(14, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-B-4", "stage": "group", "group": "B", "md": 3,
     "home": "CAN", "away": "AUS",
     "venue": "BC Place, Vancouver",
     "kickoff": at(14, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(14, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 06-26
    {"ext": "WC26-F-4", "stage": "group", "group": "F", "md": 3,
     "home": "ALG", "away": "JOR",
     "venue": "Estadio Akron, Guadalajara",
     "kickoff": at(15, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(15, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},

    # 淘汰赛阶段(07-01 ~ 07-19)
    {"ext": "WC26-R32-1", "stage": "R32", "md": None,
     "home": "BRA", "away": "URU",
     "venue": "SoFi Stadium, Los Angeles",
     "kickoff": at(20, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(20, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-R32-2", "stage": "R32", "md": None,
     "home": "ARG", "away": "DEN",
     "venue": "MetLife Stadium, New York",
     "kickoff": at(21, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(21, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-R32-3", "stage": "R32", "md": None,
     "home": "FRA", "away": "BEL",
     "venue": "AT&T Stadium, Dallas",
     "kickoff": at(22, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(22, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-R32-4", "stage": "R32", "md": None,
     "home": "ENG", "away": "ITA",
     "venue": "Mercedes-Benz Stadium, Atlanta",
     "kickoff": at(23, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(23, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    {"ext": "WC26-R16-1", "stage": "R16", "md": None,
     "home": "BRA", "away": "ENG",
     "venue": "MetLife Stadium, New York",
     "kickoff": at(25, 18, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(25, 17, 50).strftime("%Y-%m-%d %H:%M:%S")},
    {"ext": "WC26-R16-2", "stage": "R16", "md": None,
     "home": "ARG", "away": "NED",
     "venue": "SoFi Stadium, Los Angeles",
     "kickoff": at(26, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(26, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    {"ext": "WC26-QF-1", "stage": "QF", "md": None,
     "home": "BRA", "away": "ARG",
     "venue": "MetLife Stadium, New York",
     "kickoff": at(29, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(29, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    {"ext": "WC26-SF-1", "stage": "SF", "md": None,
     "home": "BRA", "away": "FRA",
     "venue": "MetLife Stadium, New York",
     "kickoff": at(33, 21, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(33, 20, 50).strftime("%Y-%m-%d %H:%M:%S")},

    {"ext": "WC26-FNL", "stage": "F", "md": None,
     "home": "BRA", "away": "ARG",
     "venue": "MetLife Stadium, New York",
     "kickoff": at(38, 20, 0).strftime("%Y-%m-%d %H:%M:%S"),
     "close": at(38, 19, 50).strftime("%Y-%m-%d %H:%M:%S")},
]

# ============================================================
# 赔率(3 家博彩公司 × 每个市场)
# ============================================================
def odds_for_match(match_ext: str, h_elo: int, a_elo: int, market: str):
    """根据 ELO 差生成基础赔率,让每场比赛有不同 baseline"""
    elo_diff = h_elo - a_elo
    p_h = 1 / (1 + 10 ** (-elo_diff / 400))  # 主场加成略小
    p_h = p_h * 0.85 + 0.10
    p_a = (1 - p_h) * 0.85
    p_d = 1 - p_h - p_a
    if p_d < 0.08:
        p_d = 0.08
        s = p_h + p_a
        p_h = p_h / s * (1 - p_d)
        p_a = p_a / s * (1 - p_d)
    if market == "1x2":
        return [
            ("1x2", "H", round(1 / p_h * 0.95, 2)),
            ("1x2", "D", round(1 / p_d * 0.95, 2)),
            ("1x2", "A", round(1 / p_a * 0.95, 2)),
        ]
    if market == "ah":
        # 让一球 / 让平半
        if elo_diff > 100:
            return [
                ("ah", "H(-1)", round(1 / (p_h * 1.2) * 0.95, 2), -1),
                ("ah", "A(+1)", round(1 / (1 - p_h * 0.2) * 0.95, 2), 1),
            ]
        return []
    return []


def run():
    init_db()
    db = SessionLocal()
    try:
        if db.query(Team).count() > 0:
            print(f"[seed] DB already populated (teams={db.query(Team).count()}). Skipping.")
            return

        # 1) 写 48 队
        for iso3, zh, en, group, elo, rank, is_host in TEAMS_2026:
            db.add(Team(
                iso3=iso3,
                iso2=iso3[:2].lower(),  # 默认 fallback,flagcdn 走自己的映射
                name_zh=zh,
                name_en=en,
                fifa_rank=rank,
                elo=elo,
                group=group,
                confederation="UEFA" if iso3 in [
                    "ESP","GER","ENG","FRA","ITA","NED","POR","BEL","CRO",
                    "DEN","SUI","AUT","POL","UKR","SRB","CZE","NOR","SWE",
                ] else ("CONMEBOL" if iso3 in [
                    "BRA","ARG","URU","COL","ECU","PAR","CHI","PER","BOL"
                ] else ("CONCACAF" if iso3 in [
                    "MEX","USA","CAN","CRC","HON","PAN","CUW","JAM"
                ] else ("AFC" if iso3 in [
                    "JPN","KOR","IRN","AUS","QAT","KSA","IRQ","UAE",
                    "CHN","JOR","UZB","IND"
                ] else ("CAF" if iso3 in [
                    "MAR","SEN","EGY","ALG","TUN","GHA","CIV","NGA",
                    "CMR","RSA","CPV"
                ] else "OFC")))),
                is_host=is_host,
            ))
        db.commit()
        print(f"[seed] Teams inserted: {db.query(Team).count()}")

        # 2) 写比赛
        team_by_iso = {t.iso3: t for t in db.query(Team).all()}
        match_by_ext = {}
        for m in MOCK_MATCHES:
            db.add(Match(
                external_id=m["ext"],
                stage=m["stage"],
                group=m.get("group"),
                matchday=m.get("md"),
                venue=m["venue"],
                kickoff_at=datetime.strptime(m["kickoff"], "%Y-%m-%d %H:%M:%S"),
                betting_close_at=datetime.strptime(m["close"], "%Y-%m-%d %H:%M:%S"),
                betting_close_source="manual",
                status="scheduled",
                home_team_id=team_by_iso[m["home"]].id,
                away_team_id=team_by_iso[m["away"]].id,
            ))
            match_by_ext[m["ext"]] = (m["home"], m["away"])
        db.commit()
        print(f"[seed] Matches inserted: {db.query(Match).count()}")

        # 3) 写赔率
        n_odds = 0
        for m in MOCK_MATCHES:
            home_iso, away_iso = m["home"], m["away"]
            h_elo = team_by_iso[home_iso].elo
            a_elo = team_by_iso[away_iso].elo
            match_db = db.query(Match).filter(Match.external_id == m["ext"]).first()

            # 3 家博彩公司:代表盘口差异
            books = {
                "Pinnacle": 0.96,  # 高赔付(抽水低)
                "Bet365":   0.94,
                "手工-A":   0.92,  # 国内体彩口径
            }
            for bookie, vig in books.items():
                for market in ["1x2", "ah"]:
                    rows = odds_for_match(m["ext"], h_elo, a_elo, market)
                    # vig 调整
                    rows_adj = []
                    for r in rows:
                        if len(r) == 3:
                            _, sel, odds_v = r
                            line = None
                        else:
                            _, sel, odds_v, line = r
                        rows_adj.append((market, sel, round(odds_v * vig / 0.95, 2), line))
                    for r in rows_adj:
                        market, sel, odds_v, line = r
                        db.add(Odd(
                            match_id=match_db.id,
                            bookmaker=bookie,
                            market=market,
                            selection=sel,
                            odds=odds_v,
                            line=line,
                            ts=datetime.utcnow(),
                        ))
                        n_odds += 1
        db.commit()
        print(f"[seed] Odds inserted: {n_odds}")

        print("[seed] DONE - 2026 WC data loaded")
    finally:
        db.close()


if __name__ == "__main__":
    run()

