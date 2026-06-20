"""绔炲僵鍒嗘瀽 API锛氭瘮鍒?/ 鎬昏繘鐞?/ 鍗婂叏鍦?/ 鍐犲啗鎺ㄨ崘"""
from fastapi import APIRouter, HTTPException
from app.services.sporttery import (
    fetch, parse_crs, parse_ttg, parse_hafu, parse_champion,
    get_champion_fallback,
)
from app.services.poisson import predict_goals
from app.services.htft import predict_htft
from app.db.database import SessionLocal
from app.db.models import Team
from app.db.schemas import (
    CrsRecommendOut, TtgRecommendOut,
    HafuRecommendOut, ChampionRecommendOut,
    FootballTodayOut, FootballTodayBest, FootballTodayMatch,

)
from app.db.tz import now as now_bj

router = APIRouter(prefix="/api/football", tags=["football"])


def _implied_prob(odds: float) -> float:
    return 1 / odds if odds > 0 else 0


def _edge(p_model: float, odds: float) -> float:
    return p_model * odds - 1


_HAFU_LABELS = {
    "hh": "半场主胜/全场主胜",
    "hd": "半场主胜/全场平",
    "ha": "半场主胜/全场客胜",
    "dh": "半场平/全场主胜",
    "dd": "半场平/全场平",
    "da": "半场平/全场客胜",
    "ah": "半场客胜/全场主胜",
    "ad": "半场客胜/全场平",
    "aa": "半场客胜/全场客胜",
}


def _get_all_teams_elo() -> dict[str, int]:
    """浠?DB 鍔犺浇鎵€鏈夌悆闃熺殑 ELO锛岃繑鍥?{name_zh: elo}

    娉ㄦ剰: 浠呯敤 name_zh 浣滀负 key,閬垮厤 name_zh/name_en 鍙岃瀵艰嚧姒傜巼鍒嗘瘝缈诲€?    """
    db = SessionLocal()
    try:
        teams = db.query(Team).filter(Team.name_zh.isnot(None)).all()
        return {t.name_zh: t.elo for t in teams}
    finally:
        db.close()


def _elo_ranking(elo_dict: dict[str, int]) -> dict[str, int]:
    """杩斿洖 {team_name: rank}锛宺ank 瓒婂皬瓒婂己"""
    sorted_teams = sorted(elo_dict.items(), key=lambda x: -x[1])
    return {name: rank + 1 for rank, (name, _) in enumerate(sorted_teams)}


def today_str() -> str:
    return now_bj().strftime("%Y-%m-%d")


@router.get("/crs", response_model=list[CrsRecommendOut])
def get_crs(date: str | None = None):
    """
    姣斿垎鎺ㄨ崘锛氭硦鏉?Top5 vs 瀹為檯璧旂巼鎵句环鍊?    """
    try:
        raw = fetch("crs", date)
    except Exception:
        raise HTTPException(status_code=503, detail="鏃犳硶杩炴帴浣撳僵鏈嶅姟绔紝璇风◢鍚庨噸璇")
    out = []
    for match in raw.get("matchList", []):
        match_id = match.get("id", 0)
        home_name = match.get("homeTeamAllName", "")
        away_name = match.get("awayTeamAllName", "")

        elo_h = match.get("home_elo", 1700)
        elo_a = match.get("away_elo", 1700)

        poisson = predict_goals(elo_h, elo_a, home_advantage=80)
        top_scores = poisson["top_scores"]

        crs_odds = parse_crs(match)
        pool_list = {p["poolCode"]: p for p in match.get("poolList", [])}
        single = pool_list.get("crs", {}).get("single", 1)

        items = []
        for score, p_poisson in top_scores:
            odds = crs_odds.get(score)
            if not odds or odds <= 1:
                continue
            edge = _edge(p_poisson, odds)
            items.append({
                "score": score,
                "p_poisson": float(p_poisson),
                "odds": float(odds),
                "edge": float(round(edge, 3)),
            })

        best = max(items, key=lambda x: x["edge"], default=None)
        out.append(CrsRecommendOut(
            match_id=match_id,
            home=home_name,
            away=away_name,
            kickoff_at=f"{match.get('matchDate', '')}T{match.get('matchTime', '')}",
            top_scores=items,
            best_bet=best["score"] if best else None,
            best_edge=best["edge"] if best else 0.0,
            single=single,
        ))
    return out


