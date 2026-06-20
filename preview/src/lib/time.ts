export function formatHMS(totalSeconds: number): string {
  if (totalSeconds < 0) totalSeconds = 0;
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  return [h, m, s].map((n) => n.toString().padStart(2, "0")).join(":");
}

export function minutesToClose(target: Date | string): number {
  const t = typeof target === "string" ? new Date(target) : target;
  return Math.floor((t.getTime() - Date.now()) / 60000);
}

export function countdownColor(seconds: number): "green" | "yellow" | "red" | "gray" {
  if (seconds <= 0) return "gray";
  if (seconds < 1800) return "red";
  if (seconds < 7200) return "yellow";
  return "green";
}

export function formatDateZh(d: Date | string): string {
  const t = typeof d === "string" ? new Date(d) : d;
  const mm = (t.getMonth() + 1).toString().padStart(2, "0");
  const dd = t.getDate().toString().padStart(2, "0");
  const hh = t.getHours().toString().padStart(2, "0");
  const min = t.getMinutes().toString().padStart(2, "0");
  return `${mm}-${dd} ${hh}:${min}`;
}
