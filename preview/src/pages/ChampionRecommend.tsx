import { useEffect, useState } from "react";
import Guide from "../components/Guide";

interface ChampionItem {
  team: string;
  odds: number;
  elo_rank: number;
  edge: number;
  p_elo: number;
  implied: number;
}

interface ChampionRecommend {
  pool_code: string;
  items: ChampionItem[];
  fetched_at: string;
}

export default function ChampionRecommend() {
  const [champion, setChampion] = useState<ChampionRecommend | null>(null);
  const [top2, setTop2] = useState<ChampionRecommend | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pool, setPool] = useState<"冠军" | "冠亚军">("冠军");

  useEffect(() => {
    Promise.all([
      fetch("/api/football/champion?pool=冠军").then((r) => { if (!r.ok) throw new Error("网络错误 状态码 " + r.status); return r.json(); }),
      fetch("/api/football/champion?pool=冠亚军").then((r) => { if (!r.ok) throw new Error("网络错误 状态码 " + r.status); return r.json(); }),
    ])
      .then(([c, t]) => {
        setChampion(c);
        setTop2(t);
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
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">猜冠军 / 猜冠亚军</h1>
        <div className="rounded border border-red-800/50 bg-red-900/20 p-4 text-red-300 text-sm">
          加载失败：{error}（后端可能未运行）
        </div>
      </div>
    );
  }

  const current = pool === "冠军" ? champion : top2;
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
        <button
          onClick={() => setPool("冠军")}
          className={`px-4 py-2 rounded text-sm font-medium ${
            pool === "冠军" ? "bg-emerald-600 text-white" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
          }`}
        >
          猜冠军
        </button>
        <button
          onClick={() => setPool("冠亚军")}
          className={`px-4 py-2 rounded text-sm font-medium ${
            pool === "冠亚军" ? "bg-emerald-600 text-white" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
          }`}
        >
          猜冠亚军
        </button>
      </div>

      {items.length === 0 ? (
        <div className="rounded border border-amber-800/50 bg-amber-900/20 p-6 text-center">
          <div className="text-amber-300 text-sm font-medium mb-1">
            ⚠️ {pool} 暂未开售
          </div>
          <div className="text-slate-400 text-xs">
            {pool === "冠军"
              ? "猜冠军将在世界杯抽签后（预计2025年12月）开启，届时可购买。"
              : "猜冠亚军将在世界杯抽签后（预计2025年12月）开启，届时可购买。"}
          </div>
        </div>
      ) : (
        <>
          <div className="text-xs text-slate-500 mb-2">
            共 {items.length} 支队伍 · 数据更新时间：{current?.fetched_at || "-"}
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/40 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-800/60 text-slate-300 text-xs">
                <tr>
                  <th className="text-left px-3 py-2 w-8">#</th>
                  <th className="text-left px-3 py-2">球队</th>
                  <th className="px-3 py-2 text-center">ELO排名</th>
                  <th className="px-3 py-2 text-right">赔率</th>
                  <th className="px-3 py-2 text-right">隐含概率</th>
                  <th className="px-3 py-2 text-right">Edge(价值)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {items.map((item, i) => (
                  <tr key={item.team} className="hover:bg-slate-800/30">
                    <td className="px-3 py-2 text-slate-500 font-mono">{i + 1}</td>
                    <td className="px-3 py-2">
                      <span className="text-slate-200 font-medium">{item.team}</span>
                    </td>
                    <td className="px-3 py-2 text-center">
                      <span className="font-mono text-slate-400">#{item.elo_rank}</span>
                    </td>
                    <td className="px-3 py-2 text-right">
                      <span className="font-mono text-emerald-300 font-bold">@{item.odds.toFixed(2)}</span>
                    </td>
                    <td className="px-3 py-2 text-right">
                      <span className="font-mono text-slate-300">{(item.implied * 100).toFixed(1)}%</span>
                    </td>
                    <td className="px-3 py-2 text-right">
                      <span
                        className={`font-mono font-bold ${
                          item.edge > 0 ? "text-emerald-300" : "text-red-300"
                        }`}
                      >
                        {item.edge > 0 ? "+" : ""}{(item.edge * 100).toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}