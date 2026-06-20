interface Props {
  value: number;       // 0~1 概率
  color?: string;      // Tailwind 颜色类，默认 bg-emerald-500
  showLabel?: boolean; // 是否显示百分比文字
}

export default function ProbabilityBar({ value, color = "bg-emerald-500", showLabel = true }: Props) {
  const pct = (Math.max(0, Math.min(1, value)) * 100).toFixed(0);
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-800 rounded overflow-hidden">
        <div
          className={`h-full ${color} transition-all duration-300`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showLabel && (
        <span className="w-10 text-right font-mono text-xs text-slate-300">{pct}%</span>
      )}
    </div>
  );
}