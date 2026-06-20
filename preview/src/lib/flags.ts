// flagcdn.com 公开 CDN,支持所有 ISO 3166-1 alpha-2 国家代码
// URL 格式:https://flagcdn.com/w80/{iso2}.png
const ISO2_MAP: Record<string, string> = {
  // 东道主
  USA: "us", CAN: "ca", MEX: "mx",
  // 2026 世足 48 强(按组)
  RSA: "za", KOR: "kr", DEN: "dk",                // A
  ESP: "es", JPN: "jp", AUS: "au", QAT: "qa",    // B (QAT 实际是 B 组)
  BRA: "br", MAR: "ma", NOR: "no", PAN: "pa",    // C
  URU: "uy", PAR: "py", KSA: "sa", CRO: "hr",    // D
  GER: "de", TUN: "tn", CUW: "cw", NZL: "nz",    // E
  ARG: "ar", ALG: "dz", AUT: "at", JOR: "jo",    // F
  FRA: "fr", SEN: "sn", GHA: "gh", HON: "hn",    // G
  ENG: "gb", EGY: "eg", IRN: "ir", CPV: "cv",    // H
  POR: "pt", CIV: "ci", UZB: "uz", BOL: "bo",    // I
  NED: "nl", SUI: "ch", ECU: "ec", PER: "pe",    // J (Netherlands)
  BEL: "be", SUI2: "ch", CRC: "cr", SRB: "rs",  // K (瑞士重复,换塞尔维亚)
  ITA: "it", POL: "pl", CZE: "cz", UKR: "ua",   // L
  // 之前的老数据保留
  WAL: "gb", SCO: "gb", NIR: "gb", CMR: "cm",
  GER2: "de", IRL: "ie", COL: "co", CHI: "cl",
  VEN: "ve", ISL: "is", NIR2: "gb", NGA: "ng",
  TUN2: "tn", EGY2: "eg", KOR2: "kr", CHN: "cn",
  IRQ: "iq", UAE: "ae", ETH: "et", MAR2: "ma",
  ALG2: "dz", RSA2: "za", MAR3: "ma", TUN3: "tn",
};

// 简单匹配:如果直接映射不存在,就用 ISO3 前两位
export function flagUrl(iso3: string): string {
  const code = ISO2_MAP[iso3] || iso3.slice(0, 2).toLowerCase();
  return `https://flagcdn.com/w80/${code}.png`;
}