@router.get("/ttg", response_model=list[TtgRecommendOut])
def get_ttg(date: str | None = None):
    """
    鎬昏繘鐞冩帹鑽愶細娉婃澗杩涚悆鍒嗗竷 脳 澶у皬璧旂巼鎵句环鍊?    """
    try:
        raw = fetch("ttg", date)
    except Exception:
        raise HTTPException(status_code=503, detail="鏃犳硶杩炴帴浣撳僵鏈嶅姟绔紝璇风◢鍚庨噸璇")
    out = []
    for match in raw.get("matchList", []):
        match_id = match.get("id", 0)
        home_name = match.get("homeTeamAllName", "")
        away_name = match.get("awayTeamAllName", "")

        elo_h = match.get("home_elo", 1700)
        elo_a = match.get("away_elo", 1700)

        poisson = predict_goals(elo_h, elo_a, home_advantage=80)
        lambda_total = poisson["lambda_home"] + poisson["lambda_away"]

        ttg_odds = parse_ttg(match)
        pool_list = {p["poolCode"]: p for p in match.get("poolList", [])}
        single = pool_list.get("ttg", {}).get("single", 1)

        items = []
        for g_str, p_poisson in poisson["goals_distribution"].items():
            odds = ttg_odds.get(g_str)
            if not odds or odds <= 1:
                continue
            edge = _edge(float(p_poisson), odds)
            items.append({
                "goals": g_str,
                "p_poisson": float(p_poisson),
                "odds": float(odds),
                "edge": float(round(edge, 3)),
            })

        best = max(items, key=lambda x: x["edge"], default=None)
        out.append(TtgRecommendOut(
            match_id=match_id,
            home=home_name,
            away=away_name,
            kickoff_at=f"{match.get('matchDate', '')}T{match.get('matchTime', '')}",
            lambda_total=float(lambda_total),
            goals=items,
            best_bet=best["goals"] if best else None,
            best_edge=best["edge"] if best else 0.0,
            single=single,
        ))
    return out


@router.get("/hafu", response_model=list[HafuRecommendOut])
def get_hafu(date: str | None = None):
    """
    鍗婂叏鍦烘帹鑽愶細HTFT 妯″瀷 vs 瀹為檯璧旂巼鎵句环鍊?    """
    try:
        raw = fetch("hafu", date)
    except Exception:
        raise HTTPException(status_code=503, detail="鏃犳硶杩炴帴浣撳僵鏈嶅姟绔紝璇风◢鍚庨噸璇")
    out = []
    for match in raw.get("matchList", []):
        match_id = match.get("id", 0)
        home_name = match.get("homeTeamAllName", "")
        away_name = match.get("awayTeamAllName", "")

        elo_h = match.get("home_elo", 1700)
        elo_a = match.get("away_elo", 1700)

        htft = predict_htft(elo_h, elo_a, home_adv=60)
        hafu_odds = parse_hafu(match)
        pool_list = {p["poolCode"]: p for p in match.get("poolList", [])}
        single = pool_list.get("hafu", {}).get("single", 1)

        items = []
        for outcome, p_htft in htft["outcomes"].items():
            odds = hafu_odds.get(outcome)
            if not odds or odds <= 1:
                continue
            edge = _edge(float(p_htft), odds)
            label = _HAFU_LABELS.get(outcome, outcome)
            items.append({
                "outcome": outcome,
                "label": label,
                "p_htft": float(p_htft),
                "odds": float(odds),
                "edge": float(round(edge, 3)),
            })

        top3 = sorted(items, key=lambda x: x["edge"], reverse=True)[:3]
        best = max(items, key=lambda x: x["edge"], default=None)
        out.append(HafuRecommendOut(
            match_id=match_id,
            home=home_name,
            away=away_name,
            kickoff_at=f"{match.get('matchDate', '')}T{match.get('matchTime', '')}",
            outcomes=items,
            top3=top3,
            best_bet=best["outcome"] if best else None,
            best_edge=best["edge"] if best else 0.0,
            single=single,
        ))
    return out


