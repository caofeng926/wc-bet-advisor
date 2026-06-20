import ast, os, sys

ws = r"C:\Users\win\Documents\2026世界杯体彩竞猜"

def read(p):
    with open(p, encoding="utf-8-sig") as f:
        return f.read()

def check_py(rel):
    p = os.path.join(ws, rel)
    if not os.path.exists(p):
        return f"MISSING: {rel}"
    try:
        ast.parse(read(p))
        return f"OK   : {rel} ({len(read(p))} chars)"
    except SyntaxError as e:
        return f"ERR  : {rel} - {e}"

def check_tsx(rel, expect_symbols):
    p = os.path.join(ws, rel)
    if not os.path.exists(p):
        return [f"MISSING: {rel}"]
    content = read(p)
    out = []
    for sym in expect_symbols:
        if sym in content:
            out.append(f"  found  : {sym}")
        else:
            out.append(f"  MISSING: {sym}")
    return [f"CHECK : {rel}"] + out

print("=== Python syntax ===")
for f in [
    "backend/app/api/football.py",
    "backend/app/db/schemas.py",
    "backend/tests/test_football_today.py",
]:
    print(check_py(f))

print("\n=== Frontend content checks ===")
for f, symbols in [
    ("preview/src/components/TodayPicks.tsx",
     ["FootballTodayBest", "FootballTodayMatch", "FootballTodayOut",
      "source === \"offline\"", "best_crs", "best_ttg", "best_hafu",
      "ProbabilityBar", "ValueBadge", "getFootballToday"]),
    ("preview/src/lib/api.ts",
     ["FootballTodayBest", "FootballTodayMatch", "FootballTodayOut",
      "getFootballToday", "fetched_at", "source"]),
    ("preview/src/pages/Dashboard.tsx",
     ["TodayPicks", "import Guide", "import TodayPicks"]),
]:
    for line in check_tsx(f, symbols):
        print(line)

print("\n=== Schema symbol cross-check ===")
schemas = read(os.path.join(ws, "backend/app/db/schemas.py"))
for sym in ["FootballTodayBest", "FootballTodayMatch", "FootballTodayOut",
            "CrsRecommendOut", "TtgRecommendOut", "HafuRecommendOut"]:
    print(f"  schemas.{sym}: {'OK' if sym in schemas else 'MISSING'}")
