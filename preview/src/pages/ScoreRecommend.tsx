import { useEffect, useState } from "react";
import OddsCard from "../components/OddsCard";
import Guide from "../components/Guide";
import TeamFlag from "../components/TeamFlag";

interface CrsItem {
  score: string;
  p_poisson: number;
  odds: number;
  edge: number;
}

interface CrsRecommend {
  match_id: number;
  home: string;
  away: string;
  kickoff_at: string;
  top_scores: CrsItem[];
  best_bet: string | null;
  best_edge: number;
  single: number;
}

export default function ScoreRecommend() {
  const [data, setData] = useState<CrsRecommend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/football/crs")
      .then((r) => {
        if (!r.ok) throw new Error(`网络错误 状态码 ${r.status}`);
        return r.json();
      })
      .then((d: CrsRecommend[]) => {
        setData(d);
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="text-slate-400 text-sm py-12 text-center">加载中...</div>;
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-800/50 bg-red-900/20 p-6 max-w-lg">
        <div className="text-red-300 text-sm">
          加载失败：{error}（后端可能未运行）
        </div>
      </div>
    );
  }

  if (data.length === 0) {
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
        <div className="text-slate-500 text-sm text-center py-12 border border-dashed border-slate-800 rounded">
          今日暂无比分数据（请确认后端已启动且 sporttery.cn API 可用）
        </div>
      </div>
    );
  }

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
              <TeamFlag iso3={m.home.substring(0, 3)} name_zh={m.home} size="sm" />
              <div>
                <span className="text-slate-200 text-sm font-medium">{m.home}</span>
                <span className="text-slate-600 mx-2">vs</span>
                <span className="text-slate-200 text-sm font-medium">{m.away}</span>
              </div>
              <span className="text-slate-500 text-xs">{m.kickoff_at}</span>
            </div>
            <div className="flex items-center gap-2">
              {m.single === 1 && (
                <span className="text-[10px] bg-emerald-900 text-emerald-300 px-1.5 py-0.5 rounded">
                  单关
                </span>
              )}
              {m.best_bet && (
                <span className="text-xs text-emerald-400 font-mono">
                  最佳: {m.best_bet} ({(m.best_edge * 100).toFixed(0)}% edge)
                </span>
              )}
            </div>
          </div>
          <div className="grid grid-cols-5 gap-2">
            {m.top_scores.slice(0, 5).map((s) => (
              <OddsCard
                key={s.score}
                label={s.score}
                odds={s.odds}
                prob={s.p_poisson}
                edge={s.edge}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}