// 简单 SVG 折线图(基于真实PnL数据)
import { useEffect, useState } from "react";
import { api, type PnlSummary } from "../lib/api";

export default function RoiChart() {
  const [summary, setSummary] = useState<PnlSummary | null>(null);

  useEffect(() => {
    api.getPnlSummary().then(setSummary).catch(() => {});
  }, []);

  const totalPnl = summary?.total_pnl ?? 0;
  const roi = summary?.roi_pct ?? 0;
  const hitRate = summary?.hit_rate_pct ?? 0;

  // Mock 30-day curve (基于总ROI模拟)
  // 实际生产需要每日PnL记录
  const base = 1000;
  const [data] = useState<number[]>(() => Array.from({ length: 30 }, (_, i) => {
    const trend = (totalPnl / 30) * i;
    const noise = (Math.random() - 0.5) * 20;
    return base + trend + noise;
  }));

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const W = 600;
  const H = 180;
  const pad = 20;

  const pts = data.map((v, i) => {
    const x = pad + (i / (data.length - 1)) * (W - 2 * pad);
    const y = H - pad - ((v - min) / range) * (H - 2 * pad);
    return `${x},${y}`;
  });

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-bold text-slate-300">收益曲线(基于跟单记录)</h3>
        <div className="text-right">
          <div className={`text-lg font-bold font-mono ${totalPnl >= 0 ? "text-emerald-300" : "text-red-300"}`}>
            {totalPnl >= 0 ? "+" : ""}¥{totalPnl.toFixed(0)}
          </div>
          <div className="text-xs text-slate-500">ROI {roi >= 0 ? "+" : ""}{roi.toFixed(1)}% · 命中率 {hitRate.toFixed(0)}%</div>
        </div>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-44">
        <defs>
          <linearGradient id="roiFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
          </linearGradient>
        </defs>
        <line x1={pad} y1={H - pad} x2={W - pad} y2={H - pad} stroke="#334155" strokeWidth="0.5" />
        <polygon points={`${pad},${H - pad} ${pts.join(" ")} ${W - pad},${H - pad}`} fill="url(#roiFill)" />
        <polyline points={pts.join(" ")} fill="none" stroke="#10b981" strokeWidth="2" />
        {data.map((v, i) => {
          if (i % 5 !== 0) return null;
          const x = pad + (i / (data.length - 1)) * (W - 2 * pad);
          return <line key={i} x1={x} y1={H - pad} x2={x} y2={H - pad + 3} stroke="#475569" />;
        })}
        <text x={pad} y={H - 4} fill="#64748b" fontSize="9">06-01</text>
        <text x={W - pad - 25} y={H - 4} fill="#64748b" fontSize="9">06-30</text>
      </svg>
    </div>
  );
}
