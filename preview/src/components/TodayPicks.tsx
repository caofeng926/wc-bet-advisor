import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Target, TrendingUp, Timer, Trophy, AlertCircle, WifiOff } from "lucide-react";
import { api, type FootballTodayOut, type FootballTodayMatch } from "../lib/api";
import ValueBadge from "./ValueBadge";
import ProbabilityBar from "./ProbabilityBar";

const marketMeta: Record<string, { icon: any; href: string; label: string; tone: string }> = {
  crs:  { icon: Target,     href: "/score", label: "比分",     tone: "text-rose-300" },
  ttg:  { icon: TrendingUp, href: "/total", label: "总进球",   tone: "text-blue-300" },
  hafu: { icon: Timer,      href: "/htft",  label: "半全场",   tone: "text-violet-300" },
};

function BestChip({ best }: { best: FootballTodayMatch["best_crs"] }) {
  if (!best) {
    return <span className="text-xs text-slate-500">无数据</span>;
  }
  const meta = marketMeta[best.market] || marketMeta.crs;
  const Icon = meta.icon;
  return (
    <div className="rounded-md border border-slate-800 bg-slate-900/40 p-2.5 min-w-0">
      <div className="flex items-center justify-between gap-1.5 text-[10px] text-slate-500 uppercase tracking-wider mb-1.5">
        <span className={`flex items-center gap-1 ${meta.tone}`}>
          <Icon className="w-3 h-3" />
          {meta.label}
        </span>
        {best.single === 1 && (
          <span className="text-[9px] bg-emerald-900/40 text-emerald-300 px-1 rounded">单关</span>
        )}
      </div>
      <div className="text-sm font-medium text-slate-100 truncate">{best.label}</div>
      <div className="flex items-baseline justify-between gap-2 mt-1">
        <span className="font-mono text-emerald-300 text-sm font-bold">@{best.odds.toFixed(2)}</span>
        <ValueBadge edge={best.edge} size="sm" />
      </div>
      <div className="mt-1.5">
        <ProbabilityBar value={best.p_model} color="bg-emerald-500" showLabel={true} />
      </div>
    </div>
  );
}

export default function TodayPicks() {
  const [data, setData] = useState<FootballTodayOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const today = await api.getFootballToday();
        if (mounted) { setData(today); setLoading(false); }
      } catch (e) {
        if (mounted) {
          setError(e instanceof Error ? e.message : "请求失败");
          setLoading(false);
        }
      }
    })();
    return () => { mounted = false; };
  }, []);

  if (loading) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-6 text-sm text-slate-500 text-center">
        正在拉取今日体彩 5 玩法推荐...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-800/50 bg-red-900/20 p-4 flex gap-2 text-sm text-red-200">
        <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
        <div>5 玩法推荐接口异常:{error}</div>
      </div>
    );
  }

  if (!data || data.source === "offline" || data.matches.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-6">
        <div className="flex items-center gap-2 text-slate-300 text-sm font-medium mb-1">
          <WifiOff className="w-4 h-4 text-slate-500" />
          今日 5 玩法推荐(等待体彩开盘)
        </div>
        <div className="text-xs text-slate-500 leading-relaxed">
          {data?.date
            ? `${data.date} 暂无可用赛事。`
            : "今日暂无可用赛事。"}
          体彩通常在赛日前 1-3 天开盘，届时比分/总进球/半全场页会自动出现推荐。
          <Link to="/champion" className="text-amber-400 hover:underline ml-1">猜冠军 →</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Trophy className="w-4 h-4 text-amber-400" />
          <h2 className="text-lg font-bold text-slate-200">今日 5 玩法速览</h2>
          <span className="text-xs text-slate-500">({data.matches.length} 场 · {data.date})</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <Link to="/score" className="hover:text-rose-300">比分 →</Link>
          <Link to="/total" className="hover:text-blue-300">总进球 →</Link>
          <Link to="/htft" className="hover:text-violet-300">半全场 →</Link>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {data.matches.map((m) => (
          <div
            key={m.match_id}
            className="rounded-lg border border-slate-800 bg-slate-900/40 p-3"
          >
            <div className="flex items-center justify-between mb-2.5">
              <div className="flex items-center gap-2 min-w-0">
                <span className="text-sm text-slate-100 font-medium truncate">{m.home}</span>
                <span className="text-xs text-slate-600">vs</span>
                <span className="text-sm text-slate-100 font-medium truncate">{m.away}</span>
              </div>
              <span className="text-[10px] text-slate-500 font-mono shrink-0 ml-2">
                {m.kickoff_at.replace("T", " ")}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <BestChip best={m.best_crs} />
              <BestChip best={m.best_ttg} />
              <BestChip best={m.best_hafu} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
