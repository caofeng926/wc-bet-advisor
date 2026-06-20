# WC-Bet-Advisor 详细设计文档

> 版本: v1.0 · 日期: 2026-06-10 · 配套 PRD v1.0

## 1. 架构总览

`mermaid
graph TB
  subgraph Browser
    UI[React Frontend<br/>Ant Design + ECharts]
  end

  subgraph Backend [FastAPI Backend]
    API[API Layer]
    REC[Recommender]
    VE[Value Engine]
    M1[Model: ELO]
    M2[Model: Poisson]
    ING[Odds Ingest]
    POLY[Polymarket Client]
    MAP[Polymarket Mapper]
    CRON[APScheduler]
  end

  subgraph Data
    DB[(SQLite)]
    OD[football-data.org]
    POL[Polymarket]
    OA[Odds API]
    MA[Manual Import]
  end

  UI <-->|REST/JSON| API
  API --> REC
  API --> VE
  REC --> VE
  REC --> M1
  REC --> M2
  VE --> M1
  VE --> M2
  ING --> OD
  ING --> OA
  ING --> MA
  POLY --> POL
  MAP --> POLY
  MAP --> DB
  CRON --> ING
  CRON --> POLY
  CRON --> REC
  API --> DB
  ING --> DB
  VE --> DB
  REC --> DB
`

---

## 2. 技术选型

| 层 | 选型 | 版本 | 理由 |
|---|---|---|---|
| 前端框架 | React | 18.x | 主流 + 生态 |
| 构建 | Vite | 5.x | 启动快 |
| 语言 | TypeScript | 5.x | 强类型 |
| UI 库 | Ant Design | 5.x | 组件全、中文友好 |
| 图表 | ECharts | 5.x | 中文图表优秀 |
| 状态 | Zustand | 4.x | 轻量 |
| HTTP | Axios | 1.x | 拦截器方便 |
| 路由 | React Router | 6.x | 标准 |
| 后端框架 | FastAPI | 0.110+ | 异步、自动文档 |
| ORM | SQLAlchemy | 2.0+ | 主流 |
| 数据库 | SQLite | 3.x | 轻量 |
| 调度 | APScheduler | 3.x | 简单 |
| HTTP 客户端 | httpx | 0.27+ | 异步 |
| 数值 | numpy + scipy | latest | 泊松计算 |
| 测试 | pytest + vitest | latest | 标准 |
| 容器 | Docker + docker-compose | latest | 一键起 |

---

## 3. 数据模型

