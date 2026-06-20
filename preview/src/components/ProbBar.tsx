interface Item { label: string; value: number; color: string; }
interface Props { items: Item[]; }

export default function ProbBar({ items }: Props) {
  const max = Math.max(...items.map((i) => i.value), 0.01);
  return (
    <div className="space-y-1.5">
      {items.map((it) => (
        <div key={it.label} className="flex items-center gap-2 text-xs">
          <span className="w-12 text-slate-400">{it.label}</span>
          <div className="flex-1 bg-slate-800 rounded h-2 overflow-hidden">
            <div
              className={`h-full ${it.color} transition-all`}
              style={{ width: `${(it.value / max) * 100}%` }}
            />
          </div>
          <span className="w-12 text-right font-mono text-slate-300">
            {(it.value * 100).toFixed(0)}%
          </span>
        </div>
      ))}
    </div>
  );
}
