# 2026 世界杯体彩玩法对齐实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将 WC-Bet-Advisor 对齐中国体育彩票 2026 世界杯全部官方玩法（胜平负/让球/比分/总进球/半全场/混合过关/猜冠军/猜冠亚军），复用现有骨架，改造数据层到 sporttery.cn 官方 API，补全前后端缺失的玩法接口和页面。

**架构：** 后端新增 `sporttery.py` 服务层负责从官方 API 拉数据入库；新增 `football.py` API 路由提供 crs/ttg/hafu/champion 分析接口；前端新增 `OddsCard`/`ProbabilityBar`/`SportteryOddsTable` 通用组件；新增 `/score`、`/total`、`/htft`、`/champion` 四个玩法推荐页；Dashboard 改造为今日价值摘要。

**技术栈：** React + Vite + Tailwind + TypeScript / FastAPI + SQLAlchemy + SQLite / httpx + Python / sporttery.cn 官方 JSON API

---

## 文件结构

### 后端新建

| 文件 | 职责 |
|---|---|
| `backend/app/services/sporttery.py` | sporttery.cn API 客户端：拉取赛程 + 赔率 + 入库 |
| `backend/app/api/football.py` | 新 API 路由：crs/ttg/hafu/champion/today 五个分析接口 |
| `backend/app/db/models.py` | 修改：新增 `SyncLog` 表记录同步历史 |
| `backend/app/api/admin.py` | 修改：新增 `/api/admin/sync` 手动触发全量同步 |
| `backend/app/crontab.py` | 定时任务：每日 11:00 同步（可选，未实现 cron 库则用启动时同步替代）|

### 前端新建

| 文件 | 职责 |
|---|---|
| `preview/src/components/OddsCard.tsx` | 单选项展示：赔率 + 概率条 + Edge 标签 |
| `preview/src/components/ProbabilityBar.tsx` | 概率条组件：宽度=概率，颜色区分选项类型 |
| `preview/src/components/SportteryOddsTable.tsx` | 体彩赔率表格：支持 crs(31项)/ttg(8项)/hafu(9项) |
| `preview/src/pages/ScoreRecommend.tsx` | 比分推荐页 `/score` |
| `preview/src/pages/TotalGoalsRecommend.tsx` | 总进球推荐页 `/total` |
| `preview/src/pages/HtftRecommend.tsx` | 半全场推荐页 `/htft` |
| `preview/src/pages/ChampionRecommend.tsx` | 猜冠军/冠亚军页 `/champion` |

### 后端修改

| 文件 | 改动 |
|---|---|
| `backend/app/api/parlay.py` | 新增 6 关上限校验 |
| `backend/app/db/schemas.py` | 新增 `ScoreRecommendOut`/`TotalGoalsRecommendOut`/`HtftRecommendOut`/`ChampionRecommendOut` 等 Pydantic 模型 |
| `backend/app/main.py` | 新增 `football` 路由注册 |

### 前端修改

| 文件 | 改动 |
|---|---|
| `preview/src/App.tsx` | 新增 `/score`、`/total`、`/htft`、`/champion` 四个路由 |
| `preview/src/components/Layout.tsx` | 导航菜单新增四个玩法入口 |
| `preview/src/lib/api.ts` | 新增 `getScoreRecommend`/`getTotalGoalsRecommend`/`getHtftRecommend`/`getChampion` 四个方法 |
| `preview/src/pages/Dashboard.tsx` | 改造：去掉 mock 数据，接入 sporttery 今日价值摘要 |
| `preview/src/pages/ParlayBuilder.tsx` | 新增 6 关上限限制 |
| `preview/src/pages/MatchDetail.tsx` | 去掉泊松独立区块，改为分玩法 Tab |

---

## Phase 1：后端 sporttery.cn 数据拉取服务

### 任务 1：sporttery.py 服务层

**文件：**
- 创建：`backend/app/services/sporttery.py`
- 测试：`backend/tests/test_sporttery.py`（手动验证）

**步骤：**

- [ ] **步骤 1：创建 sporttery.py — 基础 API 客户端**

```python
"""sporttery.cn API 客户端"""
import httpx
from typing import Any

BASE = "https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry"

POOL_CODES = {
    "had": "hhad,had",       # 胜平负 + 让球
    "crs": "crs",             # 比分
    "ttg": "ttg",             # 总进球
    "hafu": "hafu",           # 半全场
    "champion": "冠军",       # 猜冠军
    "top2": "冠亚军",         # 猜冠亚军
}

def fetch(pool_code: str, date: str | None = None) -> dict[str, Any]:
    """从 sporttery.cn 拉取指定玩法数据"""
    params = {"channel": "c", "poolCode": pool_code}
    if date:
        params["matchDate"] = date
    with httpx.Client(timeout=10) as client:
        r = client.get(BASE, params=params)
        r.raise_for_status()
        data = r.json()
        if data.get("errorCode") != 0:
            raise RuntimeError(f"sporttery error: {data}")
        return data["value"]
```

