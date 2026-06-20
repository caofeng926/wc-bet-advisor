"""14场胜负彩 & 任选九 search algorithm

Heuristic search:
- Main: pick highest probability each match
- Backups: for low-confidence matches, include double- or triple-pick
- 任选九: select 9 matches with largest ELO diff
"""


def lotto14_search(match_preds: list[dict], top_n: int = 7):
    """14场搜索:主注 + 6注复式

    Args:
        match_preds: list of {H: float, D: float, A: float} probability dicts

    Returns:
        (main_ticket, backup_tickets)
    """
    main = [max(["H", "D", "A"], key=lambda x: p.get(x, 0)) for p in match_preds]

    backups = []
    for b in range(6):
        picks = []
        for i, p in enumerate(match_preds):
            if (b + i) % 3 == 0:
                picks.append("HD")
            elif (b + i) % 3 == 1:
                picks.append("DA")
            else:
                picks.append(max(["H", "D", "A"], key=lambda x: p.get(x, 0)))
        backups.append(picks)

    return main, backups


def lotto9_search(match_preds: list[dict]):
    """任选九搜索:从14场选9场信心最足的

    Args:
        match_preds: list of {H: float, D: float, A: float} with optional _diff

    Returns:
        (main_ticket, backup_tickets)
    """
    # Select9 with largest H/A probability difference (most confident)
    diffs = []
    for p in match_preds:
        h = p.get("H", 0)
        a = p.get("A", 0)
        diffs.append(abs(h - a))

    # Pick 9 most confident (largest diff)
    indexed = list(enumerate(diffs))
    indexed.sort(key=lambda x: -x[1])
    selected_idxs = [i for i, _ in indexed[:9]]

    main = [max(["H", "D", "A"], key=lambda x: match_preds[i].get(x, 0))
            for i in selected_idxs]

    #3 backup tickets
    backups = []
    for b in range(3):
        picks = []
        for i in selected_idxs:
            p = match_preds[i]
            if (b + i) % 3 == 0:
                picks.append("HD")
            elif (b + i) % 3 == 1:
                picks.append("DA")
            else:
                picks.append(max(["H", "D", "A"], key=lambda x: p.get(x, 0)))
        backups.append(picks)

    return main, backups