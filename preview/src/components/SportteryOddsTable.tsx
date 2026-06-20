import ProbabilityBar from "./ProbabilityBar";

interface CrsRow { score: string; p_poisson: number; odds: number; edge: number; }
interface TtgRow { goals: string; p_poisson: number; odds: number; edge: number; }
interface HafuRow { outcome: string; label: string; p_htft: number; odds: number; edge: number; }

type Row = CrsRow | TtgRow | HafuRow;

interface Props {
  type: "crs" | "ttg" | "hafu";
  rows: Row[];
  bestBet: string | null;
}

const HAFU_SHORT_LABELS: Record<string, string> = {
  hh: "胜-胜", hd: "胜-平", ha: "胜-负",
  dh: "平-胜", dd: "平-平", da: "平-负",
  ah: "负-胜", ad: "负-平", aa: "负-负",
};

export default function SportteryOddsTable({ type, rows, bestBet }: Props) {
  if (!rows || rows.length === 0) {
    return (
      <div className="text-slate-500 text-sm py-4 text-center">
        暂无赔率数据
      </div>
    );
  }

  return (
    <div className="rounded border border-slate-800 bg-slate-900/40 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-800/60 text-slate-300 text-xs">
          <tr>
            <th className="text-left px-3 py-2">选项</th>
            <th className="px-3 py-2 text-left">概率</th>
            <th className="px-3 py-2">赔率</th>
            <th className="px-3 py-2">Edge</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {rows.map((r, i) => {
            const key =
              type === "crs" ? (r as CrsRow).score
              : type === "ttg" ? (r as TtgRow).goals
              : (r as HafuRow).outcome;
            const prob = (r as CrsRow).p_poisson || (r as HafuRow).p_htft;
            const isBest = key === bestBet;
            const displayLabel = type === "hafu" ? HAFU_SHORT_LABELS[key] || key : key;

            return (
              <tr
                key={`${key}-${i}`}
                className={isBest ? "bg-emerald-900/20" : "hover:bg-slate-800/30"}
              >
                <td className="px-3 py-2">
                  <span className={`font-medium ${isBest ? "text-emerald-200" : "text-slate-200"}`}>
                    {displayLabel}
                  </span>
                </td>
                <td className="px-3 py-2">
                  <ProbabilityBar
                    value={prob}
                    color={isBest ? "bg-emerald-500" : "bg-slate-600"}
                  />
                </td>
                <td className="px-3 py-2 font-mono text-slate-200">
                  @{(r as CrsRow).odds.toFixed(2)}
                </td>
                <td className="px-3 py-2">
                  <span
                    className={`font-mono ${
                      (r as CrsRow).edge > 0 ? "text-emerald-300" : "text-red-300"
                    }`}
                  >
                    {(((r as CrsRow).edge) * 100).toFixed(0)}%
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}