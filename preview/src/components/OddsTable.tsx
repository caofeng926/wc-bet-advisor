import type { OddApi } from "../lib/api";

interface Props { rows: OddApi[]; }

export default function OddsTable({ rows }: Props) {
  const bySelection: Record<string, OddApi[]> = {};
  rows.forEach((r) => {
    if (!bySelection[r.selection]) bySelection[r.selection] = [];
    bySelection[r.selection].push(r);
  });

  const selOrder = Object.keys(bySelection).sort((a, b) => {
    const aOdds = Math.min(...bySelection[a].map((r) => r.odds));
    const bOdds = Math.min(...bySelection[b].map((r) => r.odds));
    return aOdds - bOdds;
  });

  return (
    <div className="overflow-hidden rounded-lg border border-slate-800">
      <table className="w-full text-sm">
        <thead className="bg-slate-800/60 text-slate-300 text-xs">
          <tr>
            <th className="text-left px-3 py-2">选项</th>
            <th className="px-3 py-2">Pinnacle</th>
            <th className="px-3 py-2">Bet365</th>
            <th className="px-3 py-2">手工-A</th>
            <th className="px-3 py-2 text-emerald-300">代表盘口</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {selOrder.map((sel) => {
            const byBookie: Record<string, number | undefined> = {};
            bySelection[sel].forEach((r) => (byBookie[r.bookmaker] = r.odds));
            const min = Math.min(...bySelection[sel].map((r) => r.odds));
            const isBest = (b: string) => byBookie[b] === min;
            return (
              <tr key={sel} className="hover:bg-slate-800/30">
                <td className="px-3 py-2 font-medium text-slate-200">{sel}</td>
                {["Pinnacle", "Bet365", "手工-A"].map((b) => (
                  <td
                    key={b}
                    className={`px-3 py-2 text-center font-mono ${
                      isBest(b) ? "text-emerald-300 font-bold" : "text-slate-300"
                    }`}
                  >
                    {byBookie[b]?.toFixed(2) ?? "—"}
                  </td>
                ))}
                <td className="px-3 py-2 text-center font-mono text-emerald-300 font-bold">
                  {min.toFixed(2)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
