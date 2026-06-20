# 2026 世界杯体彩玩法对齐规格说明

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将现有 WC-Bet-Advisor 项目对齐中国体育彩票 2026 世界杯全部官方玩法，在赛前提供有模型依据的竞猜建议。

**架构：** 复用现有 React + FastAPI + SQLite 骨架，改造数据层（从 mock 切换到体彩官方 sporttery.cn API），补全前端分玩法展示页，后端新增对应接口。分析引擎（ELO 概率模型、泊松进球分布、Kelly 资金管理）保留复用。

**技术栈：** React + Vite + Tailwind + TypeScript / FastAPI + SQLAlchemy + SQLite / sporttery.cn 官方 JSON API

---

## 一、数据源改造

### 1.1 体彩官方 API (sporttery.cn)

| 玩法 | poolCode | 数据字段 |
|---|---|---|
| 胜平负 + 让球 | `hhad,had` | `had.h/d/a`，`hhad.h/d/a/goalLine` |
| 比分 | `crs` | 31项：`s01s00`=1:0 … `s5s2`=5:2 + `s1sh/s1sd/s1sa` |
| 总进球 | `ttg` | `ttg.s0`~`ttg.s7`（0球~7+球） |
| 半全场 | `hafu` | `hafu.hh/hd/ha/dh/dd/da/ah/ad/aa` |
| 冠军 | `冠军` | 32支队伍列表 + 各自赔率 |
| 冠亚军 | `冠亚军` | 32支队伍列表 + 各自赔率 |

**API 端点：**
```
https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry?channel=c&poolCode={poolCode}
```

- 响应中每场比赛含 `poolList[]`，每个玩法对象含 `single` 字段（1=支持单关，0=仅过关）
- 赔率字段命名见上表

### 1.2 现有骨架复用策略

| 现有模块 | 处置 |
|---|---|
| `api.ts` 前端客户端 | 改造：新增 `getSporttery(crs/ttg/hafu/champion)` 方法 |
| `recommendations.py` 后端 | 改造：从 sporttery.cn 拉数据，叠加 ELO/泊松概率做价值分析 |
| `poisson.py` 服务 | 保留：计算泊松进球分布，映射到比分/总进球/半全场选项 |
| `htft.py` 服务 | 保留：半场全场预测，复用于半全场推荐 |
| `kelly.py` 服务 | 保留：Kelly 公式计算投注比例 |
| `seed.py` | 废弃：不再需要 mock 数据 |
| `polymarket.py` | 保留或废弃：Polymarket 数据用于赛前参考 |

---

## 二、前端页面结构

### 2.1 导航结构（不变）

```
首页 Dashboard        → 今日价值推荐（胜平负/让球）
14场胜负彩 / 任选九   → 现有 Lotto14 页面
比分推荐             → 【新增】足球波胆推荐页
总进球推荐            → 【新增】大小球推荐页
半全场推荐            → 【新增】半全场推荐页
混合过关             → 现有 ParlayBuilder（加 6关限制）
猜冠军/冠亚军         → 【新增】冠军竞猜页
方案库/复盘          → 现有 Slips 页面
```

### 2.2 新增页面

#### 2.2.1 比分推荐页 (`/score`) — 新建
- 读取今日全部比赛
- 对每场：泊松分布 → Top5 比分概率
- 对比 sporttery.cn `crs` 赔率，找出"价值"选项（Edge ≥ 5%）
- 展示：Top5 比分概率条 + 对应赔率 + Edge 标签
- 说明泊松模型是什么（λ 期望进球数的通俗解释）
- 单关状态：读 `poolList.crs.single`

#### 2.2.2 总进球推荐页 (`/total`) — 新建
- 对每场：泊松分布 → 总进球期望（λ_home + λ_away）
- 竞彩总进球 8 选项：0/1/2/3/4/5/6/7+
- 泊松积分得到各进球数概率，对比赔率找价值
- 展示：期望进球数大字 + 各选项概率条 + Edge
- 单关状态：读 `poolList.ttg.single`

#### 2.2.3 半全场推荐页 (`/htft`) — 新建
- 对每场：用现有 `htft.py` 预测 9 种组合概率
- 对比 sporttery.cn `hafu` 赔率
- 展示：Top3 组合 + 概率条 + Edge
- 说明半场/全场分别是什么意思
- 单关状态：读 `poolList.hafu.single`

#### 2.2.4 猜冠军/冠亚军页 (`/champion`) — 新建
- 展示 32 支队伍赔率列表（来自 `冠军` / `冠亚军` poolCode）
- ELO 排名作为实力参考叠加到赔率上
- 价值分析：ELO 排名 vs 赔率倒算隐含概率，找出被高估/低估的队伍
- 提示：冠军/冠亚军在决赛前持续售卖，开售后随时可买

### 2.3 现有页面改造

