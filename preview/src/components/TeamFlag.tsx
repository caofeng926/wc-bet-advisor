import { flagUrl } from "../lib/flags";

interface Props {
  iso3: string;
  name_zh: string;
  size?: "sm" | "md" | "lg";
  showName?: boolean;
}

export default function TeamFlag({ iso3, name_zh, size = "md", showName = true }: Props) {
  const dim = size === "sm" ? "w-5 h-4" : size === "lg" ? "w-12 h-9" : "w-8 h-6";
  const text = size === "sm" ? "text-xs" : size === "lg" ? "text-base" : "text-sm";
  return (
    <span className="inline-flex items-center gap-1.5">
      <img
        src={flagUrl(iso3)}
        alt={name_zh}
        title={name_zh}
        className={`${dim} rounded-sm object-cover border border-slate-700 shadow-sm`}
        loading="lazy"
      />
      {showName && <span className={text}>{name_zh}</span>}
    </span>
  );
}
