"""Sporttery.cn (体彩官方) API client for fetching match odds.

API base: https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry
All field names in responses use camelCase (e.g. homeTeamAllName, matchDate, poolCode).
"""
import httpx

BASE_URL = "https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry"

_PROXY = "http://127.0.0.1:10808"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
}


def fetch(pool_code: str, date: str | None = None) -> dict:
    """Fetch match data from Sporttery API.

    Args:
        pool_code: Pool code such as "had", "hhad", "crs", "ttg", "hafu", "chp".
                   Multiple codes can be comma-separated (e.g. "hhad,had").
        date: Optional matchDate filter (e.g. "2025-06-14").

    Returns:
        The "value" field from the API response dict.
    """
    params: dict = {"channel": "c", "poolCode": pool_code}
    if date:
        params["matchDate"] = date

    with httpx.Client(proxy=_PROXY, headers=_HEADERS, verify=False, timeout=15) as client:
        r = client.get(BASE_URL, params=params)
        r.raise_for_status()
        data = r.json()
    return data["value"]


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_had_hhad(match: dict) -> dict:
    """Parse胜平负 (HAD) and 让球胜平负 (HHAD) odds from a match dict.

    Args:
        match: A single match object from the matchList array.

    Returns:
        dict with keys:
            - had: {"h": float, "d": float, "a": float}
            - hhad: {"h": float, "d": float, "a": float, "goalLine": str}
            - single_had: bool  (True if this pool is single)
            - single_hhad: bool
    """
    had = match.get("had", {})
    hhad = match.get("hhad", {})

    def _float(v) -> float | None:
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    result: dict = {
        "had": {
            "h": _float(had.get("h")),
            "d": _float(had.get("d")),
            "a": _float(had.get("a")),
        },
        "hhad": {
            "h": _float(hhad.get("h")),
            "d": _float(hhad.get("d")),
            "a": _float(hhad.get("a")),
            "goalLine": str(hhad.get("goalLine", "")),
        },
    }

    # Determine single flag from poolList
    pool_list: list[dict] = match.get("poolList", [])
    single_had = False
    single_hhad = False
    for pool in pool_list:
        code = pool.get("poolCode", "")
        single = pool.get("single")
        if code == "had" and single == 1:
            single_had = True
        elif code == "hhad" and single == 1:
            single_hhad = True

    result["single_had"] = single_had
    result["single_hhad"] = single_hhad
    return result


def parse_crs(match: dict) -> dict[str, float]:
    """Parse比分 (CRS) 31 options from a match dict.

    The31 score fields use the pattern ``s{homescore}{awayscore}`` with special
    codes ``s1sh`` (胜其他), ``s1sd`` (平其他), ``s1sa`` (负其他).

    Returns:
        dict mapping score strings such as "1:0", "2:0", "win_other", "draw_other",
        "lose_other" to their odds as float.
    """
    crs = match.get("crs", {})
    mapping = _build_crs_mapping()
    result: dict[str, float] = {}
    for field, score_str in mapping.items():
        try:
            val = float(crs.get(field, 0))
            if val > 0:
                result[score_str] = val
        except (TypeError, ValueError):
            pass
    return result


def _build_crs_mapping() -> dict[str, str]:
    """Build field-name -> score-string mapping for all 31 CRS options."""
    mapping: dict[str, str] = {}
    # Regular scores: home 0-5, away 0-5 (31 combos, but we enumerate explicitly)
    for h in range(6):
        for a in range(6):
            if h == 5 and a == 5:
                continue  # handled by win/draw/lose_other below
            field = f"s{h}s{a}"
            score_str = f"{h}:{a}"
            mapping[field] = score_str
    # Special "other" categories
    mapping["s1sh"] = "win_other" # 胜其他
    mapping["s1sd"] = "draw_other"   # 平其他
    mapping["s1sa"] = "lose_other"   # 负其他
    return mapping


def parse_ttg(match: dict) -> dict[str, float]:
    """Parse总进球 (TTG) 0~7+ options from a match dict.

    Returns:
        dict mapping goal strings "0"-"7" (where "7" means 7+) to odds.
    """
    ttg = match.get("ttg", {})
    result: dict[str, float] = {}
    for i in range(8):
        key = f"s{i}"
        try:
            val = float(ttg.get(key, 0))
            if val > 0:
                result[str(i)] = val
        except (TypeError, ValueError):
            pass
    return result


def parse_hafu(match: dict) -> dict[str, float]:
    """Parse半全场 (HAFU) 9 options from a match dict.

    Returns:
        dict mapping 2-letter hafu codes to odds:
        "hh"=主胜-主胜 "hd"=主胜-平 "ha"=主胜-客胜
        "dh"=平-主胜 "dd"=平-平 "da"=平-客胜
        "ah"=客胜-主胜 "ad"=平-客胜 "aa"=客胜-客胜
    """
    hafu = match.get("hafu", {})
    result: dict[str, float] = {}
    for code in ("hh", "hd", "ha", "dh", "dd", "da", "ah", "ad", "aa"):
        try:
            val = float(hafu.get(code, 0))
            if val > 0:
                result[code] = val
        except (TypeError, ValueError):
            pass
    return result


def parse_champion(outer: dict) -> list[dict]:
    """Parse冠军/冠亚军 odds from the champion API response.

    Args:
        outer: The full "value" dict returned by the champion pool API.

    Returns:
        list of dicts [{"team": str, "odds": float}, ...]
    """
    items: list[dict] = outer.get("items", [])
    result: list[dict] = []
    for item in items:
        team = item.get("teamNameCn", "")
        try:
            odds = float(item.get("odds", 0))
        except (TypeError, ValueError):
            continue
        if team and odds > 0:
            result.append({"team": team, "odds": odds})
    return result


# ---------------------------------------------------------------------------
# Fallback (offline) mock generators — used when Sporttery API is unreachable
# ---------------------------------------------------------------------------

def get_champion_fallback() -> list[dict]:
    """根据 DB 内 48 支球队的 ELO 生成模拟冠军赔率。

    当体彩官方 API 不可用或返回空时使用。模型基于 Plackett-Luce 概率:
        p_i = exp(elo_i / SCALE) / Σ exp(elo_j / SCALE)
    再叠加 8% 庄家抽水,转换为赔率,保留 2 位小数,最低 1.50。

    Returns:
        list[dict]: [{"team": str, "odds": float}, ...], 按赔率升序
    """
    import math
    from app.db.database import SessionLocal
    from app.db.models import Team

    db = SessionLocal()
    try:
        teams = db.query(Team).filter(Team.name_zh.isnot(None)).all()
    finally:
        db.close()

    if not teams:
        return []

    SCALE = 400.0
    MARGIN = 1.08
    exps = [(t.name_zh, math.exp(t.elo / SCALE)) for t in teams]
    total = sum(e for _, e in exps)

    items: list[dict] = []
    for name, e in exps:
        p = e / total
        implied = p * MARGIN
        odds = max(round(1 / implied, 2), 1.50)
        items.append({"team": name, "odds": odds})
    items.sort(key=lambda x: x["odds"])
    return items
