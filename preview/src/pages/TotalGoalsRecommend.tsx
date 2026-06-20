import { useEffect, useState } from "react";
import OddsCard from "../components/OddsCard";
import Guide from "../components/Guide";
import TeamFlag from "../components/TeamFlag";

interface TtgItem {
  goals: string;
  p_poisson: number;
  odds: number;
  edge: number;
}

interface TtgRecommend {
  match_id: number;
  home: string;
  away: string;
  kickoff_at: string;
  lambda_total: number;
  goals: TtgItem[];
  best_bet: string | null;
  best_edge: number;
  single: number;
}

export default function TotalGoalsRecommend() {
  const [data, setData] = useState<TtgRecommend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/football/ttg")
      .then((r) => { if (!r.ok) throw new Error(`网络错误 状态码 ${r.status}`); return r.json(); })
      .then((d: TtgRecommend[]) => { setData(d); setLoading(false); })
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return <div className="text-slate-400 text-sm py-12 text-center">加载中...</div>;
  if (error) return <div className="text-red-300 text-sm py-8 text-center">加载失败：{error}</div>;

  if (data.length === 0) {
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
        <div className="text-slate-500 text-sm text-center py-12 border border-dashed border-slate-800 rounded">
          今日暂无总进球数据
        </div>
      </div>
    );
  }

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

      {data.map((m) => {
        const over25Prob = m.goals
          .filter((g) => parseInt(g.goals) >= 3)
          .reduce((sum, g) => sum + g.p_poisson, 0);
        return (
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
              <div className="text-right">
                <div className="text-2xl font-bold text-amber-300 font-mono">{m.lambda_total.toFixed(2)}</div>
                <div className="text-xs text-slate-500">λ期望进球</div>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-2">
              {m.goals.slice(0, 8).map((g) => {
                const isOver = parseInt(g.goals) >= 3;
                return (
                  <OddsCard
                    key={g.goals}
                    label={`${g.goals}球${isOver ? "大" : "小"}`}
                    odds={g.odds}
                    prob={g.p_poisson}
                    edge={g.edge}
                    single={Boolean(m.single)}
                  />
                );
              })}
            </div>
            <div className="mt-2 text-xs text-slate-500">
              大2.5概率：<span className="text-amber-300 font-mono">{(over25Prob * 100).toFixed(0)}%</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}