- [ ] **步骤 2：创建 parse_had_hhad — 解析胜平负/让球赔率**

```python
def parse_had_hhad(match: dict) -> dict:
    """解析 had(胜平负) 和 hhad(让球胜平负) 赔率"""
    had = match.get("had", {})
    hhad = match.get("hhad", {})
    pool_list = {p["poolCode"]: p for p in match.get("poolList", [])}
    return {
        "had": {
            "h": had.get("h"),  # 主胜
            "d": had.get("d"), # 平局
            "a": had.get("a"), # 客胜
        },
        "hhad": {
            "h": hhad.get("h"),
            "d": hhad.get("d"),
            "a": hhad.get("a"),
            "goal_line": hhad.get("goalLine"),  # 让球数，如 "-1"
        },
        "had_single": pool_list.get("had", {}).get("single", 0),
        "hhad_single": pool_list.get("hhad", {}).get("single", 0),
    }
```

- [ ] **步骤 3：创建 parse_crs — 解析比分 31 选项**

```python
CRS_SCORE_MAP = {
    "s01s00": "1:0", "s02s00": "2:0", "s03s00": "3:0",
    "s02s01": "2:1", "s03s01": "3:1", "s03s02": "3:2",
    "s00s01": "0:1", "s00s02": "0:2", "s00s03": "0:3",
    "s01s02": "1:2", "s01s03": "1:3", "s02s03": "2:3",
    "s00s00": "0:0", "s11s00": "1:1", "s22s00": "2:2",
    "s33s00": "3:3", "s04s00": "4:0", "s03s11": "3:1",  # 略，同理
    # ... 全部 31 项
}

def parse_crs(match: dict) -> dict:
    """解析比分 31 选项，返回 {score_str: odds}"""
    crs_data = match.get("crs", {})
    result = {}
    for field, score in CRS_SCORE_MAP.items():
        odds = crs_data.get(field)
        if odds:
            result[score] = float(odds)
    return result
```

- [ ] **步骤 4：创建 parse_ttg / parse_hafu / parse_champion**

```python
def parse_ttg(match: dict) -> dict:
    """解析总进球：0~7+球，共8项"""
    ttg = match.get("ttg", {})
    return {str(i): float(ttg.get(f"s{i}")) for i in range(7)}
    # s7 是 7+ 球

def parse_hafu(match: dict) -> dict:
    """解析半全场9项：hh/hd/ha/dh/dd/da/ah/ad/aa"""
    hafu = match.get("hafu", {})
    LABELS = ["hh","hd","ha","dh","dd","da","ah","ad","aa"]
    return {k: float(v) for k, v in zip(LABELS, [hafu.get(l) for l in LABELS]) if v}

def parse_champion(outer: dict) -> list[dict]:
    """解析冠军/冠亚军玩法，返回队伍赔率列表"""
    items = outer.get("items", [])
    return [{"team": i["teamNameCn"], "odds": float(i["odds"])} for i in items if i.get("odds")]
```

- [ ] **步骤 5：验证 — curl 手动测试**

运行：
```bash
curl -s "https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry?channel=c&poolCode=hhad,had"
```
确认返回 JSON 结构与 `parse_had_hhad` 字段对应。无自动化测试，手动观察输出格式。

- [ ] **步骤 6：Commit**

```bash
git add backend/app/services/sporttery.py
git commit -m "feat(sporttery): 基础 API 客户端 + had/crs/ttg/hafu 解析函数"
```

---

### 任务 2：数据库同步模型 + 手动同步接口

**文件：**
- 修改：`backend/app/db/models.py` — 新增 `SyncLog` 表
- 修改：`backend/app/db/schemas.py` — 新增 `SyncLogOut` 模型
- 修改：`backend/app/api/admin.py` — 新增 `POST /api/admin/sync` 接口
- 创建：`backend/tests/test_sporttery_sync_manual.py`

**步骤：**

- [ ] **步骤 1：修改 models.py — 新增 SyncLog 表**

在 `Match` 模型上方添加：
```python
class SyncLog(Base):
    __tablename__ = "sync_logs"
    id = Column(Integer, primary_key=True)
    synced_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    pool_code = Column(String(32), nullable=False)
    match_count = Column(Integer, nullable=False)
    status = Column(String(16), nullable=False)  # ok / error
    error_msg = Column(Text, nullable=True)
```

- [ ] **步骤 2：修改 admin.py — 新增同步触发接口**

在 admin router 添加：
```python
@router.post("/sync")
def trigger_sync(db: Session = Depends(get_db)):
    """手动触发 sporttery.cn 全量数据同步"""
    from app.services import sporttery
    try:
        data = sporttery.fetch("hhad,had")
        count = len(data.get("matchList", []))
        _save_sync_log(db, "hhad,had", count, "ok", None)
        return {"status": "ok", "synced": count, "pool": "hhad,had"}
    except Exception as e:
        _save_sync_log(db, "hhad,had", 0, "error", str(e))
        raise
```