#### Dashboard (`/`)
- 今日全部比赛列表
- 每场比赛：胜平负/让球/比分/总进球/半全场 — 各自"价值最高"的选项
- 点击进入对应玩法详情页
- 去掉现有的"泊松比分预测"独立大区块（已迁移到 /score）

#### MatchDetail (`/matches/:id`)
- 保留，作为单场比赛详情
- 该页面内嵌比分/总进球/半全场三个区块
- 赔率从 sporttery.cn 实时拉取

#### ParlayBuilder (`/parlay`)
- 现有逻辑保留
- **强制限制：最多选 6 场**，超出时 UI 禁用并提示

### 2.4 UI 通用组件

| 组件 | 职责 |
|---|---|
| `OddsCard` | 单个选项展示：赔率 + 概率条 + Edge 标签 |
| `ProbabilityBar` | 概率条：填充宽度对应概率，颜色区分 H/D/A 或大/小 |
| `ValueBadge` | Edge ≥ 5% 时显示绿色高亮标签 |
| `Guide` | 现有，保持不变 |
| `KellyCalculator` | 现有，保持不变 |
| `SportteryOddsTable` | 新增：从 sporttery.cn 拉的赔率表格，支持 crs/ttg/hafu |

---

## 三、后端接口改造

### 3.1 现有接口处置

| 接口 | 处置 |
|---|---|
| `GET /api/matches` | 保留，切换到 sporttery.cn 数据源 |
| `GET /api/matches/:id` | 保留，切换到 sporttery.cn |
| `GET /api/recommendations/today` | 改造：叠加 ELO vs 竞彩赔率的价值分析 |
| `GET /api/recommendations/poisson/:id` | 保留，计算逻辑不变 |
| `GET /api/recommendations/htft/:id` | 保留 |
| `GET /api/parlay/candidates` | 保留，数据源切换到 sporttery.cn |
| `GET /api/lotto/14场/recommendation` | 保留 |
| `GET /api/lotto/任选九/recommendation` | 保留 |
| `GET /api/slips` | 保留 |

### 3.2 新增接口

| 接口 | 说明 |
|---|---|
| `GET /api/football/crs?date=YYYY-MM-DD` | 比分赔率 + 单关状态 + 泊松 Top5 价值 |
| `GET /api/football/ttg?date=YYYY-MM-DD` | 总进球赔率 + 单关状态 + 泊松概率分布 |
| `GET /api/football/hafu?date=YYYY-MM-DD` | 半全场赔率 + 单关状态 + HTFT 概率 |
| `GET /api/football/today` | 今日全部比赛 5 个玩法的价值摘要 |
| `GET /api/football/champion` | 冠军赔率列表 + ELO 实力排名 |
| `GET /api/football/top2` | 冠亚军赔率列表 |
| `GET /api/sporttery/matches` | sporttery.cn 赛程拉取代理（解决跨域） |

### 3.3 数据模型

**同步策略：** 每日 11:00 前从 sporttery.cn 拉取当日赛程和赔率，入库 SQLite。后端分析模块继续用 SQLite 数据；前端展示层实时读库。

不实时轮询 sporttery.cn（避免高频请求），而是：
1. 启动时同步一次
2. 用户手动刷新时同步
3. 方案库中的方案记录赔率快照（购买时锁定）

---

## 四、混合过关 6 关限制

- 前端 `ParlayBuilder.tsx`：`selected.length >= 6` 时，禁止再选，UI 显示"最多6关"
- 后端 `/api/parlay/calculate`：超 6 关时返回错误 `"最多支持6关"`
- 说明：体彩官方规则，最少2关，最多6关

---

## 五、猜冠军 / 冠亚军

- 世界杯抽签后（约 2025年12月）才有名单和赔率
- **赛前（现在到抽签前）**：显示"冠军竞猜将在抽签后开启"
- **抽签后**：拉取 `poolCode=冠军` / `冠亚军`，展示 32 支队伍赔率
- ELO 排名叠加到赔率分析中，找出"被低估"的冠军候选

---

## 六、规格自检

- [ ] 占位符：无
- [ ] 内部一致性：前端路由 / 后端接口 / 数据流全部对齐
- [ ] 范围：可由单一实现计划覆盖
- [ ] 模糊性：无

---

## 七、实现顺序

1. **Phase 1（基础）**：后端 sporttery.cn 赛程拉取 + 入库
2. **Phase 2（接口）**：后端新增 crs/ttg/hafu/champion 四个分析接口
3. **Phase 3（前端基础）**：前端新增 OddsCard / ProbabilityBar / SportteryOddsTable 组件
4. **Phase 4（页面）**：比分推荐页 + 总进球推荐页 + 半全场推荐页
5. **Phase 5（Dashboard 改造）**：今日价值摘要，改掉 mock 数据
6. **Phase 6（混合过关）**：加 6 关限制
7. **Phase 7（冠军）**：猜冠军/冠亚军页，抽签后接入真实数据
