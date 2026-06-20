"""Polymarket API client for fetching market prices."""
import httpx


POLYMARKET_BASE = "https://gamma-api.polymarket.com"


def fetch_markets_for_team(team_name_en: str) -> list[dict]:
    """Fetch Polymarket markets for a team name."""
    try:
        with httpx.Client(timeout=10) as client:
            r = client.get(
                f"{POLYMARKET_BASE}/markets",
                params={"question": team_name_en, "closed": "false", "limit": 10},
            )
            if r.status_code != 200:
                return []
            data = r.json()
            return data.get("markets", [])
    except Exception:
        return []


def fetch_match_markets(home_name_en: str, away_name_en: str) -> list[dict]:
    """Fetch Polymarket markets matching a specific matchup."""
    all_markets = fetch_markets_for_team(home_name_en)
    filtered = []
    for m in all_markets:
        q = m.get("question", "").lower()
        if away_name_en.lower() in q or home_name_en.lower() in q:
            filtered.append(m)
    return filtered


def normalize_polymarket(markets: list[dict]) -> list[dict]:
    """Normalize Polymarket response to internal format."""
    out = []
    for market in markets:
        outcomes = market.get("outcomes", [])
        if len(outcomes) < 2:
            continue
        yes_price = float(market.get("outcomePrices", {}).get(outcomes[0], 0))
        no_price = float(market.get("outcomePrices", {}).get(outcomes[1], 0))
        if yes_price <= 0 or no_price <= 0:
            continue
        # Assume Yes = Home wins, No = Away wins for match winner markets
        implied_p = yes_price
        out.append({
            "market_id": market.get("id", ""),
            "question": market.get("question", ""),
            "outcome_yes": outcomes[0],
            "outcome_no": outcomes[1],
            "price_yes": round(yes_price, 4),
            "price_no": round(no_price, 4),
            "implied_prob": round(implied_p, 4),
            "liquidity": float(market.get("liquidity",0)),
            "volume_24h": float(market.get("volume24hr", 0)),
        })
    return out