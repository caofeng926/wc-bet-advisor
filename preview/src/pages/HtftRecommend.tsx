import { useEffect, useState } from "react";
import OddsCard from "../components/OddsCard";
import Guide from "../components/Guide";
import TeamFlag from "../components/TeamFlag";

interface HafuItem {
  outcome: string;
  label: string;
  p_htft: number;
  odds: number;
  edge: number;
}

interface HafuRecommend {
  match_id: number;
  home: string;
  away: string;
  kickoff_at: string;
  top3: HafuItem[];
  best_bet: string | null;
  best_edge: number;
  single: number;
  outcomes: HafuItem[];
}

export default function HtftRecommend() {
  const [data, setData] = useState<HafuRecommend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/football/hafu")
      .then((r) => { if (!r.ok) throw new Error(`网络错误 状态码 ${r.status}`); return r.json(); })
      .then((d: HafuRecommend[]) => { setData(d); setLoading(false); })
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return <div className="text-slate-400 text-sm py-12 text-center">加载中...</div>;
  if (error) return <div className="text-red-300 text-sm py-8 text-center">加载失败：{error}</div>;

  if (data.length === 0) {
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
        <div className="text-slate-500 text-sm text-center py-12 border border-dashed border-slate-800 rounded">
          今日暂无半全场数据
        </div>
      </div>
    );
  }

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
              <TeamFlag iso3={m.home.substring(0, 3)} name_zh={m.home} size="sm" />
              <div>
                <span className="text-slate-200 text-sm font-medium">{m.home}</span>
                <span className="text-slate-600 mx-2">vs</span>
                <span className="text-slate-200 text-sm font-medium">{m.away}</span>
              </div>
              <span className="text-slate-500 text-xs">{m.kickoff_at}</span>
            </div>
            {m.single === 1 && (
              <span className="text-[10px] bg-emerald-900 text-emerald-300 px-1.5 py-0.5 rounded">单关</span>
            )}
          </div>
          <div className="grid grid-cols-3 gap-2">
            {m.top3.map((h) => (
              <OddsCard
                key={h.outcome}
                label={h.label}
                odds={h.odds}
                prob={h.p_htft}
                edge={h.edge}
              />
            ))}
          </div>
          {m.best_bet && (
            <div className="mt-2 text-xs text-emerald-400">
              最佳: {m.outcomes.find(o => o.outcome === m.best_bet)?.label ?? m.best_bet} · Edge {(m.best_edge * 100).toFixed(0)}%
            </div>
          )}
        </div>
      ))}
    </div>
  );
}