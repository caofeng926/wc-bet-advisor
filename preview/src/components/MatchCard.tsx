import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import TeamFlag from "./TeamFlag";
import ValueBadge from "./ValueBadge";
import { formatDateZh, formatHMS, countdownColor } from "../lib/time";
import type { MatchApi } from "../lib/api";
import type { ModelPrediction } from "../mock/predictions";

interface Props { match: MatchApi; pick: ModelPrediction | null; }

export default function MatchCard({ match, pick }: Props) {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    if (!match.betting_close_at) return;
    const t = setInterval(() => {
      setSeconds(Math.floor((new Date(match.betting_close_at!).getTime() - Date.now()) / 1000));
    }, 1000);
    return () => clearInterval(t);
  }, [match.betting_close_at]);

  const closed = seconds <= 0;
  const color = countdownColor(seconds);
  const colorMap = {
    green:  "text-emerald-300",
    yellow: "text-amber-300",
    red:    "text-red-300 pulse-red",
    gray:   "text-slate-500",
  }[color];

  return (
    <Link
      to={`/matches/${match.id}`}
      className={`block rounded-lg border bg-slate-900/40 hover:bg-slate-800/60 transition p-4 ${
        closed ? "border-slate-800 opacity-60" : "border-slate-700"
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-slate-500">
          {match.stage}
          {match.group && <span className="ml-2 px-1.5 py-0.5 bg-slate-800 rounded text-slate-400">{match.group} 组</span>}
        </span>
        <span className={`text-xs font-mono ${colorMap}`}>
          {closed ? "已截止" : `⏱ ${formatHMS(seconds)}`}
        </span>
      </div>
      <div className="flex items-center justify-between gap-3">
        <div className="flex-1">
          <TeamFlag iso3={match.home.iso3} name_zh={match.home.name_zh} size="md" />
        </div>
        <div className="text-slate-600 text-sm font-bold">VS</div>
        <div className="flex-1 text-right">
          <TeamFlag iso3={match.away.iso3} name_zh={match.away.name_zh} size="md" />
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
        <div className="flex items-center gap-3">
          <span className="text-slate-500">🕐 {formatDateZh(match.kickoff_at)}</span>
          {/* ELO差显示 */}
          <span className="text-slate-600" title="ELO差值（正值=主队强）">
            ⚡ ELO {(match.home.elo - match.away.elo) > 0 ? "+" : ""}{match.home.elo - match.away.elo}
          </span>
        </div>
        {match.status === "ft" ? (
          <span className="text-slate-400 font-mono">
            终场 {match.ft_home} : {match.ft_away}
          </span>
        ) : pick ? (
          <div className="flex items-center gap-2">
            <span className="text-slate-300">
              {pick.market === "ah" ? pick.selection : (pick.selection === "H" ? "主胜" : pick.selection === "D" ? "平局" : "客胜")}
              <span className="ml-1 text-emerald-400 font-mono">@{pick.odds.toFixed(2)}</span>
            </span>
            <ValueBadge edge={pick.edge} />
          </div>
        ) : (
          <span className="text-slate-500">无推荐</span>
        )}
      </div>
    </Link>
  );
}
