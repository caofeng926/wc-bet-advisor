import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";
import TeamFlag from "../components/TeamFlag";
import Guide from "../components/Guide";
import { api, type MatchApi } from "../lib/api";
import { formatDateZh, formatHMS, countdownColor } from "../lib/time";

interface Row {
  match_id: number;
  home: string;
  away: string;
  kickoff_at: string;
  picks: string[];
  p_each: Record<string, number>;
  best_pick: string;
  best_p: number;
}
interface Ticket {
  picks: string[];
  stake_count: number;
  cost: number;
  ev_pct: number;
  kind: "main" | "backup";
}

const COLORS: Record<string, string> = { H: "bg-emerald-600", D: "bg-amber-500", A: "bg-blue-600" };
const LABEL: Record<string, string> = { H: "胜", D: "平", A: "负" };

export default function Lotto14() {
  const [rows, setRows] = useState<Row[]>([]);
  const [main, setMain] = useState<Ticket | null>(null);
  const [backups, setBackups] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [apiUp, setApiUp] = useState<boolean | null>(null);
  const [issue, setIssue] = useState("");
  const [kind, setKind] = useState<"14" | "9">("14");

  useEffect(() => {
    let mounted = true;
    api.health().then(() => mounted && setApiUp(true)).catch(() => mounted && setApiUp(false));
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    if (rows.length === 0) return;
    const earliest = rows.reduce((a, b) => new Date(a.kickoff_at) < new Date(b.kickoff_at) ? a : b);
    const tick = () => setSeconds(Math.floor((new Date(earliest.kickoff_at).getTime() - Date.now() - 5 * 60 * 1000) / 1000));
    tick();
    const t = setInterval(tick, 1000);
    return () => clearInterval(t);
  }, [rows]);

  async function generate() {
    setLoading(true);
    try {
      const d = kind === "14" ? await api.getLotto14() : await api.getLotto9();
      const eloDiff = (m: MatchApi) => m.home.elo - m.away.elo;
      const probH = (m: MatchApi) => 1 / (1 + 10 ** (-(eloDiff(m) + 80) / 400));
      const newRows: Row[] = d.matches.map((m: MatchApi) => {
        const pH = probH(m);
        const pA = 1 - pH;
        const pD = Math.max(0.15, (1 - Math.abs(2 * pH - 1)) * 0.30);
        const s = pH + pD + pA;
        const probs = { H: pH / s, D: pD / s, A: pA / s };
        const bestPick = maxObj(probs);
        return {
          match_id: m.id,
          home: m.home.iso3,
          away: m.away.iso3,
          kickoff_at: m.kickoff_at,
          picks: [bestPick],
          p_each: { H: pH / s, D: pD / s, A: pA / s },
          best_pick: bestPick,
          best_p: probs[bestPick as keyof typeof probs],
        };
      });
      setRows(newRows);
      setMain(d.main);
      setBackups(d.backups);
      setIssue(d.issue_no);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  function maxObj(o: Record<string, number>): string {
    return Object.keys(o).reduce((a, b) => (o[b] > o[a] ? b : a));
  }

  const color = countdownColor(seconds);
  const colorMap: string = (() => {
    const map: Record<string, string> = {
      green: "text-emerald-300",
      yellow: "text-amber-300",
      red: "text-red-300 pulse-red",
      gray: "text-slate-500",
    };
    return map[color] ?? "text-slate-300";
  })();

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">{kind === "14" ? "第 " + issue + " 期 · 胜负彩 14 场" : "任选九"}</h1>
          <p className="text-sm text-slate-400 mt-1">
            {rows.length > 0 && `首场 ${formatDateZh(rows[0].kickoff_at)} 开赛`}
          </p>
          {/* 说明卡片 */}
          <div className="mt-2 p-3 rounded-lg border border-slate-800 bg-slate-900/20 text-xs text-slate-400 leading-relaxed">
            <span className="text-slate-300 font-medium">💡 怎么看懂这个页面：</span>
            {kind === "14" ? (
              <>14场胜负彩要求猜中全部14场比赛的胜平负。<strong className="text-slate-200">主推</strong>是模型最有信心的一注，<strong className="text-slate-200">复式</strong>是对信心不足的场次多选了其他结果（如"胜/平"），增加了中奖概率但也增加了成本。每注2元。</>
            ) : (
              <>任选九是从14场中任选9场来猜，难度比14场低，但奖金也相对少。<strong className="text-slate-200">主推</strong>是模型精选的9场。</>
            )}
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500">距销售截止</div>
          <div className={`text-2xl font-mono font-bold ${colorMap}`}>{formatHMS(seconds)}</div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={generate}
          disabled={loading || apiUp === false}
          className="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-medium flex items-center gap-1.5"
        >
          <Sparkles className="w-4 h-4" />
          {loading ? "生成中..." : kind === "14" ? "一键生成 14 场推荐" : "一键生成任选九"}
        </button>
        <div className="flex gap-1 bg-slate-800/40 rounded p-1">
          <button
            onClick={() => setKind("14")}
            className={`px-3 py-1 rounded text-sm ${kind === "14" ? "bg-emerald-600" : "text-slate-400"}`}
          >
            14 场
          </button>
          <button
            onClick={() => setKind("9")}
            className={`px-3 py-1 rounded text-sm ${kind === "9" ? "bg-emerald-600" : "text-slate-400"}`}
          >
            任选九
          </button>
        </div>
        <Guide items={[
          { term: "主胜 / 平局 / 客胜", def: "主队赢=主胜，平局=平，客队赢=客胜。对应3个选项。" },
          { term: "主推", def: "模型认为概率最高的选项组成的一注。单注2元，全对才中奖。" },
          { term: "复式", def: "对某场同时选2个结果（如胜/平），成本翻倍但更容易中奖。" },
          { term: "EV (期望值)", def: "理论长期收益的百分比。EV+10%表示每投入100元长期可回收110元。" },
          { term: "ELO", def: "球队实力评分。巴西ELO~2050，卡塔尔~1600，差值越大强队优势越明显。" },
        ]} />
        {apiUp === false && (
          <span className="text-xs text-red-300">⚠️ 后端未运行</span>
        )}
      </div>

      {rows.length > 0 && (
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-800/60 text-slate-300 text-xs">
              <tr>
                <th className="text-left px-3 py-2 w-10">#</th>
                <th className="text-left px-3 py-2">对阵</th>
                <th className="px-3 py-2 w-1/4">
                  <span className="text-emerald-400">主胜</span>
                  <span className="text-slate-600 ml-1">(概率)</span>
                </th>
                <th className="px-3 py-2 w-1/4">
                  <span className="text-amber-400">平局</span>
                  <span className="text-slate-600 ml-1">(概率)</span>
                </th>
                <th className="px-3 py-2 w-1/4">
                  <span className="text-blue-400">客胜</span>
                  <span className="text-slate-600 ml-1">(概率)</span>
                </th>
                <th className="px-3 py-2 w-32">模型推荐</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {rows.map((r) => (
                <tr key={r.match_id} className="hover:bg-slate-800/30">
                  <td className="px-3 py-2 text-slate-500 font-mono">{r.match_id}</td>
                  <td className="px-3 py-2">
                    <div className="flex items-center gap-2">
                      <TeamFlag iso3={r.home} name_zh="" size="sm" showName={false} />
                      <span className="text-slate-200">{r.home}</span>
                      <span className="text-slate-600 text-xs mx-1">vs</span>
                      <TeamFlag iso3={r.away} name_zh="" size="sm" showName={false} />
                      <span className="text-slate-200">{r.away}</span>
                    </div>
                  </td>
                  {(["H", "D", "A"] as const).map((k) => (
                    <td key={k} className="px-3 py-2">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-slate-800 rounded overflow-hidden">
                          <div className={`h-full ${COLORS[k]}`} style={{ width: `${(r.p_each[k] || 0) * 100}%` }} />
                        </div>
                        <span className="w-10 text-right font-mono text-slate-300 text-xs">
                          {((r.p_each[k] || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                  ))}
                  <td className="px-3 py-2">
                    <div className="flex gap-1">
                      {(["H", "D", "A"] as const).map((k) => {
                        const isPicked = r.picks.includes(k) || r.best_pick === k;
                        return (
                          <span
                            key={k}
                            className={`px-2 py-0.5 rounded text-xs font-bold ${
                              isPicked
                                ? k === "H" ? "bg-emerald-600 text-white" : k === "D" ? "bg-amber-600 text-white" : "bg-blue-600 text-white"
                                : "bg-slate-800 text-slate-500"
                            }`}
                          >
                            {LABEL[k]}
                          </span>
                        );
                      })}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {main && (
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-emerald-400" /> 生成结果
          </h2>
          {/* 结果说明 */}
          <div className="text-xs text-slate-500 bg-slate-900/20 rounded p-3 border border-slate-800 leading-relaxed">
            <strong className="text-slate-300">怎么看这些结果：</strong>
            主推是模型最有信心的选择。复式1-6是对部分场次加了双选。
            <span className="text-emerald-400 ml-1">EV +X%</span> = 理论长期每投入100元可额外收回X元。
            例如 EV+8% 意味着长期胜率对的话平均回报率为 108%。
          </div>
          <div className="rounded-lg border-2 border-emerald-700/50 bg-emerald-900/10 p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm font-bold text-emerald-200">
                主推 · {main.stake_count} 注 · ¥{main.cost.toFixed(0)}
              </div>
              <div className="text-xs font-mono text-emerald-300">理论 EV +{main.ev_pct}%</div>
            </div>
            <div className="flex flex-wrap gap-1 font-mono text-xs">
              {main.picks.map((p, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700"
                >
                  {i + 1}.{p.split("").map((c) => LABEL[c] || c).join("/")}
                </span>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {backups.map((t, idx) => (
              <div key={idx} className="rounded-lg border border-slate-700 bg-slate-900/40 p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm font-bold text-slate-300">
                    复式 {idx + 1} · {t.stake_count} 注 · ¥{t.cost.toFixed(0)}
                  </div>
                  <div className="text-xs font-mono text-slate-400">期望收益 +{t.ev_pct}%</div>
                </div>
                <div className="flex flex-wrap gap-1 font-mono text-[10px]">
                  {t.picks.map((p, i) => (
                    <span
                      key={i}
                      className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700"
                    >
                      {i + 1}.{p.split("").map((c) => LABEL[c] || c).join("/")}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

