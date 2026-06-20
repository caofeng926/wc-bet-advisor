import ProbabilityBar from "./ProbabilityBar";
import ValueBadge from "./ValueBadge";

interface Props {
  label: string;       // 选项名，如 "1:0"、"大2.5球"
  odds: number;        // 赔率
  prob: number;        // 模型概率 0~1
  edge: number;        // Edge 值
  single?: boolean;    // 是否支持单关
}

const COLOR_MAP: Record<string, string> = {
  H: "bg-emerald-500", D: "bg-amber-500", A: "bg-blue-500",
  over: "bg-emerald-500", under: "bg-red-500",
};

export default function OddsCard({ label, odds, prob, edge, single }: Props) {
  const color = COLOR_MAP[label] || "bg-slate-500";
  return (
    <div className="rounded border border-slate-700 bg-slate-900/40 p-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-slate-200">{label}</span>
        <div className="flex items-center gap-2">
          {single !== undefined && (
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded ${
                single ? "bg-emerald-900 text-emerald-300" : "bg-slate-700 text-slate-400"
              }`}
            >
              {single ? "单关" : "过关"}
            </span>
          )}
          <ValueBadge edge={edge} />
        </div>
      </div>
      <div className="text-2xl font-bold font-mono text-white mb-2">
        @{odds.toFixed(2)}
      </div>
      <ProbabilityBar value={prob} color={color} />
    </div>
  );
}