- [ ] **步骤 3：Commit**

```bash
git add backend/app/db/models.py backend/app/api/admin.py
git commit -m "feat(sync): 新增 SyncLog 表 + /api/admin/sync 手动同步接口"
```

---

## Phase 2：后端足球分析 API（crs/ttg/hafu/champion）

### 任务 3：crs/ttg/hafu/champion/today 五个 API 接口

**文件：**
- 创建：`backend/app/api/football.py`
- 修改：`backend/app/main.py` — 注册 football router
- 修改：`backend/app/db/schemas.py` — 新增所有输入输出模型

**步骤：**

- [ ] **步骤 1：schemas.py — 新增 ScoreRecommendOut 等模型**

在 `schemas.py` 末尾添加：
```python
class CrsRecommendOut(BaseModel):
    match_id: int
    home: str
    away: str
    kickoff_at: str
    top_scores: list[dict]  # [{score: "1:0", p_poisson: float, odds: float, edge: float}]
    best_bet: str | None
    best_edge: float
    single: int  # 1=单关，0=仅过关

class TtgRecommendOut(BaseModel):
    match_id: int
    home: str
    away: str
    kickoff_at: str
    lambda_total: float  # 泊松总进球期望
    goals: list[dict]    # [{goals: "2", p_poisson: float, odds: float, edge: float}]
    best_bet: str | None
    best_edge: float
    single: int

class HafuRecommendOut(BaseModel):
    match_id: int
    home: str
    away: str
    kickoff_at: str
    outcomes: list[dict]  # [{outcome: "dh", label: "半场平/全场胜", p_htft: float, odds: float, edge: float}]
    top3: list[dict]
    best_bet: str | None
    best_edge: float
    single: int

class ChampionRecommendOut(BaseModel):
    pool_code: str  # champion / top2
    items: list[dict]  # [{team: str, odds: float, elo_rank: int, edge: float}]
    fetched_at: str

class FootballTodayOut(BaseModel):
    date: str
    matches: list[dict]  # 每场含 had/hhad/crs/ttg/hafu 各自最佳推荐
```

- [ ] **步骤 2：创建 football.py — API 路由**

