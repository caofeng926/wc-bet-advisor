import { useEffect, useState } from "react";
import { useLocation, Link } from "react-router-dom";
import { formatHMS, countdownColor } from "../lib/time";
import { api, type CountdownApi } from "../lib/api";

export default function CountdownBanner() {
  const [data, setData] = useState<CountdownApi | null>(null);
  const loc = useLocation();

  useEffect(() => {
    let mounted = true;
    api.getCountdown().then((d) => {
      if (mounted) setData(d);
    }).catch(() => {});
    const poll = setInterval(() => {
      api.getCountdown().then((d) => {
        if (mounted) setData(d);
      }).catch(() => {});
    }, 10000);
    return () => { mounted = false; clearInterval(poll); };
  }, []);

  if (!data) return null;

  const seconds = data.seconds_remaining;
  const color = countdownColor(seconds);
  const closed = seconds <= 0 || data.status === "all_closed";

  const colorMap: Record<string, { bg: string; border: string; text: string; dot: string }> = {
    green:  { bg: "bg-emerald-900/60", border: "border-emerald-700", text: "text-emerald-300", dot: "bg-emerald-400" },
    yellow: { bg: "bg-amber-900/60",   border: "border-amber-700",   text: "text-amber-300",   dot: "bg-amber-400 pulse-yellow" },
    red:    { bg: "bg-red-900/70",     border: "border-red-700",     text: "text-red-300",     dot: "bg-red-400 pulse-red" },
    gray:   { bg: "bg-slate-800/60",   border: "border-slate-700",   text: "text-slate-400",   dot: "bg-slate-500" },
  };
  const cm = colorMap[color] ?? colorMap.gray;

  return (
    <div className={`${cm.bg} ${cm.border} border-b backdrop-blur`}>
      <div className="max-w-7xl mx-auto px-4 py-2 flex items-center justify-between text-sm">
        <div className="flex items-center gap-3">
          <span className={`w-2.5 h-2.5 rounded-full ${cm.dot}`} />
          {closed ? (
            <span className={cm.text}>
              {data.status === "all_closed" ? "今日销售已全部截止" : `距 ${data.home} vs ${data.away} 截止时间已过`}
            </span>
          ) : (
            <span className={cm.text}>
              距 <span className="font-bold">{data.home} vs {data.away}</span> 购彩截止
            </span>
          )}
        </div>
        <div className="flex items-center gap-4">
          <span className={`font-mono text-lg font-bold ${cm.text}`}>
            {formatHMS(seconds)}
          </span>
          {!closed && data.match_id && loc.pathname !== `/matches/${data.match_id}` && (
            <Link
              to={`/matches/${data.match_id}`}
              className="text-xs text-slate-300 hover:text-white underline-offset-2 hover:underline"
            >
              去看 →
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