@router.get("/champion", response_model=ChampionRecommendOut)
def get_champion(pool: str = "鍐犲啗"):
    """
    鐚滃啝鍐?/ 鍐犱簹鍐涳細璧旂巼鍒楄〃 + ELO 鎺掑悕

    鏁版嵁婧愮瓥鐣?
    1. 鍏堝皾璇曚綋褰╁畼鏂?API(https://webapi.sporttery.cn)
    2. 鑻ュけ璐ユ垨杩斿洖绌?浣跨敤 DB 鍐?48 闃?ELO 鎺ㄥ鐨?fallback 璧旂巼

    p_elo: Plackett-Luce 48 闃熼敠鏍囪禌鑳滅巼, 涓?fallback 璧旂巼鍙ｅ緞涓€鑷?    edge = p_elo * odds - 1
        鐪熷疄 API 涓嬬悊璁轰笂 edge 鍦?[-0.10, +0.50] 鍖洪棿
        fallback 鎯呭喌涓?edge 绾?-0.08(8% 鎶芥按)
    """
    items: list[dict] = []
    data_source = "sporttery_api"
    try:
        raw = fetch(pool)
        items = parse_champion(raw)
    except Exception:
        items = []

    if not items:
        items = get_champion_fallback()
        data_source = "elo_fallback"

    if not items:
        raise HTTPException(status_code=503, detail="鏆傛棤鍐犲啗璧旂巼鏁版嵁")

    elo_dict = _get_all_teams_elo()
    elo_rank_map = _elo_ranking(elo_dict)

    # Plackett-Luce 閿︽爣璧涜儨鐜? p_i = exp(elo_i/400) / 危 exp(elo_j/400)
    import math
    SCALE = 400.0
    exps = {name: math.exp(e / SCALE) for name, e in elo_dict.items()}
    total = sum(exps.values()) or 1.0

    enriched = []
    for item in items:
        team_name = item["team"]
        p_luce = exps.get(team_name, 0.0) / total
        implied = _implied_prob(item["odds"])
        edge = _edge(p_luce, item["odds"])
        enriched.append({
            "team": team_name,
            "odds": item["odds"],
            "elo_rank": elo_rank_map.get(team_name, 999),
            "edge": float(round(edge, 3)),
            "p_elo": float(round(p_luce, 4)),
            "implied": float(round(implied, 4)),
        })

    enriched.sort(key=lambda x: x["edge"], reverse=True)
    return ChampionRecommendOut(
        pool_code=pool,
        items=enriched,
        fetched_at=now_bj().isoformat(),
        data_source=data_source,
    )


_TTG_LABELS = {str(i): f"{i} 球" for i in range(8)}
_TTG_LABELS["7"] = "7+ 球"


def _analyze_crs(match: dict, elo_h: int, elo_a: int) -> "FootballTodayBest | None":
    crs_odds = parse_crs(match)
    if not crs_odds:
        return None
    poisson = predict_goals(elo_h, elo_a, home_advantage=80)
    pool_list = {p["poolCode"]: p for p in match.get("poolList", [])}
    single = pool_list.get("crs", {}).get("single", 0)
    items = []
    for score, p_poisson in poisson["top_scores"]:
        # poisson top_scores use "i-j" dash, parse_crs uses "h:a" colon
        score_key = score.replace("-", ":")
        odds = crs_odds.get(score_key)
        if not odds or odds <= 1:
            continue
        edge = _edge(p_poisson, odds)
        items.append((score, p_poisson, odds, edge))
    if not items:
        return None
    items.sort(key=lambda x: -x[3])
    score, p_poisson, odds, edge = items[0]
    return FootballTodayBest(
        market="crs",
        selection=score,
        label=f"比分 {score}",
        odds=float(odds),
        p_model=float(p_poisson),
        edge=float(round(edge, 3)),
        single=int(single),
    )