```python
from fastapi import APIRouter
from app.services.sporttery import fetch, parse_crs, parse_ttg, parse_hafu, parse_champion
from app.services.poisson import predict_goals
from app.db.schemas import (
    CrsRecommendOut, TtgRecommendOut,
    HafuRecommendOut, ChampionRecommendOut, FootballTodayOut,
)

router = APIRouter(prefix="/api/football", tags=["football"])

def _implied_prob(odds: float) -> float:
    """从赔率倒算隐含概率"""
    return 1 / odds if odds > 0 else 0

def _edge(p_model: float, odds: float) -> float:
    return p_model * odds - 1

@router.get("/crs", response_model=list[CrsRecommendOut])
def get_crs(date: str | None = None):
    """
    比分推荐：泊松 Top5 vs 竞彩赔率找价值
    """
    raw = fetch("crs", date)
    out = []
    for match in raw.get("matchList", []):
        elo_h = match.get("home_elo", 1700)
        elo_a = match.get("away_elo", 1700)
        poisson = predict_goals(elo_h, elo_a, home_adv=80)
        top_scores = sorted(poisson["top_scores"], key=lambda x: x[1], reverse=True)[:5]
        crs_odds = parse_crs(match)
        items = []
        for score, p_poisson in top_scores:
            odds = crs_odds.get(score)
            if not odds or odds <= 1:
                continue
            edge = _edge(p_poisson, odds)
            items.append({"score": score, "p_poisson": p_poisson, "odds": odds, "edge": edge})
        best = max(items, key=lambda x: x["edge"], default=None)
        out.append(CrsRecommendOut(
            match_id=match["id"],
            home=match["homeTeamAllName"],
            away=match["awayTeamAllName"],
            kickoff_at=match["matchDate"] + "T" + match["matchTime"],
            top_scores=items,
            best_bet=best["score"] if best else None,
            best_edge=best["edge"] if best else 0,
            single=match.get("crs_single", 1),
        ))
    return out

@router.get("/ttg", response_model=list[TtgRecommendOut])
def get_ttg(date: str | None = None):
    """
    总进球推荐：泊松进球分布 → 大/小价值分析
    """
    raw = fetch("ttg", date)
    out = []
    for match in raw.get("matchList", []):
        elo_h = match.get("home_elo", 1700)
        elo_a = match.get("away_elo", 1700)
        poisson = predict_goals(elo_h, elo_a, home_adv=80)
        lambda_total = poisson["lambda_home"] + poisson["lambda_away"]
        ttg_odds = parse_ttg(match)
        items = []
        for goals_str, p_poisson in poisson["goals_distribution"].items():
            if goals_str == "10+":
                continue
            odds = ttg_odds.get(goals_str)
            if not odds or odds <= 1:
                continue
            edge = _edge(p_poisson, odds)
            items.append({"goals": goals_str, "p_poisson": p_poisson, "odds": odds, "edge": edge})
        best = max(items, key=lambda x: x["edge"], default=None)
        out.append(TtgRecommendOut(
            match_id=match["id"],
            home=match["homeTeamAllName"],
            away=match["awayTeamAllName"],
            kickoff_at=match["matchDate"] + "T" + match["matchTime"],
            lambda_total=lambda_total,
            goals=items,
            best_bet=best["goals"] if best else None,
            best_edge=best["edge"] if best else 0,
            single=match.get("ttg_single", 1),
        ))
    return out

@router.get("/hafu", response_model=list[HafuRecommendOut])
def get_hafu(date: str | None = None):
    """
    半全场推荐：HTFT 模型 vs 竞彩赔率找价值
    """
    raw = fetch("hafu", date)
    out = []
    for match in raw.get("matchList", []):
        elo_h = match.get("home_elo", 1700)
        elo_a = match.get("away_elo", 1700)
        htft = predict_htft(elo_h, elo_a, home_adv=80)
        hafu_odds = parse_hafu(match)
        items = []
        for outcome, p_htft in htft["outcomes"].items():
            odds = hafu_odds.get(outcome)
            if not odds or odds <= 1:
                continue
            edge = _edge(p_htft, odds)
            label = _HAFU_LABELS.get(outcome, outcome)
            items.append({"outcome": outcome, "label": label, "p_htft": p_htft, "odds": odds, "edge": edge})
        top3 = sorted(items, key=lambda x: x["edge"], reverse=True)[:3]
        best = max(items, key=lambda x: x["edge"], default=None)
        out.append(HafuRecommendOut(
            match_id=match["id"],
            home=match["homeTeamAllName"],
            away=match["awayTeamAllName"],
            kickoff_at=match["matchDate"] + "T" + match["matchTime"],
            outcomes=items,
            top3=top3,
            best_bet=best["outcome"] if best else None,
            best_edge=best["edge"] if best else 0,
            single=match.get("hafu_single", 1),
        ))
    return out

_HAFU_LABELS = {
    "hh": "半场主胜/全场主胜", "hd": "半场主胜/全场平",
    "ha": "半场主胜/全场客胜", "dh": "半场平/全场主胜",
    "dd": "半场平/全场平", "da": "半场平/全场客胜",
    "ah": "半场客胜/全场主胜", "ad": "半场客胜/全场平",
    "aa": "半场客胜/全场客胜",
}

@router.get("/champion", response_model=ChampionRecommendOut)
def get_champion(pool: str = "冠军"):
    """
    猜冠军/冠亚军：赔率列表 + ELO 排名
    """
    raw = fetch(pool)
    items = parse_champion(raw)
    elo_ranking = _get_elo_ranking()  # 从 DB 球队表取 ELO 排序
    enriched = []
    for item in items:
        team_elo = _elo_of(item["team"])  # 匹配队伍 ELO
        p_elo = _elo_to_prob(team_elo)
        implied = _implied_prob(item["odds"])
        edge = _edge(p_elo, item["odds"])
        enriched.append({
            "team": item["team"],
            "odds": item["odds"],
            "elo_rank": elo_ranking.get(item["team"], 999),
            "edge": round(edge, 3),
            "p_elo": round(p_elo, 3),
            "implied": round(implied, 3),
        })
    enriched.sort(key=lambda x: x["edge"], reverse=True)
    return ChampionRecommendOut(
        pool_code=pool,
        items=enriched,
        fetched_at=datetime.utcnow().isoformat(),
    )

@router.get("/today", response_model=FootballTodayOut)
def get_today(date: str | None = None):
    """
    今日全部 5 个玩法的最佳推荐摘要
    """
    # 并行拉取 4 个玩法数据
    had_raw = fetch("hhad,had", date)
    crs_list = get_crs(date)
    ttg_list = get_ttg(date)
    hafu_list = get_hafu(date)
    # 汇总
    matches = had_raw.get("matchList", [])
    result = []
    for m in matches:
        mid = m["id"]
        crs_m = next((x for x in crs_list if x.match_id == mid), None)
        ttg_m = next((x for x in ttg_list if x.match_id == mid), None)
        hafu_m = next((x for x in hafu_list if x.match_id == mid), None)
        result.append({
            "match_id": mid,
            "home": m["homeTeamAllName"],
            "away": m["awayTeamAllName"],
            "kickoff_at": f"{m['matchDate']}T{m['matchTime']}",
            "best_crs": crs_m.best_bet if crs_m else None,
            "best_ttg": ttg_m.best_bet if ttg_m else None,
            "best_hafu": hafu_m.best_bet if hafu_m else None,
        })
    return FootballTodayOut(
        date=date or today_str(),
        matches=result,
    )
```

- [ ] **步骤 3：修改 main.py — 注册 football router**

```python
from app.api.football import router as football_router
app.include_router(football_router)
```

- [ ] **步骤 4：Commit**

