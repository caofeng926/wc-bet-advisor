import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface Props {
  edge: number;
  size?: "sm" | "md";
}

export default function ValueBadge({ edge, size = "sm" }: Props) {
  const pct = (edge * 100).toFixed(0);
  const isPositive = edge > 0.05;
  const isNeutral = edge >= 0 && edge <= 0.05;
  const isNegative = edge < 0;

  const color = isPositive
    ? "bg-emerald-500/15 text-emerald-300 border-emerald-700/40"
    : isNeutral
    ? "bg-slate-700/40 text-slate-300 border-slate-600"
    : "bg-red-500/15 text-red-300 border-red-700/40";

  const Icon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus;
  const sizeClass = size === "sm" ? "text-xs px-1.5 py-0.5" : "text-sm px-2 py-1";

  return (
    <span className={`inline-flex items-center gap-1 border rounded font-mono ${color} ${sizeClass}`}>
      <Icon className="w-3 h-3" />
      {isPositive ? "+" : ""}
      {pct}%
    </span>
  );
}
