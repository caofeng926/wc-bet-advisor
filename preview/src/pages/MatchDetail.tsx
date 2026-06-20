import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Save, Check, SkipForward, AlertCircle, TrendingUp } from "lucide-react";
import OddsTable from "../components/OddsTable";
import ValueBadge from "../components/ValueBadge";
import KellyCalculator from "../components/KellyCalculator";
import TeamFlag from "../components/TeamFlag";
import { formatDateZh } from "../lib/time";
import { api, type MatchApi, type OddApi, type PoissonPrediction } from "../lib/api";
import { getPredictions } from "../mock/predictions";

export default function MatchDetail() {
  const { id } = useParams();
  const matchId = +(id || "0");
  const [match, setMatch] = useState<MatchApi | null>(null);
  const [odds, setOdds] = useState<OddApi[]>([]);
  const [poisson, setPoisson] = useState<PoissonPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const [m, o, p] = await Promise.all([
          api.getMatch(matchId),
          api.getMatchOdds(matchId),
          api.getPoisson(matchId).catch(() => null),
        ]);
        if (mounted) {
          setMatch(m);
          setOdds(o);
          setPoisson(p);
          setLoading(false);
        }
      } catch (e) {
        if (mounted) {
          setError(e instanceof Error ? e.message : "加载失败");
          setLoading(false);
        }
      }
    })();
    return () => { mounted = false; };
  }, [matchId]);

  if (loading) return <div className="text-slate-400 text-sm py-12 text-center">加载中...</div>;
  if (error || !match) {
    return (
      <div className="rounded-lg border border-red-800/50 bg-red-900/20 p-6 max-w-lg">
        <div className="flex gap-2 text-red-200 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <div>
            <div className="font-medium">无法加载比赛 #{matchId}</div>
            <div className="text-red-300/80 text-xs mt-1">{error || "比赛不存在"}</div>
            <Link to="/" className="text-emerald-400 hover:underline mt-3 inline-block">← 返回 Dashboard</Link>
          </div>
        </div>
      </div>
    );
  }

  const marketOdds = odds.filter((o) => o.market === "1x2");
  const ahOdds = odds.filter((o) => o.market === "ah");
  const preds = getPredictions(match.id, match.home.elo, match.away.elo).filter((p) => p.recommended);

  // 把泊松 top3 比分映射成 "value" 卡片
  const over25 = poisson
    ? Object.entries(poisson.goals_distribution)
        .filter(([k]) => parseInt(k) >= 3)
        .reduce((sum, [, v]) => sum + v, 0)
    : 0;
  const under25 = 1 - over25;
  const btts = poisson
    ? poisson.score_matrix.slice(1, 6).reduce(
        (s, row) => s + row.slice(1, 6).reduce((a, b) => a + b, 0),
        0
      )
    : 0;

  return (
    <div className="space-y-6">
      <div>
        <Link to="/" className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1">
          <ArrowLeft className="w-3 h-3" /> 返回 Dashboard
        </Link>
        <div className="mt-3 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-500 mb-1">
              {match.stage} {match.group && `· ${match.group} 组`} · {match.venue}
            </div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-4">
              <TeamFlag iso3={match.home.iso3} name_zh={match.home.name_zh} size="lg" showName={true} />
              <span className="text-slate-500">VS</span>
              <TeamFlag iso3={match.away.iso3} name_zh={match.away.name_zh} size="lg" showName={true} />
            </h1>
            <div className="text-sm text-slate-400 mt-2">
              🕐 {formatDateZh(match.kickoff_at)} · 距购彩截止 {match.minutes_to_close} 分钟
            </div>
          </div>
          {match.status === "ft" && (
            <div className="text-right">
              <div className="text-xs text-slate-500">终场比分</div>
              <div className="text-3xl font-bold font-mono text-slate-300">
                {match.ft_home} : {match.ft_away}
              </div>
            </div>
          )}
        </div>
      </div>

      <section>
        <h2 className="text-sm font-bold text-slate-300 mb-3">📊 赔率对比</h2>
        {marketOdds.length > 0 && (
          <>
            <h3 className="text-xs text-slate-500 mb-2">胜平负</h3>
            <OddsTable rows={marketOdds} />
          </>
        )}
        {ahOdds.length > 0 && (
          <>
            <h3 className="text-xs text-slate-500 mb-2 mt-4">让球胜平负</h3>
            <OddsTable rows={ahOdds} />
          </>
        )}
      </section>

      <section>
        <h2 className="text-sm font-bold text-slate-300 mb-3">🎯 价值分析(模型 vs 市场)</h2>
        {/* 说明 */}
        <div className="mb-3 p-2.5 rounded-lg border border-slate-800 bg-slate-900/20 text-xs text-slate-400 leading-relaxed">
          <strong className="text-slate-300">💡 怎么看懂价值分析：</strong>
          <strong className="text-emerald-300">ELO</strong> = 根据球队实力(ELO评分)推算的胜率；
          <strong className="text-emerald-300">市场</strong> = 根据赔率倒推的隐含概率；
          <strong className="text-emerald-300">Model</strong> = 两者加权融合后的最终概率。
          <strong className="text-emerald-300">Edge</strong> = Model概率 × 赔率 − 1，edge &gt; 5% 才算有价值。
        </div>
        <div className="grid grid-cols-2 gap-4">
          {preds.length === 0 ? (
            <div className="col-span-2 text-center py-8 text-slate-500 text-sm">
              本场无 edge ≥ 5% 的推荐
            </div>
          ) : (
            preds.map((p) => (
              <div key={`${p.market}-${p.selection}`} className="rounded-lg border border-emerald-700/40 bg-emerald-900/10 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm font-bold text-emerald-200">
                    {p.market === "ah" ? "让球 " : ""}
                    {p.selection === "H" ? "主胜" : p.selection === "D" ? "平局" : p.selection === "A" ? "客胜" : p.selection}
                    <span className="ml-2 text-emerald-300 font-mono">@{p.odds.toFixed(2)}</span>
                  </div>
                  <ValueBadge edge={p.edge} size="md" />
                </div>
                <div className="text-xs text-slate-400 space-y-0.5">
                  <div>ELO 评分: <span className="font-mono text-slate-200">{(p.p_elo * 100).toFixed(0)}%</span></div>
                  <div>市场: <span className="font-mono text-slate-200">{(p.p_market * 100).toFixed(0)}%</span></div>
                  <div>模型概率: <span className="font-mono text-emerald-300 font-bold">{(p.p_final * 100).toFixed(0)}%</span></div>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {poisson && (
        <section>
          <h2 className="text-sm font-bold text-slate-300 mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            泊松比分预测
            <span className="text-xs text-slate-500 font-normal ml-1">
              (λ_home={poisson.lambda_home} / λ_away={poisson.lambda_away})
            </span>
          </h2>
          {/* 泊松说明 */}
          <div className="mb-3 p-2.5 rounded-lg border border-slate-800 bg-slate-900/20 text-xs text-slate-400 leading-relaxed">
            <strong className="text-slate-300">💡 泊松模型是什么：</strong>
            假设比赛进球符合"泊松分布"——弱队偶尔进1-2球，强队进2-3球。
            λ( lambda)是平均进球数，ELO差越大 λ差越大。
            <strong className="text-cyan-300">大2.5球</strong> = 总进球≥3的概率，
            <strong className="text-purple-300">BTTS(双方都进球)</strong> = 双方都进球的概率。
            Top5比分 = 模型认为最可能出现的5个比分。
          </div>
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="rounded-lg border border-cyan-800/50 bg-cyan-900/10 p-3">
              <div className="text-xs text-slate-400">大 2.5 球</div>
              <div className="text-2xl font-bold text-cyan-300 mt-1">{(over25 * 100).toFixed(0)}%</div>
              <div className="text-xs text-slate-500 mt-1">小 2.5: {(under25 * 100).toFixed(0)}%</div>
            </div>
            <div className="rounded-lg border border-purple-800/50 bg-purple-900/10 p-3">
              <div className="text-xs text-slate-400">两队都进球 (BTTS)</div>
              <div className="text-2xl font-bold text-purple-300 mt-1">{(btts * 100).toFixed(0)}%</div>
              <div className="text-xs text-slate-500 mt-1">至少 1-0 或 0-1: {((1 - btts) * 100).toFixed(0)}%</div>
            </div>
            <div className="rounded-lg border border-amber-800/50 bg-amber-900/10 p-3">
              <div className="text-xs text-slate-400">总进球期望</div>
              <div className="text-2xl font-bold text-amber-300 mt-1">{(poisson.lambda_home + poisson.lambda_away).toFixed(2)}</div>
              <div className="text-xs text-slate-500 mt-1">λ_home + λ_away</div>
            </div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
            <div className="text-xs text-slate-400 mb-2">Top 5 比分概率</div>
            <div className="grid grid-cols-5 gap-2">
              {poisson.top_scores.slice(0, 5).map(([score, p]) => (
                <div key={score} className="rounded bg-slate-800/50 p-2 text-center">
                  <div className="text-2xl font-bold font-mono text-slate-100">{score}</div>
                  <div className="text-xs text-emerald-300 font-mono mt-1">{(p * 100).toFixed(1)}%</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      <section>
        <h2 className="text-sm font-bold text-slate-300 mb-3">💰 凯利试算</h2>
        {preds.length > 0 ? (
          <KellyCalculator defaultOdds={preds[0].odds} defaultP={preds[0].p_final} />
        ) : (
          <KellyCalculator />
        )}
      </section>

      <section>
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium flex items-center gap-1.5">
            <Save className="w-4 h-4" /> 保存为方案
          </button>
          <button className="px-4 py-2 rounded border border-slate-700 hover:bg-slate-800 text-slate-200 text-sm flex items-center gap-1.5">
            <Check className="w-4 h-4" /> 我已购买
          </button>
          <button className="px-4 py-2 rounded border border-slate-700 hover:bg-slate-800 text-slate-400 text-sm flex items-center gap-1.5">
            <SkipForward className="w-4 h-4" /> 跳过
          </button>
        </div>
      </section>
    </div>
  );
}