def _analyze_ttg(match: dict, elo_h: int, elo_a: int) -> "FootballTodayBest | None":
    ttg_odds = parse_ttg(match)
    if not ttg_odds:
        return None
    poisson = predict_goals(elo_h, elo_a, home_advantage=80)
    goals_dist = poisson["goals_distribution"]
    pool_list = {p["poolCode"]: p for p in match.get("poolList", [])}
    single = pool_list.get("ttg", {}).get("single", 0)
    items = []
    for g_str, odds in ttg_odds.items():
        p = float(goals_dist.get(g_str, 0.0))
        if p <= 0:
            continue
        edge = _edge(p, odds)
        items.append((g_str, p, odds, edge))
    if not items:
        return None
    items.sort(key=lambda x: -x[3])
    g, p, odds, edge = items[0]
    return FootballTodayBest(
        market="ttg",
        selection=g,
        label=f"总进球 {_TTG_LABELS.get(g, g)}",
        odds=float(odds),
        p_model=float(p),
        edge=float(round(edge, 3)),
        single=int(single),
    )


def _analyze_hafu(match: dict, elo_h: int, elo_a: int) -> "FootballTodayBest | None":
    hafu_odds = parse_hafu(match)
    if not hafu_odds:
        return None
    htft = predict_htft(elo_h, elo_a, home_adv=60)
    pool_list = {p["poolCode"]: p for p in match.get("poolList", [])}
    single = pool_list.get("hafu", {}).get("single", 0)
    items = []
    for outcome, p in htft["outcomes"].items():
        odds = hafu_odds.get(outcome)
        if not odds or odds <= 1:
            continue
        edge = _edge(p, odds)
        items.append((outcome, p, odds, edge))
    if not items:
        return None
    items.sort(key=lambda x: -x[3])
    outcome, p, odds, edge = items[0]
    return FootballTodayBest(
        market="hafu",
        selection=outcome,
        label=_HAFU_LABELS.get(outcome, outcome),
        odds=float(odds),
        p_model=float(p),
        edge=float(round(edge, 3)),
        single=int(single),
    )


@router.get("/today", response_model=FootballTodayOut)
def get_today(date: str | None = None):
    """今日全部 5 个玩法的最优推荐速览。

    数据源:sporttery.cn 实时(had/hhad/crs/ttg/hafu 单次拉取)。
    不可达时返回 source=offline + 空 matches(不抛 503,便于前端降级展示)。
    """
    date = date or today_str()
    try:
        raw = fetch("hhad,had,crs,ttg,hafu", date)
        source = "sporttery_api"
    except Exception:
        return FootballTodayOut(
            date=date,
            fetched_at=now_bj().isoformat(),
            source="offline",
            matches=[],
        )
    matches = raw.get("matchList", [])
    out_matches: list[FootballTodayMatch] = []
    for m in matches:
        mid = m.get("id", 0)
        elo_h = m.get("home_elo", 1700)
        elo_a = m.get("away_elo", 1700)
        out_matches.append(FootballTodayMatch(
            match_id=mid,
            home=m.get("homeTeamAllName", ""),
            away=m.get("awayTeamAllName", ""),
            kickoff_at=f"{m.get('matchDate', '')}T{m.get('matchTime', '')}",
            best_crs=_analyze_crs(m, elo_h, elo_a),
            best_ttg=_analyze_ttg(m, elo_h, elo_a),
            best_hafu=_analyze_hafu(m, elo_h, elo_a),
        ))
    return FootballTodayOut(
        date=date,
        fetched_at=now_bj().isoformat(),
        source=source,
        matches=out_matches,
    )
