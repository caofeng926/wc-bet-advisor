import { useState } from "react";
import { HelpCircle, X } from "lucide-react";

interface GuideItem {
  term: string;
  def: string;
}

interface Props {
  items: GuideItem[];
  title?: string;
}

/** 可点击展开的术语说明组件 */
export default function Guide({ items, title = "术语说明" }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 transition"
      >
        <HelpCircle className="w-3.5 h-3.5" />
        {title}
      </button>
      {open && (
        <div className="absolute top-full left-0 mt-2 z-50 w-72 rounded-lg border border-slate-700 bg-slate-900 p-4 shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-300">{title}</span>
            <button onClick={() => setOpen(false)} className="text-slate-500 hover:text-slate-300">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="space-y-3">
            {items.map((it) => (
              <div key={it.term} className="text-xs">
                <div className="text-emerald-300 font-medium mb-0.5">{it.term}</div>
                <div className="text-slate-400 leading-relaxed">{it.def}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/** 固定显示的关键指标说明条（不折叠）*/
export function MetricBar({ items }: Props) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/30 p-3 space-y-2">
      <div className="text-xs font-bold text-slate-300 mb-2">📊 指标说明</div>
      {items.map((it) => (
        <div key={it.term} className="flex items-start gap-2 text-xs">
          <span className="text-emerald-300 font-medium shrink-0 min-w-[60px]">{it.term}</span>
          <span className="text-slate-400 leading-relaxed">{it.def}</span>
        </div>
      ))}
    </div>
  );
}