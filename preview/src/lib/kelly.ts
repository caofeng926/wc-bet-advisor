export function kellyFraction(p: number, odds: number): number {
  if (p <= 0 || p >= 1 || odds <= 1) return 0;
  const b = odds - 1;
  const q = 1 - p;
  return (b * p - q) / b;
}

export interface StakeSuggestion {
  stake: number;
  ev: number;
  winProfit: number;
  loseLoss: number;
  kelly: number;
}

export function suggestStake(
  bankroll: number,
  p: number,
  odds: number,
  kellyMult = 0.25
): StakeSuggestion {
  const k = Math.max(0, kellyFraction(p, odds));
  const f = Math.min(k * kellyMult, 0.05);
  const stake = +(bankroll * f).toFixed(2);
  const winProfit = +(stake * (odds - 1)).toFixed(2);
  const loseLoss = -stake;
  const ev = +(p * winProfit + (1 - p) * loseLoss).toFixed(2);
  return { stake, ev, winProfit, loseLoss, kelly: k };
}