`python
# teams
class Team(Base):
    __tablename__ = "teams"
    id: int (PK)
    fifa_id: str            # football-data.org id
    name: str
    name_zh: str
    name_en: str
    iso3: str               # ARG/BRA/...
    iso2: str               # AR/BR/...
    fifa_rank: int
    elo: int
    group: str              # A/B/C/...
    confederation: str      # UEFA/CONMEBOL/...
    coach: str (nullable)
    is_host: bool
    notes: str (nullable)

# matches
class Match(Base):
    __tablename__ = "matches"
    id: int (PK)
    external_id: str
    home_team_id: int (FK)
    away_team_id: int (FK)
    stage: str              # "group"/"R16"/"QF"/"SF"/"F"
    group: str (nullable)
    matchday: int
    kickoff_at: datetime
    venue: str
    status: str             # "scheduled"/"live"/"ft"/"postponed"
    ft_home: int (nullable)
    ft_away: int (nullable)
    ht_home: int (nullable)
    ht_away: int (nullable)
    betting_close_at: datetime (nullable)
    betting_close_source: str  # "rule"/"manual"/"tba"

# odds(时序)
class Odd(Base):
    __tablename__ = "odds"
    id: int (PK)
    match_id: int (FK)
    bookmaker: str          # "Pinnacle"/"Bet365"/"手工-A"/...
    market: str             # "1x2"/"ah"/"ou"/"cs"/"tg"/"htft"
    selection: str          # "H"/"D"/"A" / "H(-1)"/"A(+1)" / "1-0" / ...
    line: float (nullable)  # 让球数/大小球
    odds: float
    ts: datetime
    vig_pct: float (nullable)

# polymarket_prices
class PolymarketPrice(Base):
    __tablename__ = "polymarket_prices"
    id: int (PK)
    market_id: str
    question: str
    team_id: int (FK, nullable)
    match_id: int (FK, nullable)
    market_type: str        # "winner"/"group_winner"/"advance"/"match"
    outcome: str            # "Yes"/"No"
    price: float            # 0-1
    volume_24h: float
    liquidity: float
    ts: datetime

# predictions
class Prediction(Base):
    __tablename__ = "predictions"
    id: int (PK)
    match_id: int (FK)
    market: str
    selection: str
    p_elo: float
    p_form: float
    p_market: float
    p_polymarket: float
    p_final: float
    edge: float
    kelly: float
    value_score: float
    bookmaker: str
    odds: float
    ts: datetime

# recommendations
class Recommendation(Base):
    __tablename__ = "recommendations"
    id: int (PK)
    match_id: int (FK, nullable)
    period_id: int (FK, nullable)
    kind: str               # "single"/"parlay"/"lotto14"/"lotto9"
    selections_json: str
    total_odds: float
    p_combined: float
    edge_combined: float
    ev: float
    kelly_combined: float
    recommended_stake_pct: float
    ts: datetime

# lotto_periods
class LottoPeriod(Base):
    __tablename__ = "lotto_periods"
    id: int (PK)
    kind: str               # "14场"/"任选9"/"6半全"/"4进球"
    season: str             # "2026"
    issue_no: str
    first_match_kickoff: datetime
    close_at: datetime
    status: str             # "selling"/"closed"/"drawn"
    draw_result: str (nullable)
    source: str

# slips
class Slip(Base):
    __tablename__ = "slips"
    id: int (PK)
    period_id: int (FK, nullable)
    title: str
    selections_json: str
    total_odds: float
    stake: float
    notes: str (nullable)
    result: str (nullable)  # "win"/"lose"/"void"/"partial"
    payout: float (nullable)
    pnl: float (nullable)
    created_at: datetime
    settled_at: datetime (nullable)

# ledger
class LedgerEntry(Base):
    __tablename__ = "ledger"
    id: int (PK)
    slip_id: int (FK)
    actual_stake: float
    result: str
    actual_payout: float
    roi_pct: float
    settled_at: datetime
`

---

## 4. API 设计

### 4.1 REST 端点

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | /api/matches | 赛程列表 |
| GET | /api/matches/{id} | 单场详情 |
| GET | /api/matches/{id}/odds | 单场所有赔率 |
| GET | /api/matches/{id}/predictions | 单场所有市场预测 |
| GET | /api/matches/{id}/polymarket | 单场 Polymarket 视图 |
| GET | /api/value-bets | 价值投注池 |
| GET | /api/recommendations/today | Dashboard 推荐流 |
| POST | /api/slips | 保存方案 |
| GET | /api/slips | 方案列表 |
| GET | /api/slips/{id} | 方案详情 |
| POST | /api/slips/{id}/settle | 结算 |
| GET | /api/pnl | 收益统计 |
| GET | /api/lotto/periods | 传统足彩销售期 |
| GET | /api/lotto/{period_id}/recommendation | 14 场方案 |
| POST | /api/kelly/calc | 凯利试算 |
| POST | /api/admin/odds/import | 管理员手工导入 |
| POST | /api/admin/close-time/set | 覆盖截止时间 |
| POST | /api/admin/results/import | 录入开奖结果 |
| GET | /api/admin/countdown | 最近截止时间 |
| GET | /api/admin/jobs/status | 调度任务状态 |

### 4.2 响应示例

GET /api/value-bets:

`json
{
  "items": [
    {
      "match_id": 23,
      "home": "ESP", "away": "CRC",
      "kickoff_at": "2026-06-23T20:00:00Z",
      "minutes_to_close": 240,
      "market": "ah",
      "selection": "ESP(-1)",
      "odds": 3.40,
      "p_elo": 0.30,
      "p_market": 0.29,
      "p_polymarket": 0.34,
      "p_final": 0.31,
      "edge": 0.054,
      "kelly": 0.054,
      "recommended_stake_pct": 0.014,
      "reasons": [
        "Polymarket 显著高于市场(分歧 +5%)",
        "ELO 差 280,Costa Rica 近 10 场场均丢 1.8"
      ]
    }
  ],
  "meta": {"total": 12, "min_edge": 0.05, "ts": "..."}
}
`

GET /api/admin/countdown:

