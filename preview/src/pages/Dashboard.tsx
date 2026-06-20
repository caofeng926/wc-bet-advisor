import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Trophy, Layers, Activity, RefreshCw, AlertCircle } from "lucide-react";
import MatchCard from "../components/MatchCard";
import TodayPicks from "../components/TodayPicks";
import Guide from "../components/Guide";
import RoiChart from "../components/RoiChart";

import { api, type MatchApi } from "../lib/api";
import { getTopPick } from "../mock/predictions";

export default function Dashboard() {
  const [matches, setMatches] = useState<MatchApi[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiUp, setApiUp] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        await api.health();
        if (mounted) setApiUp(true);
        const data = await api.listMatches({ limit: 20 });
        if (mounted) {
          const cutoff = Date.now() - 6 * 3600 * 1000;
          const horizon = Date.now() + 36 * 3600 * 1000;
          const today = data.filter((m) => {
            const t = new Date(m.kickoff_at).getTime();
            return t > cutoff && t < horizon;
          });
          setMatches(today);
          setLoading(false);
        }
      } catch (e) {
        if (mounted) {
          setError(e instanceof Error ? e.message : "API 连接失败");
          setApiUp(false);
          setLoading(false);
        }
      }
    })();
    return () => { mounted = false; };
  }, []);

  const recommendedCount = matches.filter((m) => getTopPick(m.id, m.home.elo, m.away.elo)).length;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">今日待购</h1>
          <p className="text-sm text-slate-400 mt-1">
            {loading ? "加载中..." : `共 ${matches.length} 场 · 推荐 ${recommendedCount} 场`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Guide items={[
            { term: "ELO", def: "球队实力评分。差值越大，强队优势越明显。差100=强队胜率约60%。" },
            { term: "Edge (价值)", def: "模型认为的胜率 × 赔率 − 1。edge>5%才进推荐池，表示有数学优势。" },
            { term: "Kelly", def: "凯利公式推荐的投注比例。1/4凯利=保守模式，单注最多押本金的5%。" },
            { term: "串关", def: "多场比赛绑在一起，全对才算赢。赔率相乘，收益高但难度也高。" },
          ]} />
          {apiUp !== null && (
            <span className={`text-xs px-2 py-1 rounded flex items-center gap-1 ${
              apiUp ? "bg-emerald-900/30 text-emerald-300 border border-emerald-800/50"
                    : "bg-red-900/30 text-red-300 border border-red-800/50"
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${apiUp ? "bg-emerald-400" : "bg-red-400"}`} />
              {apiUp ? "API 在线" : "API 离线"}
            </span>
          )}
          <button
            onClick={() => window.location.reload()}
            className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 px-2 py-1 rounded hover:bg-slate-800"
          >
            <RefreshCw className="w-3 h-3" /> 刷新
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-800/50 bg-red-900/20 p-4 flex gap-2 text-sm text-red-200">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <div>
            <div className="font-medium">无法连接后端 API</div>
            <div className="text-red-300/80 text-xs mt-1">请确认后端在 <code className="bg-red-900/40 px-1 rounded">http://localhost:8000</code> 运行。{error}</div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <div className="flex items-center justify-between">
            <div className="text-xs text-slate-400">推荐中</div>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-300 mt-1">{recommendedCount}</div>
          <div className="text-xs text-slate-500 mt-1">edge ≥ 5% 的场次</div>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <div className="flex items-center justify-between">
            <div className="text-xs text-slate-400">14场推荐</div>
            <Trophy className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-300 mt-1">1 + 6</div>
          <div className="text-xs text-slate-500 mt-1">主推 1 注 + 复式 6 注</div>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <div className="flex items-center justify-between">
            <div className="text-xs text-slate-400">本月 ROI</div>
            <Layers className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-300 mt-1">+13.5%</div>
          <div className="text-xs text-slate-500 mt-1">基于 2018/2022 回测</div>
        </div>
      </div>

      <TodayPicks />

      <div>
        <div className="flex items-center justify-between mb-3">

          <h2 className="text-lg font-bold text-slate-200">推荐清单</h2>
          <div className="flex items-center gap-3">
            <Link to="/lotto14" className="text-xs text-amber-400 hover:underline">14场胜负彩 →</Link>
            <Link to="/parlay" className="text-xs text-emerald-400 hover:underline">去构造串关 →</Link>
          </div>
        </div>
        {loading ? (
          <div className="text-sm text-slate-500 text-center py-12">从后端拉取中...</div>
        ) : matches.length === 0 ? (
          <div className="text-sm text-slate-500 text-center py-12 border border-dashed border-slate-800 rounded">
            今日 36h 内无比赛
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {matches.map((m) => {
              const pick = getTopPick(m.id, m.home.elo, m.away.elo);
              return <MatchCard key={m.id} match={m} pick={pick} />;
            })}
          </div>
        )}
      </div>

      <RoiChart />
    </div>
  );
}
