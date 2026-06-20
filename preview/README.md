# WC-Bet-Advisor · 预览版

> 2026 世界杯体彩竞猜购彩建议程序 — 1 天可交付的可点击 demo

## 这是什么

一个**纯前端**的桌面 Web 端原型,用 2022 世界杯真实比赛数据做 mock,演示完整产品的核心交互:

- 顶部**倒计时雷达** (3 色状态:绿/黄/红)
- **Dashboard** 今日待购 + 推荐清单 + 30 日收益曲线
- **MatchDetail** 单场:赔率对比 / 价值分析(三源融合) / 凯利试算
- **14 场胜负彩** 一键生成主推 + 6 注复式
- **混合过关** 串关构造器 + 相关性矩阵
- 12 支国家队**真实国旗**(flagcdn.com 公开 CDN)
- 自制 **2026 世界杯 logo** (SVG 矢量,无版权风险)

## 启动

```bash
cd preview
npm install   # 已装,可不跑
npm run dev
```

打开 <http://localhost:5173> 即可。

> 注意:不要被 5174 干扰,5173 是新版默认。如果端口被占 Vite 会自动顺延。

## 文件结构

```
preview/
├── public/
│   └── wc26-logo.svg          # 自制 2026 WC logo
├── src/
│   ├── main.tsx               # 入口 + Router
│   ├── App.tsx                # 4 个路由
│   ├── index.css              # Tailwind + 全局样式
│   ├── components/
│   │   ├── Layout.tsx         # 顶栏 + 侧栏 + 倒计时 + footer
│   │   ├── CountdownBanner.tsx
│   │   ├── MatchCard.tsx
│   │   ├── OddsTable.tsx
│   │   ├── ValueBadge.tsx
│   │   ├── ProbBar.tsx
│   │   ├── KellyCalculator.tsx
│   │   ├── RoiChart.tsx
│   │   └── TeamFlag.tsx
│   ├── lib/
│   │   ├── time.ts            # 倒计时格式化
│   │   ├── kelly.ts           # 凯利公式 + 试算
│   │   └── flags.ts           # ISO3 → flagcdn URL
│   ├── mock/                  # 6 场 mock 数据(2022 真实)
│   │   ├── matches.ts
│   │   ├── odds.ts
│   │   ├── polymarket.ts
│   │   ├── predictions.ts
│   │   └── lotto14.ts
│   └── pages/
│       ├── Dashboard.tsx
│       ├── MatchDetail.tsx
│       ├── Lotto14.tsx
│       └── ParlayBuilder.tsx
└── package.json
```

## 6 场 mock 比赛

| # | 对阵 | 用途 |
|---|---|---|
| 1 | 🇧🇷 巴西 vs 🇭🇷 克罗地亚 | Dashboard 主推 / 让球价值 |
| 2 | 🇪🇸 西班牙 vs 🇨🇷 哥斯达黎加 | 让 2 球价值识别 + Polymarket |
| 3 | 🇦🇷 阿根廷 vs 🇸🇦 沙特 | **已结束**(模型也会错的案例) |
| 4 | 🇲🇦 摩洛哥 vs 🇵🇹 葡萄牙 | 串关主推 / Polymarket |
| 5 | 🇫🇷 法国 vs 🇩🇰 丹麦 | 强队胜常规 |
| 6 | 🇩🇪 德国 vs 🇯🇵 日本 | 冷门高赔风险案例 |

所有 ELO 排名、赔率、概率都贴近真实盘口(2022 实际值改写)。

## 技术栈

| 层 | 选型 |
|---|---|
| 框架 | React 18 + TypeScript 5 |
| 构建 | Vite 5 |
| 样式 | TailwindCSS 3(深色主题) |
| 路由 | React Router 6 |
| 图标 | lucide-react |
| 状态 | useState + props(无全局状态) |

## 验收清单

- [x] 4 个页面 (`/`, `/matches/:id`, `/lotto14`, `/parlay`) 全部可访问
- [x] 倒计时每秒变化,3 色规则正确
- [x] 12 个国家国旗正确显示
- [x] 自制 2026 WC logo 在顶栏
- [x] MatchDetail 凯利试算实时计算
- [x] 14 场一键生成 1+6 注
- [x] 串关构造器累计 + 相关性惩罚
- [x] 1280px 宽度下布局正常
- [x] `npm run build` 零错误
- [x] Console 无报错

## 局限(已知,正式版会解决)

- ❌ 数据全部 mock,刷新不保留
- ❌ 推荐逻辑在客户端,正式版走后端 + Polymarket 实时
- ❌ 14 场搜索是贪心,正式版用 MCMC / 爬山
- ❌ 不支持保存方案 / 跟单记账(放 W3)
- ❌ 移动端不优化(< 1024px 不保证)
- ❌ 西班牙语 / 英语等多语种不做

## 进入正式版的入口

完整设计见 `../docs/DESIGN.md`,需求见 `../docs/PRD.md`。