`json
{
  "next_close_at": "2026-06-12T08:55:00Z",
  "context": {"kind": "竞彩", "match": "BRA vs CRO"},
  "seconds_remaining": 7740,
  "status": "selling"
}
`

---

## 5. 关键算法

### 5.1 价值识别

`python
def calc_recommendation(match, market, selection, odds, p_components):
    weights = settings.fusion_weights  # {"elo":0.4,"form":0.2,"market":0.2,"polymarket":0.2}
    p_final = sum(p_components[k] * weights[k] for k in weights)

    edge = p_final * odds - 1
    b = odds - 1
    kelly = (b * p_final - (1 - p_final)) / b if b > 0 else 0
    stake_pct = max(0, kelly * settings.kelly_fraction)
    stake_pct = min(stake_pct, 0.05)  # 单注封顶 5%

    pol_disagreement = abs(p_components.get("polymarket", 0) - p_components.get("market", 0))
    value_score = edge * (1 + 0.2 * pol_disagreement)

    if edge < settings.min_edge or kelly <= 0 or p_final < 0.10:
        return None

    return Recommendation(...)
`

### 5.2 凯利公式

`python
def kelly_fraction(p: float, odds: float) -> float:
    if p <= 0 or odds <= 1:
        return 0
    b = odds - 1
    q = 1 - p
    return (b * p - q) / b
`

### 5.3 泊松进球模型

`python
def predict_goals(elo_home, elo_away, home_advantage=100):
    mu = 1.4
    elo_diff = (elo_home + home_advantage - elo_away) / 200
    lam_home = np.exp(mu + elo_diff * 0.15)
    lam_away = np.exp(mu - elo_diff * 0.15)

    max_goals = 5
    matrix = np.zeros((max_goals+1, max_goals+1))
    for i in range(max_goals+1):
        for j in range(max_goals+1):
            matrix[i, j] = poisson.pmf(i, lam_home) * poisson.pmf(j, lam_away)
    return matrix
`

### 5.4 14 场胜负彩搜索

`python
def lotto14_search(match_predictions, top_n=7):
    main_ticket = [max(['H','D','A'], key=lambda x: p[x]) for p in match_predictions]
    backup_tickets = []
    for _ in range(6):
        ticket = []
        for p in match_predictions:
            if p['H'] > 0.6: ticket.append('H')
            elif p['A'] > 0.6: ticket.append('A')
            elif p['D'] > 0.3: ticket.append('D')
            else: ticket.append(['H','D','A'])
        backup_tickets.append(ticket)
    return main_ticket, backup_tickets
`

### 5.5 串关相关性惩罚

`python
def parlay_correlation_penalty(legs):
    penalty = 1.0
    for i, a in enumerate(legs):
        for b in legs[i+1:]:
            if a.match.group == b.match.group:
                penalty *= 0.7
            elif abs((a.match.kickoff_at - b.match.kickoff_at).hours) < 6:
                penalty *= 0.85
    return penalty
`

---

## 6. 前端页面设计

### 6.1 全局布局

`
┌─────────────────────────────────────────────────┐
│  截止雷达:本期销售中 · 距截止 02:14:33           │  <- 固定顶部 banner
├─────────────────────────────────────────────────┤
│  [Logo] WC-Bet-Advisor      [设置] [关于]        │
├──────┬──────────────────────────────────────────┤
│ 导航  │             页面内容                     │
├──────┴──────────────────────────────────────────┤
│  ⚠️ 本工具仅供数据分析参考,不构成购彩建议        │
└─────────────────────────────────────────────────┘
`

### 6.2 页面清单

| 路由 | 页面 | 关键组件 |
|---|---|---|
| / | Dashboard | CountdownBanner TodayPicks RoiChart QuickLinks |
| /fixtures | 赛程列表 | MatchRow Filters |
| /matches/:id | 单场详情 | OddsTable ValueHeatmap KellyCalculator PolymarketGauge |
| /parlay | 串关构造 | LegPicker CorrelationMatrix OddsCombine |
| /lotto14 | 14 场胜负彩 | LottoGrid AutoGenButton BackupTickets |
| /lotto9 | 任选九 | 同上 |
| /slips | 方案库 | SlipList SlipCard QuickSettle |
| /pnl | 复盘 | PnlByMarket PnlByDate HitRateGauge |
| /settings | 设置 | KellyFraction Bankroll FusionWeights Theme |
| /admin | 后台 | OddsImport CloseTimeManager ResultImport JobsStatus |

