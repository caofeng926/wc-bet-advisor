import { useEffect, useState } from "react";
import { AlertTriangle, Save } from "lucide-react";
import { api, type ParlayCandidate } from "../lib/api";
import TeamFlag from "../components/TeamFlag";
import { formatDateZh } from "../lib/time";

interface Leg {
  id: string;
  matchId: number;
  selection: string;
  odds: number;
  edge: number;
}

const LABEL: Record<string, string> = { H: "主胜", D: "平", A: "客胜" };

function findTeamLabel(c: ParlayCandidate): string {
  return c.market === "ah" ? c.selection : LABEL[c.selection] || c.selection;
}

export default function ParlayBuilder() {
  const [candidates, setCandidates] = useState<ParlayCandidate[]>([]);
  const [selected, setSelected] = useState<Leg[]>([]);
  const [loading, setLoading] = useState(true);
  const [stake, setStake] = useState(10);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const c = await api.getParlayCandidates(0.05);
        if (mounted) {
          setCandidates(c);
          setLoading(false);
        }
      } catch (e) {
        console.error(e);
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  function toggle(c: ParlayCandidate) {
    const id = `${c.match_id}-${c.market}-${c.selection}`;
    if (selected.find((s) => s.id === id)) {
      setSelected(selected.filter((s) => s.id !== id));
    } else {
      if (selected.length >= 6) {
        alert("混合过关最多选6场，请先取消已选选项");
        return;
      }
      setSelected([
        ...selected,
        {
          id,
          matchId: c.match_id,
          selection: c.market === "ah" ? c.selection : LABEL[c.selection] || c.selection,
          odds: c.odds,
          edge: c.edge,
        },
      ]);
    }
  }

  const totalOdds = selected.reduce((a, l) => a * l.odds, 1);
  const combinedEdge = selected.reduce((a, l) => a * (1 + l.edge), 1) - 1;
  const suggestedStake = Math.min(stake * Math.max(0, combinedEdge) * 0.25, stake * 0.5);

  const groupPenalty = (() => {
    if (selected.length < 2) return 1;
    let p = 1;
    for (let i = 0; i < selected.length; i++) {
      const a = candidates.find((c) => c.match_id === selected[i].matchId);
      if (!a) continue;
      for (let j = i + 1; j < selected.length; j++) {
        const b = candidates.find((c) => c.match_id === selected[j].matchId);
        if (!b) continue;
        if (a.group && a.group === b.group) p *= 0.7;
        if (a.kickoff_date === b.kickoff_date) p *= 0.85;
      }
    }
    return p;
  })();

  async function save() {
    if (selected.length === 0) return;
    const title = `串关 ${selected.length} 场 @${totalOdds.toFixed(2)}`;
    await api.createSlip({
      title,
      kind: "parlay",
      selections: selected.map((l) => ({
        match_id: l.matchId,
        pick: l.selection,
        odds: l.odds,
      })),
      total_odds: totalOdds,
      stake: stake,
    });
    alert("已保存到方案库");
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">混合过关构造器</h1>
        <p className="text-sm text-slate-400 mt-1">从高价值候选中勾选多场，自动计算累计赔率 / edge / 相关性</p>
        {/* 说明 */}
        <div className="mt-2 p-3 rounded-lg border border-slate-800 bg-slate-900/20 text-xs text-slate-400 leading-relaxed">
          <strong className="text-slate-300">💡 串关是什么：</strong>
          把多场比赛绑在一起猜，全部猜对才算赢。
          <strong className="text-emerald-300">总赔率 = 各场赔率相乘</strong>（2串1 ×2.0×1.9 = 3.8倍），
          但难度也相乘。同组或同日赛事会打折扣（<strong className="text-amber-300">相关性惩罚</strong>），
          因为它们结果往往相关。
        </div>
      </div>

      {loading ? (
        <div className="text-sm text-slate-500 text-center py-12">从后端加载候选...</div>
      ) : candidates.length === 0 ? (
        <div className="text-sm text-slate-500 text-center py-12 border border-dashed border-slate-800 rounded">
          暂无 edge ≥ 5% 的候选
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-6">
          <section>
            <h2 className="text-sm font-bold text-slate-300 mb-3">
              候选 ({candidates.length} 个)
            </h2>
            {selected.length > 0 && (
              <div className="text-xs text-amber-400 mb-2">
                已选 {selected.length}/6 场 · 最多6关
              </div>
            )}
            <div className="space-y-2">
              {candidates.map((c) => {
                const id = `${c.match_id}-${c.market}-${c.selection}`;
                const checked = selected.some((s) => s.id === id);
                return (
                  <label
                    key={id}
                    className={`flex items-center gap-3 p-3 rounded border cursor-pointer transition ${
                      checked
                        ? "border-emerald-600 bg-emerald-900/20"
                        : selected.length >= 6
                        ? "border-slate-800 opacity-40 cursor-not-allowed"
                        : "border-slate-800 hover:bg-slate-800/40"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggle(c)}
                      className="w-4 h-4 accent-emerald-500"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 text-sm">
                        <TeamFlag iso3={c.home} name_zh="" size="sm" showName={false} />
                        <span className="text-slate-300 truncate">{c.home}</span>
                        <span className="text-slate-600 text-xs">vs</span>
                        <TeamFlag iso3={c.away} name_zh="" size="sm" showName={false} />
                        <span className="text-slate-300 truncate">{c.away}</span>
                      </div>
                      <div className="text-[10px] text-slate-500 mt-0.5">
                        {c.group} · {formatDateZh(c.kickoff_at)}
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-xs text-slate-400">{findTeamLabel(c)}</div>
                      <div className="text-sm font-mono font-bold text-emerald-300">@{c.odds.toFixed(2)}</div>
                      <div className="text-xs text-emerald-400 font-mono">+{(c.edge * 100).toFixed(0)}%</div>
                    </div>
                  </label>
                );
              })}
            </div>
          </section>

          <section>
            <h2 className="text-sm font-bold text-slate-300 mb-3">
              已选 (<span className="text-emerald-400">{selected.length}</span> 场)
            </h2>
            {selected.length === 0 ? (
              <div className="text-sm text-slate-500 text-center py-12 border border-dashed border-slate-800 rounded">
                勾选左侧候选,这里会显示累计统计
              </div>
            ) : (
              <div className="space-y-3">
                <div className="rounded-lg border border-slate-700 bg-slate-900/60 p-3">
                  {selected.map((l) => (
                    <div key={l.id} className="flex items-center justify-between py-1.5 text-sm border-b border-slate-800 last:border-0">
                      <div className="text-slate-300">{l.selection}</div>
                      <span className="text-emerald-300 font-mono font-bold">@{l.odds.toFixed(2)}</span>
                    </div>
                  ))}
                </div>

                <div className="rounded-lg border-2 border-emerald-700/50 bg-emerald-900/10 p-4 space-y-2">
                  {/* 统计说明 */}
                  <div className="text-[11px] text-slate-500 mb-2 leading-relaxed">
                    <span className="text-slate-400 font-medium">各指标说明：</span>
                    总赔率 = 各场赔率相乘；组合 Edge = 考虑相关性后的综合优势；
                    建议注金 =1/4凯利（保守模式）+ 单注5%封顶
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">总赔率</span>
                    <span className="text-2xl font-bold text-emerald-300 font-mono">{totalOdds.toFixed(2)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">组合 Edge</span>
                    <span className={`text-base font-mono font-bold ${combinedEdge > 0 ? "text-emerald-300" : "text-red-300"}`}>
                      {combinedEdge > 0 ? "+" : ""}{(combinedEdge * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">本金</span>
                    <input
                      type="number"
                      value={stake}
                      onChange={(e) => setStake(+e.target.value)}
                      className="w-20 text-right bg-slate-800 border border-slate-700 rounded px-2 py-0.5 font-mono"
                    />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">建议注金(¼ Kelly)</span>
                    <span className="text-base font-mono font-bold text-amber-300">¥{suggestedStake.toFixed(0)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">相关性惩罚</span>
                    <span className="text-base font-mono text-purple-300">×{groupPenalty.toFixed(2)}</span>
                  </div>
                </div>

                {groupPenalty < 0.95 && (
                  <div className="text-xs text-amber-300 bg-amber-900/20 border border-amber-800/50 rounded p-2 flex gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                    <span>检测到同组/同日比赛，实际组合价值可能被高估，已用 ×{groupPenalty.toFixed(2)} 折扣。</span>
                  </div>
                )}

                <button
                  onClick={save}
                  className="w-full px-4 py-2.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium flex items-center justify-center gap-1.5"
                >
                  <Save className="w-4 h-4" /> 保存为方案(进方案库)
                </button>
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