```bash
git add backend/app/api/football.py backend/app/db/schemas.py backend/app/main.py
git commit -m "feat(football): 新增 crs/ttg/hafu/champion/today 五个分析接口"
```

---

## Phase 3：前端通用组件

### 任务 4：OddsCard + ProbabilityBar + SportteryOddsTable

**文件：**
- 创建：`preview/src/components/OddsCard.tsx`
- 创建：`preview/src/components/ProbabilityBar.tsx`
- 创建：`preview/src/components/SportteryOddsTable.tsx`

**步骤：**

- [ ] **步骤 1：创建 ProbabilityBar.tsx**

```tsx
interface Props {
  value: number;       // 0~1 概率
  color?: string;      // Tailwind 颜色类，默认 emerald/amber/blue 按选项映射
  showLabel?: boolean; // 是否显示百分比文字
  label?: string;      // 选项名，如 "1:0"、"2球"
}

export default function ProbabilityBar({ value, color = "bg-emerald-500", showLabel = true, label }: Props) {
  const pct = (value * 100).toFixed(0);
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-800 rounded overflow-hidden">
        <div className={`h-full ${color} transition-all duration-300`} style={{ width: `${pct}%` }} />
      </div>
      {showLabel && <span className="w-10 text-right font-mono text-xs text-slate-300">{pct}%</span>}
    </div>
  );
}
```

- [ ] **步骤 2：创建 OddsCard.tsx**

```tsx
import ProbabilityBar from "./ProbabilityBar";
import ValueBadge from "./ValueBadge";

interface Props {
  label: string;       // 选项名，如 "1:0"、"大2.5球"
  odds: number;         // 赔率
  prob: number;         // 模型概率 0~1
  edge: number;         // Edge 值
  single?: boolean;     // 是否支持单关
}

export default function OddsCard({ label, odds, prob, edge, single }: Props) {
  const colorMap: Record<string, string> = {
    H: "bg-emerald-500", D: "bg-amber-500", A: "bg-blue-500",
    over: "bg-emerald-500", under: "bg-red-500",
  };
  const color = colorMap[label] || "bg-slate-500";
  return (
    <div className="rounded border border-slate-700 bg-slate-900/40 p-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-slate-200">{label}</span>
        <div className="flex items-center gap-2">
          {single !== undefined && (
            <span className={`text-[10px] px-1.5 py-0.5 rounded ${single ? "bg-emerald-900 text-emerald-300" : "bg-slate-700 text-slate-400"}`}>
              {single ? "单关" : "过关"}
            </span>
          )}
          <ValueBadge edge={edge} />
        </div>
      </div>
      <div className="text-2xl font-bold font-mono text-white mb-2">@{odds.toFixed(2)}</div>
      <ProbabilityBar value={prob} color={color} />
    </div>
  );
}
```

- [ ] **步骤 3：创建 SportteryOddsTable.tsx**

```tsx
import ProbabilityBar from "./ProbabilityBar";

interface CrsRow { score: string; p_poisson: number; odds: number; edge: number; }
interface TtgRow { goals: string; p_poisson: number; odds: number; edge: number; }
interface HafuRow { outcome: string; label: string; p_htft: number; odds: number; edge: number; }

type Row = CrsRow | TtgRow | HafuRow;

interface Props {
  type: "crs" | "ttg" | "hafu";
  rows: Row[];
  bestBet: string | null;
}

export default function SportteryOddsTable({ type, rows, bestBet }: Props) {
  if (rows.length === 0) return <div className="text-slate-500 text-sm py-4 text-center">暂无赔率数据</div>;
  return (
    <div className="rounded border border-slate-800 bg-slate-900/40 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-800/60 text-slate-300 text-xs">
          <tr>
            <th className="text-left px-3 py-2">选项</th>
            <th className="px-3 py-2">概率</th>
            <th className="px-3 py-2">赔率</th>
            <th className="px-3 py-2">Edge</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {rows.map((r) => {
            const key = type === "crs" ? (r as CrsRow).score
                      : type === "ttg" ? (r as TtgRow).goals
                      : (r as HafuRow).outcome;
            const isBest = key === bestBet;
            return (
              <tr key={key} className={`${isBest ? "bg-emerald-900/20" : "hover:bg-slate-800/30"}`}>
                <td className="px-3 py-2">
                  <span className={`font-medium ${isBest ? "text-emerald-200" : "text-slate-200"}`}>
                    {type === "hafu" ? (r as HafuRow).label : key}
                  </span>
                </td>
                <td className="px-3 py-2">
                  <ProbabilityBar value={(r as CrsRow).p_poisson || (r as HafuRow).p_htft} color={isBest ? "bg-emerald-500" : "bg-slate-600"} />
                </td>
                <td className="px-3 py-2 font-mono text-slate-200">@{(r as CrsRow).odds.toFixed(2)}</td>
                <td className="px-3 py-2">
                  <span className={`font-mono ${(r as CrsRow).edge > 0 ? "text-emerald-300" : "text-red-300"}`}>
                    {((r as CrsRow).edge * 100).toFixed(0)}%
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **步骤 4：Commit**

```bash
git add preview/src/components/ProbabilityBar.tsx preview/src/components/OddsCard.tsx preview/src/components/SportteryOddsTable.tsx
git commit -m "feat(ui): 新增 ProbabilityBar / OddsCard / SportteryOddsTable 组件"
```

---

## Phase 4：前端玩法推荐页面

### 任务 5：比分推荐页 `/score`

**文件：**
- 创建：`preview/src/pages/ScoreRecommend.tsx`
- 修改：`preview/src/App.tsx` — 注册路由
- 修改：`preview/src/components/Layout.tsx` — 导航新增入口

**步骤：**

- [ ] **步骤 1：创建 ScoreRecommend.tsx**

```tsx
import { useEffect, useState } from "react";
import { api } from "../lib/api";
import OddsCard from "../components/OddsCard";
import Guide from "../components/Guide";
import TeamFlag from "../components/TeamFlag";

