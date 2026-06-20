"""冠军推荐 fallback 单元测试: 当体彩 API 失败时使用 ELO 推导赔率"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.sporttery import get_champion_fallback


class TestChampionFallback:
    """get_champion_fallback() 必须返回 48 队 ELO 推导的冠军赔率"""

    def test_returns_48_teams(self):
        items = get_champion_fallback()
        assert len(items) == 48, f"期望 48 队, 实际 {len(items)}"

    def test_odds_format(self):
        items = get_champion_fallback()
        for it in items:
            assert isinstance(it, dict)
            assert "team" in it and isinstance(it["team"], str) and it["team"]
            assert "odds" in it and isinstance(it["odds"], float)
            assert it["odds"] >= 1.50, f"{it['team']} 赔率 {it['odds']} 低于下限 1.50"

    def test_odds_sorted_ascending(self):
        items = get_champion_fallback()
        odds_seq = [it["odds"] for it in items]
        assert odds_seq == sorted(odds_seq), "赔率应按升序排列 (热门 → 冷门)"

    def test_argentina_is_favorite(self):
        """阿根廷 ELO 最高 (2120), 应是赔率最低的冠军热门"""
        items = get_champion_fallback()
        assert items[0]["team"] == "阿根廷", f"冠军热门应是阿根廷, 实际是 {items[0]['team']}"
        assert items[0]["odds"] < items[-1]["odds"] / 2, "阿根廷赔率应明显低于最弱队"

    def test_nzl_is_longshot(self):
        """新西兰 ELO 最低 (1610), 应在末尾 (最大赔率)"""
        items = get_champion_fallback()
        assert items[-1]["team"] == "新西兰", f"最冷门应是新西兰, 实际是 {items[-1]['team']}"

    def test_implied_margin_in_range(self):
        """所有 implied 概率之和应在 1.05-1.20 之间 (庄家抽水 8%)"""
        items = get_champion_fallback()
        total_implied = sum(1 / it["odds"] for it in items)
        assert 1.05 <= total_implied <= 1.20, f"implied sum={total_implied:.3f} 超出 [1.05, 1.20]"

    def test_elo_monotonicity(self):
        """ELO 越高的队赔率越低 (弱单调)"""
        items = get_champion_fallback()
        # 拿到已知 ELO
        from app.db.database import SessionLocal
        from app.db.models import Team
        db = SessionLocal()
        try:
            elo_map = {t.name_zh: t.elo for t in db.query(Team).filter(Team.name_zh.isnot(None)).all()}
        finally:
            db.close()
        for it in items:
            assert it["team"] in elo_map, f"{it['team']} 不在 DB 里"
        # 取赔率前 5 和后 5 验证
        top5 = items[:5]
        bot5 = items[-5:]
        avg_top = sum(elo_map[it["team"]] for it in top5) / 5
        avg_bot = sum(elo_map[it["team"]] for it in bot5) / 5
        assert avg_top > avg_bot, f"前 5 名平均 ELO ({avg_top}) 应高于后 5 名 ({avg_bot})"


class TestChampionEndpointFallback:
    """当体彩 fetch() 失败时, /api/football/champion 应自动降级到 fallback"""

    def test_champion_endpoint_with_fallback(self):
        client = TestClient(app)
        with patch("app.api.football.fetch", side_effect=Exception("simulated offline")):
            r = client.get("/api/football/champion?pool=" + "冠军")
        assert r.status_code == 200, f"期望 200, 实际 {r.status_code}: {r.text[:200]}"
        data = r.json()
        assert data["data_source"] == "elo_fallback", f"应标注 fallback 数据源, 实际 {data['data_source']}"
        assert len(data["items"]) == 48

    def test_champion_p_elo_sums_to_one(self):
        """所有队伍 p_elo 之和应等于 1.0 (Plackett-Luce 概率分布)"""
        client = TestClient(app)
        r = client.get("/api/football/champion?pool=" + "冠军")
        data = r.json()
        total = sum(it["p_elo"] for it in data["items"])
        assert abs(total - 1.0) < 0.001, f"p_elo sum={total}, 期望 1.0"

    def test_champion_argentina_top(self):
        client = TestClient(app)
        r = client.get("/api/football/champion?pool=" + "冠军")
        data = r.json()
        # 列表已按 edge 降序, ARG 边缘最接近 0 (因为赔率已含 8% 抽水)
        arg = next((it for it in data["items"] if it["team"] == "阿根廷"), None)
        assert arg is not None
        # 在 fallback 下 edge 约等于 -0.08
        assert -0.15 < arg["edge"] < -0.05, f"ARG edge={arg['edge']} 偏离 -0.08 太远"
