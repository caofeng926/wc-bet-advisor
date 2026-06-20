import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import MatchDetail from "./pages/MatchDetail";
import Lotto14 from "./pages/Lotto14";
import ParlayBuilder from "./pages/ParlayBuilder";
import ScoreRecommend from "./pages/ScoreRecommend";
import TotalGoalsRecommend from "./pages/TotalGoalsRecommend";
import HtftRecommend from "./pages/HtftRecommend";
import Slips from "./pages/Slips";
import ChampionRecommend from "./pages/ChampionRecommend";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/matches/:id" element={<MatchDetail />} />
        <Route path="/lotto14" element={<Lotto14 />} />
        <Route path="/parlay" element={<ParlayBuilder />} />
        <Route path="/score" element={<ScoreRecommend />} />
        <Route path="/total" element={<TotalGoalsRecommend />} />
        <Route path="/htft" element={<HtftRecommend />} />
        <Route path="/slips" element={<Slips />} />
        <Route path="/champion" element={<ChampionRecommend />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