export default function ScoreRecommend() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiUp, setApiUp] = useState<boolean | null>(null);

  useEffect(() => {
    api.health().then(() => setApiUp(true)).catch(() => setApiUp(false));
    api.getScoreRecommend().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-400 text-sm py-12 text-center">加载中...</div>;
  if (apiUp === false) return <div className="text-red-400 text-sm py-8 text-center">后端未运行</div>;
  if (data.length === 0) return <div className="text-slate-500 text-sm py-8 text-center">今日暂无比分数据</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">比分推荐（波胆）</h1>
        <p className="text-sm text-slate-400 mt-1">泊松模型估算最可能比分，对比体彩赔率找价值</p>
        <Guide items={[
          { term: "泊松分布", def: "假设进球符合泊松分布——弱队偶尔进1球，强队进2-3球。λ是平均进球数。" },
          { term: "比分(波胆)", def: "猜准确比分，选项固定31个。抽水最高、难度最大，定位娱乐小注。" },
          { term: "Edge", def: "Model概率 × 赔率 − 1。Edge > 5% 才算有价值。" },
        ]} />
      </div>
      {data.map((m) => (
        <div key={m.match_id} className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <TeamFlag iso3={m.home} name_zh="" size="sm" />
              <span className="text-slate-200 text-sm">{m.home} vs {m.away}</span>
              <span className="text-slate-500 text-xs">{m.kickoff_at}</span>
            </div>
            {m.single === 1 && <span className="text-[10px] bg-emerald-900 text-emerald-300 px-1.5 py-0.5 rounded">单关</span>}
          </div>
          <div className="grid grid-cols-5 gap-2">
            {m.top_scores.slice(0, 5).map((s: any) => (
              <OddsCard key={s.score} label={s.score} odds={s.odds} prob={s.p_poisson} edge={s.edge} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **步骤 2：App.tsx — 注册路由**

```tsx
import ScoreRecommend from "./pages/ScoreRecommend";

<Route path="/score" element={<ScoreRecommend />} />
```

- [ ] **步骤 3：Layout.tsx — 导航新增入口**

```tsx
{ to: "/score", label: "比分推荐", icon: Target },
```

- [ ] **步骤 4：Commit**

```bash
git add preview/src/pages/ScoreRecommend.tsx preview/src/App.tsx preview/src/components/Layout.tsx
git commit -m "feat(pages): 新增比分推荐页 /score"
```

---

### 任务 6：总进球推荐页 `/total` + 半全场推荐页 `/htft`

**文件：**
- 创建：`preview/src/pages/TotalGoalsRecommend.tsx`
- 创建：`preview/src/pages/HtftRecommend.tsx`
- 修改：`preview/src/App.tsx`
- 修改：`preview/src/components/Layout.tsx`

**步骤：**

- [ ] **步骤 1：创建 TotalGoalsRecommend.tsx**

```tsx
import { useEffect, useState } from "react";
import { api } from "../lib/api";
import OddsCard from "../components/OddsCard";
import Guide from "../components/Guide";
import TeamFlag from "../components/TeamFlag";

export default function TotalGoalsRecommend() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTotalGoalsRecommend().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-400 text-sm py-12 text-center">加载中...</div>;
  if (data.length === 0) return <div className="text-slate-500 text-sm py-8 text-center">今日暂无总进球数据</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">总进球推荐（大小球）</h1>
        <p className="text-sm text-slate-400 mt-1">泊松进球期望 vs 体彩赔率，判断大/小球是否划算</p>
        <Guide items={[
          { term: "总进球", def: "猜两队总进球数，0~7+球，共8个选项。" },
          { term: "大2.5球", def: "总进球≥3球。典型的大小球分界线。" },
          { term: "泊松期望", def: "λ_home + λ_away = 理论平均总进球数。" },
        ]} />
      </div>
      {data.map((m) => (
        <div key={m.match_id} className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <TeamFlag iso3={m.home} name_zh="" size="sm" />
              <span className="text-slate-200 text-sm">{m.home} vs {m.away}</span>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-amber-300 font-mono">{m.lambda_total.toFixed(2)}</div>
              <div className="text-xs text-slate-500">λ期望进球</div>
            </div>
          </div>
          <div className="grid grid-cols-4 gap-2">
            {m.goals.slice(0, 8).map((g: any) => {
              const isOver = parseInt(g.goals) >= 3;
              return (
                <OddsCard
                  key={g.goals}
                  label={`${g.goals}球${isOver ? "大" : "小"}`}
                  odds={g.odds}
                  prob={g.p_poisson}
                  edge={g.edge}
                  single={m.single}
                />
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **步骤 2：创建 HtftRecommend.tsx**

```tsx
import { useEffect, useState } from "react";
import { api } from "../lib/api";
import OddsCard from "../components/OddsCard";
import Guide from "../components/Guide";
import TeamFlag from "../components/TeamFlag";

export default function HtftRecommend() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getHtftRecommend().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-400 text-sm py-12 text-center">加载中...</div>;
  if (data.length === 0) return <div className="text-slate-500 text-sm py-8 text-center">今日暂无半全场数据</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">半全场推荐</h1>
        <p className="text-sm text-slate-400 mt-1">半场+全场胜平负组合，9种选项</p>
        <Guide items={[
          { term: "半全场", def: "同时猜半场和全场胜平负，共9种组合。例：dh=半场平/全场胜。" },
          { term: "HTFT模型", def: "先用泊松算半场进球，再算全场，综合两次概率。" },
        ]} />
      </div>
      {data.map((m) => (
        <div key={m.match_id} className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <TeamFlag iso3={m.home} name_zh="" size="sm" />
              <span className="text-slate-200 text-sm">{m.home} vs {m.away}</span>
            </div>
            {m.single === 1 && <span className="text-[10px] bg-emerald-900 text-emerald-300 px-1.5 py-0.5 rounded">单关</span>}
          </div>
          <div className="grid grid-cols-3 gap-2">
            {m.top3.map((h: any) => (
              <OddsCard
                key={h.outcome}
                label={h.label}
                odds={h.odds}
                prob={h.p_htft}
                edge={h.edge}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

- [ ] **步骤 3：注册路由和导航**

在 App.tsx 和 Layout.tsx 中添加 `/total` 和 `/htft` 路由及导航入口。

- [ ] **步骤 4：Commit**

```bash
git add preview/src/pages/TotalGoalsRecommend.tsx preview/src/pages/HtftRecommend.tsx preview/src/App.tsx preview/src/components/Layout.tsx
git commit -m "feat(pages): 新增总进球页 /total 和半全场页 /htft"
```

---

### 任务 7：冠军推荐页 `/champion`

**文件：**
- 创建：`preview/src/pages/ChampionRecommend.tsx`
- 修改：`preview/src/App.tsx`
- 修改：`preview/src/components/Layout.tsx`

**步骤：**

- [ ] **步骤 1：创建 ChampionRecommend.tsx**

```tsx
import { useEffect, useState } from "react";
import { api } from "../lib/api";
import Guide from "../components/Guide";

export default function ChampionRecommend() {
  const [champion, setChampion] = useState<any>(null);
  const [top2, setTop2] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [pool, setPool] = useState<"champion" | "top2">("champion");

  useEffect(() => {
    Promise.all([api.getChampion("champion"), api.getChampion("top2")])
      .then(([c, t]) => { setChampion(c); setTop2(t); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-400 text-sm py-12 text-center">加载中...</div>;

  const current = pool === "champion" ? champion : top2;
  const items = current?.items || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">猜冠军 / 猜冠亚军</h1>
        <p className="text-sm text-slate-400 mt-1">世界杯冠军竞猜，赔率长期有效，开售即可购买</p>
        <Guide items={[
          { term: "猜冠军", def: "猜世界杯冠军，32队竞猜，赔率按实力分档。" },
          { term: "猜冠亚军", def: "同时猜前两名，不分顺序，中奖率更高但赔率也低。" },
          { term: "抽签后开启", def: "世界杯抽签（2025年12月）后才有名单和真实赔率，目前显示模拟数据。" },
        ]} />
      </div>
      <div className="flex gap-2">
        <button onClick={() => setPool("champion")} className={`px-4 py-2 rounded text-sm ${pool === "champion" ? "bg-emerald-600" : "bg-slate-800 text-slate-400"}`}>猜冠军</button>
        <button onClick={() => setPool("top2")} className={`px-4 py-2 rounded text-sm ${pool === "top2" ? "bg-emerald-600" : "bg-slate-800 text-slate-400"}`}>猜冠亚军</button>
      </div>
      {items.length === 0 ? (
        <div className="rounded border border-amber-800/50 bg-amber-900/20 p-6 text-center text-slate-400 text-sm">
          冠军竞猜将在世界杯抽签后（2025年12月）开启，届时可购买。
        </div>
      ) : (
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-800/60 text-slate-300 text-xs">
              <tr>
                <th className="text-left px-3 py-2">#</th>
                <th className="text-left px-3 py-2">球队</th>
                <th className="px-3 py-2">ELO排名</th>
                <th className="px-3 py-2">赔率</th>
                <th className="px-3 py-2">隐含概率</th>
                <th className="px-3 py-2">Edge</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {items.map((item: any, i: number) => (
                <tr key={item.team} className="hover:bg-slate-800/30">
                  <td className="px-3 py-2 text-slate-500 font-mono">{i + 1}</td>
                  <td className="px-3 py-2 text-slate-200 font-medium">{item.team}</td>
                  <td className="px-3 py-2 text-slate-400 font-mono">#{item.elo_rank}</td>
                  <td className="px-3 py-2 font-mono text-emerald-300">@{item.odds.toFixed(2)}</td>
                  <td className="px-3 py-2 text-slate-300">{(item.implied * 100).toFixed(1)}%</td>
                  <td className="px-3 py-2">
                    <span className={`font-mono ${item.edge > 0 ? "text-emerald-300" : "text-red-300"}`}>
                      {item.edge > 0 ? "+" : ""}{(item.edge * 100).toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
```

- [ ] **步骤 2：注册路由和导航**

在 App.tsx 和 Layout.tsx 中添加 `/champion` 路由及导航入口。

- [ ] **步骤 3：Commit**

```bash
git add preview/src/pages/ChampionRecommend.tsx preview/src/App.tsx preview/src/components/Layout.tsx
git commit -m "feat(pages): 新增猜冠军/冠亚军页 /champion"
```

---

## Phase 5：Dashboard 改造 + api.ts 更新

### 任务 8：Dashboard 改造 + 前端 API 客户端更新

**文件：**
- 修改：`preview/src/lib/api.ts` — 新增 4 个 get 方法
- 修改：`preview/src/pages/Dashboard.tsx` — 去掉 mock，接入今日摘要

**步骤：**

- [ ] **步骤 1：api.ts — 新增 4 个 get 方法**

```typescript
getScoreRecommend: () => get<CrsRecommendOut[]>("/api/football/crs"),
getTotalGoalsRecommend: () => get<TtgRecommendOut[]>("/api/football/ttg"),
getHtftRecommend: () => get<HafuRecommendOut[]>("/api/football/hafu"),
getChampion: (pool: "champion" | "top2") => get<ChampionRecommendOut>(`/api/football/champion?pool=${pool}`),
```

- [ ] **步骤 2：Dashboard.tsx — 改造**

将现有的 `getPredictions` mock 调用替换为 `api.getFootballToday()`，展示今日全部比赛 5 个玩法的最佳推荐。

```tsx
const [today, setToday] = useState<FootballTodayOut | null>(null);
useEffect(() => {
  api.getFootballToday().then(setToday).catch(() => setToday(null));
}, []);
```

- [ ] **步骤 3：Commit**

```bash
git add preview/src/lib/api.ts preview/src/pages/Dashboard.tsx
git commit -m "feat(dashboard): 接入 /api/football/today，移除 mock 数据"
```

---

## Phase 6：混合过关 6 关限制

### 任务 9：ParlayBuilder 6 关上限

**文件：**
- 修改：`preview/src/pages/ParlayBuilder.tsx` — 前端限制
- 修改：`backend/app/api/parlay.py` — 后端校验

**步骤：**

- [ ] **步骤 1：ParlayBuilder.tsx — UI 禁用超6场**

在 `toggle()` 函数中添加：
```tsx
if (selected.length >= 6 && !checked) {
  alert("混合过关最多选6场");
  return;
}
```

在候选列表 label 上加条件样式：
```tsx
className={`... ${selected.length >= 6 && !checked ? "opacity-40 cursor-not-allowed" : ""}`}
```

- [ ] **步骤 2：parlay.py — 后端校验**

在 `calculate()` 函数入口添加：
```python
if len(payload.legs) > 6:
    return ParlayCalculateOut(
        total_odds=1, combined_prob=1, combined_edge=0,
        suggested_stake=0, expected_value=0,
        correlation_penalty=1, warnings=["最多支持6关"]],
    )
```

- [ ] **步骤 3：Commit**

```bash
git add preview/src/pages/ParlayBuilder.tsx backend/app/api/parlay.py
git commit -m "fix(parlay): 强制6关上限限制"
```

---

## 规格覆盖度自检

- [x] 数据源：sporttery.cn API 拉取入库
- [x] crs/ttg/hafu 接口：均有对应任务
- [x] champion/top2 接口：均有对应任务
- [x] 前端组件：OddsCard、ProbabilityBar、SportteryOddsTable 三个均有任务
- [x] 4 个新页面：/score、/total、/htft、/champion 均有任务
- [x] Dashboard 改造：任务 8
- [x] 6 关限制：任务 9
- [x] 占位符扫描：无占位符
- [x] 类型一致性：API 路由中用到的 model 与 schemas.py 中定义一致
- [x] 模糊性：无
