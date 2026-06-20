import { useEffect, useState } from "react";
import { Trash2, Check, X } from "lucide-react";
import { api, type SlipApi, type PnlSummary } from "../lib/api";
import { formatDateZh } from "../lib/time";

export default function Slips() {
  const [slips, setSlips] = useState<SlipApi[]>([]);
  const [summary, setSummary] = useState<PnlSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);

  // 简易录入表单
  const [newTitle, setNewTitle] = useState("");
  const [newKind, setNewKind] = useState("single");
  const [newStake, setNewStake] = useState(10);
  const [newOdds, setNewOdds] = useState(1.85);

  async function load() {
    setLoading(true);
    try {
      const [s, p] = await Promise.all([api.listSlips(), api.getPnlSummary()]);
      setSlips(s);
      setSummary(p);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { load(); }, []);

  async function add() {
    if (!newTitle) return;
    await api.createSlip({
      title: newTitle,
      kind: newKind,
      selections: [{ note: "手动录入", odds: newOdds }],
      total_odds: newOdds,
      stake: newStake,
      cost: newKind.startsWith("lotto") ? 2 : 0,
    });
    setNewTitle("");
    setShowAdd(false);
    load();
  }

  async function settle(id: number, result: "win" | "lose") {
    const slip = slips.find((s) => s.id === id);
    if (!slip) return;
    const payout = result === "win" ? slip.stake * slip.total_odds + slip.cost : 0;
    await api.settleSlip(id, result, payout);
    load();
  }

  async function del(id: number) {
    if (!confirm("确定删除此方案?")) return;
    await api.deleteSlip(id);
    load();
  }

  function resultColor(r: string) {
    if (r === "win") return "text-emerald-300";
    if (r === "lose") return "text-red-300";
    if (r === "void") return "text-slate-400";
    return "text-amber-300";
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">方案库</h1>
          <p className="text-sm text-slate-400 mt-1">跟单记录 + 复盘</p>
        </div>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-sm"
        >
          {showAdd ? "取消" : "+ 新建方案"}
        </button>
      </div>

      {summary && (
        <div className="grid grid-cols-4 gap-3">
          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
            <div className="text-xs text-slate-400">总投入</div>
            <div className="text-2xl font-bold text-white mt-1">¥{summary.total_stake.toFixed(0)}</div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
            <div className="text-xs text-slate-400">总回报</div>
            <div className="text-2xl font-bold text-white mt-1">¥{summary.total_payout.toFixed(0)}</div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
            <div className="text-xs text-slate-400">净收益</div>
            <div className={`text-2xl font-bold mt-1 ${summary.total_pnl >= 0 ? "text-emerald-300" : "text-red-300"}`}>
              {summary.total_pnl >= 0 ? "+" : ""}¥{summary.total_pnl.toFixed(0)}
            </div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
            <div className="text-xs text-slate-400">ROI / 命中率</div>
            <div className={`text-2xl font-bold mt-1 ${summary.roi_pct >= 0 ? "text-emerald-300" : "text-red-300"}`}>
              {summary.roi_pct >= 0 ? "+" : ""}{summary.roi_pct.toFixed(1)}%
            </div>
             <div className="text-xs text-slate-500 mt-1">命中 {summary.hit_rate_pct.toFixed(0)}%</div>
          </div>
        </div>
      )}

      {summary && summary.by_market && Object.keys(summary.by_market).length > 0 && (
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <h3 className="text-sm font-bold text-slate-300 mb-3">按玩法统计</h3>
          <div className="grid grid-cols-4 gap-3">
            {Object.entries(summary.by_market).map(([kind, stats]: [string, { pnl: number; roi_pct: number }]) => (
              <div key={kind} className="rounded border border-slate-800 p-3">
                <div className="text-xs text-slate-400">{kind}</div>
                <div className={`text-lg font-bold mt-1 ${stats.pnl >= 0 ? "text-emerald-300" : "text-red-300"}`}>
                  {stats.pnl >= 0 ? "+" : ""}¥{stats.pnl.toFixed(0)}
                </div>
                <div className="text-xs text-slate-500">ROI {stats.roi_pct >= 0 ? "+" : ""}{stats.roi_pct.toFixed(1)}%</div>
                <div className="text-xs text-slate-600 mt-1">{stats.count} 单 · 命中率 {stats.hit_rate_pct.toFixed(0)}%</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {showAdd && (
        <div className="rounded-lg border border-emerald-700/50 bg-emerald-900/10 p-4">
          <h3 className="text-sm font-bold text-emerald-200 mb-3">新建方案</h3>
          <div className="grid grid-cols-5 gap-3">
            <input
              type="text"
              placeholder="方案名"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm"
            />
            <select
              value={newKind}
              onChange={(e) => setNewKind(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm"
            >
              <option value="single">单注</option>
              <option value="parlay">串关</option>
              <option value="lotto14">14 场</option>
              <option value="lotto9">任选九</option>
            </select>
            <input
              type="number"
              step="0.01"
              placeholder="赔率"
              value={newOdds}
              onChange={(e) => setNewOdds(+e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm font-mono"
            />
            <input
              type="number"
              placeholder="本金 ¥"
              value={newStake}
              onChange={(e) => setNewStake(+e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-sm font-mono"
            />
            <button
              onClick={add}
              className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-sm"
            >
              保存
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-sm text-slate-500 text-center py-8">加载中...</div>
      ) : slips.length === 0 ? (
        <div className="text-sm text-slate-500 text-center py-8 border border-dashed border-slate-800 rounded">
          暂无方案。点 "+ 新建方案" 录入第一单。
        </div>
      ) : (
        <div className="space-y-2">
          {slips.map((s) => (
            <div
              key={s.id}
              className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 flex items-center gap-4"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-200 truncate">{s.title}</span>
                  <span className="text-xs px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {s.kind}
                  </span>
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  @{s.total_odds.toFixed(2)} · ¥{s.stake.toFixed(0)} · {formatDateZh(s.created_at)}
                </div>
              </div>
              <div className={`text-sm font-mono ${resultColor(s.result)}`}>
                {s.result === "win" ? "中" : s.result === "lose" ? "未中" : s.result === "void" ? "作废" : "待"}
                {s.settled_at && (
                  <div className="text-xs">
                    {s.pnl >= 0 ? "+" : ""}¥{s.pnl.toFixed(0)}
                  </div>
                )}
              </div>
              {s.result === "pending" && (
                <div className="flex gap-1">
                  <button
                    onClick={() => settle(s.id, "win")}
                    className="p-1.5 rounded bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-200"
                    title="标记为中"
                  >
                    <Check className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => settle(s.id, "lose")}
                    className="p-1.5 rounded bg-red-600/30 hover:bg-red-600/50 text-red-200"
                    title="标记为未中"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
              <button
                onClick={() => del(s.id)}
                className="p-1.5 rounded hover:bg-slate-800 text-slate-500"
                title="删除"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
