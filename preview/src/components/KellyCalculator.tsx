import { useState } from "react";
import { suggestStake } from "../lib/kelly";
import { Calculator } from "lucide-react";

interface Props { defaultOdds?: number; defaultP?: number; }

export default function KellyCalculator({ defaultOdds = 1.85, defaultP = 0.56 }: Props) {
  const [bankroll, setBankroll] = useState(1000);
  const [odds, setOdds] = useState(defaultOdds);
  const [p, setP] = useState(defaultP);
  const [kf, setKf] = useState(0.25);

  const r = suggestStake(bankroll, p, odds, kf);

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-5">
      <div className="flex items-center gap-2 mb-4">
        <Calculator className="w-4 h-4 text-emerald-400" />
        <h3 className="text-sm font-bold text-slate-200">凯利试算</h3>
      </div>
      <div className="grid grid-cols-4 gap-3 mb-4">
        <div>
          <label className="text-xs text-slate-400">本金(¥)</label>
          <input
            type="number"
            value={bankroll}
            onChange={(e) => setBankroll(+e.target.value || 0)}
            className="w-full mt-1 bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm font-mono"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400">赔率</label>
          <input
            type="number"
            step="0.01"
            value={odds}
            onChange={(e) => setOdds(+e.target.value || 0)}
            className="w-full mt-1 bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm font-mono"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400">模型概率</label>
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={p}
            onChange={(e) => setP(Math.min(1, Math.max(0, +e.target.value || 0)))}
            className="w-full mt-1 bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm font-mono"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400">凯利系数</label>
          <select
            value={kf}
            onChange={(e) => setKf(+e.target.value)}
            className="w-full mt-1 bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm font-mono"
          >
            <option value="0.1">0.1(保守)</option>
            <option value="0.25">0.25(默认)</option>
            <option value="0.5">0.5(半凯利)</option>
            <option value="1.0">1.0(全凯利)</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-3 pt-3 border-t border-slate-800">
        <div>
          <div className="text-xs text-slate-400">建议注金</div>
          <div className="text-lg font-bold text-emerald-300 font-mono">¥{r.stake}</div>
        </div>
        <div>
          <div className="text-xs text-slate-400">命中盈利</div>
          <div className="text-lg font-bold text-emerald-300 font-mono">+¥{r.winProfit}</div>
        </div>
        <div>
          <div className="text-xs text-slate-400">未中亏损</div>
          <div className="text-lg font-bold text-red-300 font-mono">¥{r.loseLoss}</div>
        </div>
        <div>
          <div className="text-xs text-slate-400">EV(单次期望)</div>
          <div className={`text-lg font-bold font-mono ${r.ev >= 0 ? "text-emerald-300" : "text-red-300"}`}>
            {r.ev >= 0 ? "+" : ""}¥{r.ev}
          </div>
        </div>
      </div>
      <div className="mt-3 text-[11px] text-slate-500 leading-relaxed">
        💡 <strong className="text-slate-400">凯利公式：</strong>f* = (b×p − q) / b ·
        其中 b=赔率−1，p=模型概率，q=1−p。
        实际取 {kf} 凯利（保守模式）+5% 单注封顶。
        长期按此下注，数学上可最大化对数财富，但短期会有回撤。
      </div>
    </div>
  );
}
