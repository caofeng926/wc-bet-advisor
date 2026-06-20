import { Outlet, NavLink, Link } from "react-router-dom";
import CountdownBanner from "./CountdownBanner";
import { Home, Trophy, Layers, ClipboardList, Target, TrendingUp, Timer, Award } from "lucide-react";

export default function Layout() {
  const nav = [
    { to: "/", label: "首页 总览", icon: Home },
    { to: "/lotto14", label: "14场胜负彩", icon: Trophy },
    { to: "/champion", label: "猜冠军/冠亚军", icon: Award },
    { to: "/parlay", label: "混合过关", icon: Layers },
    { to: "/score", label: "比分推荐", icon: Target },
    { to: "/total", label: "总进球推荐", icon: TrendingUp },
    { to: "/htft", label: "半全场推荐", icon: Timer },
    { to: "/slips", label: "方案库 / 复盘", icon: ClipboardList },
  ];
  return (
    <div className="min-h-screen flex flex-col">
      <CountdownBanner />
      <header className="bg-slate-900/80 border-b border-slate-800 backdrop-blur sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <img src="/wc26-logo.svg" alt="WC 2026" className="w-10 h-10" />
            <div>
              <div className="text-lg font-bold text-white leading-tight">WC-Bet-Advisor</div>
              <div className="text-[10px] text-slate-400 leading-tight tracking-widest">2026 世界杯购彩建议 · v0.2.0</div>
            </div>
          </Link>
          <div className="text-xs text-slate-500">v0.2.0 · live</div>
        </div>
      </header>
      <div className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 flex gap-6">
        <aside className="w-56 shrink-0">
          <nav className="space-y-1 sticky top-24">
            {nav.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.to === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-3 py-2.5 rounded-md text-sm transition ${
                    isActive
                      ? "bg-emerald-600/20 text-emerald-300 border border-emerald-700/50"
                      : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                  }`
                }
              >
                <n.icon className="w-4 h-4" />
                {n.label}
              </NavLink>
            ))}
            <div className="pt-4 mt-4 border-t border-slate-800">
              <div className="text-[10px] text-slate-600 px-3 uppercase tracking-widest">说明</div>
              <div className="text-xs text-slate-500 mt-2 px-3 leading-relaxed">
                数据基于 2026 世界杯真实分组(12 组 48 队),赛程为示例。<br />所有推荐仅供研究参考,竞猜有风险。
              </div>
            </div>
          </nav>
        </aside>
        <main className="flex-1 min-w-0">
          <Outlet />
        </main>
      </div>
      <footer className="border-t border-slate-800 bg-slate-900/60 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span>⚠️</span>
            本工具仅供数据分析参考,不构成购彩建议;竞猜有风险,请理性投注。
          </div>
          <div>本页面数据基于 2026 世界杯真实分组(12 组 48 队),部分赛程为示例</div>
        </div>
      </footer>
    </div>
  );
}
