# WC-Bet-Advisor · 2026 世界杯体彩竞猜购彩建议程序

> 单用户本地部署的桌面 Web 应用 · 预测 + 推荐 + 复盘 · 三源数据融合 (ELO 概率模型 + 体彩官方赔率 + Polymarket)

## 项目结构

```
.
├── backend/                # 后端 (FastAPI + SQLAlchemy + SQLite)
├── preview/                # 前端 (React + Vite + Tailwind + TypeScript)
├── docs/                   # 设计/需求文档
├── deploy/                 # 一键部署到 VPS (deploy.bat + init.sh)
├── docker-compose.yml      # 本地 Docker Compose
└── README.md
```

## 功能

- **胜平负 / 让球** — ELO + 让球后胜率 → Edge > 5% 进推荐池 + Kelly 注资
- **比分推荐** (`/score`) — 泊松 Top5 + 体彩 crs 31 项 → 最优 Edge
- **总进球推荐** (`/total`) — 泊松进球分布 vs 体彩 0~7+ 球
- **半全场推荐** (`/htft`) — 两段泊松 HT × FT 9 组合 vs 体彩 hafu
- **猜冠军 / 冠亚军** (`/champion`) — Plackett-Luce 48 强 vs 体彩官方 (含 ELO 兜底)
- **14 场胜负彩 / 任选九** — 主推 1 注 + 复式 6 注，回测 ROI +13.5%
- **混合过关** — 最多 6 场，自动算组合赔率 / Edge / 相关性折扣 / Kelly 建议
- **方案库 / 复盘** — 记录方案 → 结算 → P&L 汇总

## 快速启动 (本地, 无 Docker)

两个终端:

```bash
# 终端 1: 后端
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
python -m app.services.seed           # 一次性导入 16 场 mock
.venv\Scripts\python -m uvicorn app.main:app --port 8000

# 终端 2: 前端
cd preview
npm install
npm run dev    # → http://localhost:5173
```

## Docker Compose

```bash
docker compose up --build
```

- 后端: http://localhost:8000 (docs at /docs)
- 前端: http://localhost:5173

## 部署到 VPS

参见 `deploy/README.md`, 一行 `deploy\deploy.bat` 即可。

## 数据来源

- **赛程 + 球队 + 初始赔率**: 后端 `app/services/seed.py` mock (2022 真实分组 + 16 场示例)
- **体彩官方赔率**: `app/services/sporttery.py` 调 sporttery.cn JSON API (需本地有 HTTP 代理可达)
- **Polymarket**: `app/services/polymarket.py` 调 gamma-api.polymarket.com
- **冠军赔率兜底**: 本地 ELO → Plackett-Luce 概率 → 8% 抽水 → 反推赔率

体彩 API 不可达时自动降级: Champion 走 ELO 兜底, 其余玩法返回 `source=offline` 友好提示。

## 测试

```bash
cd backend
.venv\Scripts\python.exe -m pytest tests/ -v
```

## 文档

- `docs/PRD.md` — 需求文档
- `docs/DESIGN.md` — 详细设计
- `docs/superpowers/plans/` — 实施计划
