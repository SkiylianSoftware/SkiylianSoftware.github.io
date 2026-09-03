"""
Compute "next milestone" predictions for the dashboard.

For each tracked metric (subscribers, views, comments, videos) this:
  - picks the NEXT threshold above the current value, mixing Skye's
    balanced-ternary milestones (3^n) with round numbers
  - estimates the achievement date using the FULL history dataset but with
    recent days weighted higher (exponential decay), so the pace reflects
    current momentum rather than a flat 30-day slice

History comes from history.json (cumulative per-platform values). Writes
_data/future_milestones.json which the dashboard renders as colour-coded
cards.
"""

import json
import math
import os
from datetime import datetime, timedelta, timezone

DATA_DIR = "_data"
OUT_FILE = os.path.join(DATA_DIR, "future_milestones.json")

# Candidate thresholds per metric: balanced ternary (3^n) + round numbers.
# Mixed deliberately, e.g. subs 61 -> 81 then 100 then 243...
NEWTON_DECAY_DAYS = 60.0  # weight halves roughly every ~42 days

POWERS_OF_THREE = [3**n for n in range(1, 16)]  # 3, 9, 27, 81, 243, ...

ROUND_SUBS = [100 * m for m in range(1, 101)]
ROUND_VIEWS = [
    int(r)
    for r in (
        50,
        100,
        250,
        500,
        1000,
        2500,
        5000,
        10000,
        25000,
        50000,
        100000,
        250000,
        500000,
        1000000,
    )
]
ROUND_COMMENTS = [50 * m for m in range(1, 101)]
ROUND_VIDEOS = [50 * m for m in range(1, 101)]


def read_json(name):
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def candidates(round_nums):
    all_ = set(POWERS_OF_THREE) | set(round_nums)
    return sorted(t for t in all_ if t >= 10)


def next_threshold(current, round_nums):
    for t in candidates(round_nums):
        if t > current:
            return t
    return None


def weighted_rate(dates, values):
    """Per-day growth from the whole series, decay-weighted toward recent.

    Returns (slope_per_day, confidence) or (None, 0) if not significant.
    Values are cumulative; we fit against the number of days from the latest
    point so older points carry exponentially less weight.
    """
    n = len(dates)
    if n < 2:
        return None, 0.0
    base = dates[-1]
    xs = [(base - dates[i]).days for i in range(n)]  # 0 = latest, grows negative
    ys = [values[i] for i in range(n)]

    weights = [math.exp(x / NEWTON_DECAY_DAYS) for x in xs]  # exp(-|x|/decay)

    wsum = sum(weights)
    if wsum <= 0:
        return None, 0.0
    xbar = sum(w * x for w, x in zip(weights, xs, strict=True)) / wsum
    ybar = sum(w * y for w, y in zip(weights, ys, strict=True)) / wsum
    denom = sum(w * (x - xbar) ** 2 for w, x in zip(weights, xs, strict=True))
    if abs(denom) < 1e-9:
        return None, 0.0
    slope = sum(w * (x - xbar) * (y - ybar) for w, x, y in zip(weights, xs, ys, strict=True)) / denom
    if not math.isfinite(slope):
        return None, 0.0
    return slope, min(1.0, wsum / max(1, n))


def eta_date(current, target, rate):
    if rate <= 0:
        return None
    days = (target - current) / rate
    if days <= 0:
        return None
    return datetime.now(timezone.utc) + timedelta(days=days)


def main():
    history = read_json("history.json") or []
    if not history:
        print("No history data; skipping future milestone ETA computation")
        return

    def series(field):
        dates, values = [], []
        for e in history:
            ym = e.get("youtube_main") or {}
            if field not in ym:
                continue
            d = e.get("date")
            if not d:
                continue
            dates.append(datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc))
            values.append(ym[field])
        if not dates:
            return [], []
        order = sorted(range(len(dates)), key=lambda i: dates[i])
        return [dates[i] for i in order], [values[i] for i in order]

    spec = {
        "subs": ("subscriber_count", ROUND_SUBS),
        "views": ("view_count", ROUND_VIEWS),
        "comments": ("comment_count", ROUND_COMMENTS),
        "videos": ("video_count", ROUND_VIDEOS),
    }

    meta = read_json("site_meta.json") or {}
    out = {}
    for key, (field, rounds) in spec.items():
        cur = meta.get(field)
        if cur is None:
            dates, values = series(field)
            cur = values[-1] if values else 0
        dates, values = series(field)
        nxt = next_threshold(int(cur or 0), rounds)
        rate, conf = weighted_rate(dates, values) if len(dates) >= 2 else (None, 0.0)
        entry = {"current": int(cur or 0), "next": nxt, "rate": None, "eta": None}
        if nxt:
            eta = eta_date(int(cur or 0), nxt, rate) if rate else None
            if eta:
                entry["eta"] = eta.strftime("%Y-%m-%d")
                entry["rate"] = round(rate, 3)
        out[key] = entry
        print(f"  {key}: current={entry['current']} next={nxt} rate={rate and round(rate, 3)} eta={entry['eta']}")

    with open(OUT_FILE, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