---

## 7. 截止时间模块设计

### 7.1 数据流

`
[管理员录入/规则倒推]
   ↓
[matches.betting_close_at]   <- 竞彩单场
[lotto_periods.close_at]     <- 传统足彩销售期
   ↓
[前端全局 banner: GET /api/admin/countdown]
[前端每 10s 拉一次]
   ↓
[卡片过期 → 后端 /api/value-bets 过滤 + 前端置灰]
`

### 7.2 4 个默认决策

| 决策点 | 默认值 | 可调入口 |
|---|---|---|
| 缓冲时长 | 竞彩 = 5 min | Settings 改 |
| 截止后行为 | **置灰可看**(可复盘) | - |
| 多玩法同场 | **同时显示**,详情 tab 切 | - |
| 录入负担 | **自动推算 + 偏差 > 1h 弹提醒** | - |

### 7.3 倒计时状态色

`python
def status_color(seconds_remaining):
    if seconds_remaining < 0: return "gray"  # 已截止
    if seconds_remaining < 1800: return "red"  # < 30min
    if seconds_remaining < 7200: return "yellow"  # < 2h
    return "green"
`

---

## 8. 部署架构

`yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes: ["./data:/app/data"]
    environment:
      - DATABASE_URL=sqlite:///./data/wc_bet.db
      - POLYMARKET_API_BASE=https://gamma-api.polymarket.com
      - FOOTBALL_DATA_API_KEY=
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]
    environment:
      - VITE_API_BASE=http://localhost:8000
`

启动:

`ash
cp .env.example .env
docker compose up
# 浏览器打开 http://localhost:5173
`

---

## 9. 测试策略

### 9.1 单元测试

- 	est_odds_ingest.py:多家赔率归一、去尾均值
- 	est_value_engine.py:edge/凯利计算(对照手算)
- 	est_kelly.py:边界(odds=1, p=0, p=1)
- 	est_poisson.py:λ 合理性、概率和 ≈ 1
- 	est_lotto14.py:14 场固定结果下搜索能收敛
- 	est_polymarket_mapper.py:多国名匹配(ISO3/英文/中文)

### 9.2 集成测试

- /api/value-bets 在 mock 数据集 Top5 至少 3 个 edge>0
- 串关构造器相关性惩罚生效
- 截止时间过滤生效

### 9.3 端到端

- Playwright 跑通 Dashboard → 详情 → 保存 → 结算 → 复盘
- Docker 启动后 5 分钟内可访问

### 9.4 历史回测

- 用 2018/2022 真实比赛跑一遍模型
- 报告:命中率、平均赔率、ROI、最大回撤
- 回测结果放 Settings 页面,公开透明

---

## 10. 开发规范

| 项 | 规范 |
|---|---|
| 代码风格 | 前端 ESLint + Prettier,后端 Black + Ruff |
| 命名 | 前端 camelCase,后端 snake_case,DB 表 snake_case |
| Git | 简短 commit msg,feature 分支,PR 合并 |
| 日志 | 后端 loguru,关键操作(数据拉取/推荐/结算)记 info |
| 错误处理 | 后端全局异常中间件,前端 ErrorBoundary |
| 配置 | 环境变量走 .env,敏感项不进 git |
| 文档 | README + API 文档(FastAPI 自动) + 本设计文档 |

---

## 11. 风险与缓解(技术视角)

| 风险 | 缓解 |
|---|---|
| Polymarket API 变更 | 抽象 PolymarketClient 接口,适配器易替换 |
| 赔率拉取失败 | 多源 + 重试 + 降级到上期数据 + UI 标"数据陈旧" |
| 推荐计算超时 | 后台异步任务 + 前端轮询 |
| SQLite 并发 | WAL 模式 + 单写多读场景够用 |
| 截止时间误判 | 管理员覆盖 + 偏差提醒 |

---

## 12. 交付物清单

- [ ] 完整前后端代码
- [ ] Docker compose 一键起
- [ ] .env.example 模板
- [ ] README(快速开始)
- [ ] 本设计文档
- [ ] PRD 文档
- [ ] 单元测试 + 集成测试
- [ ] 一份 mock 数据集(用于演示)
- [ ] 2018/2022 回测报告