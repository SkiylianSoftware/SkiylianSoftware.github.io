"""
Compute per-video and per-game momentum (hotness) from video_history.json.

For each tracked video, looks at the last 7 / 30 / 90 days of per-day view
data and computes:
- views_7d / views_30d / views_90d: views gained in each window
- surge_pct: views_7d as percentage of total lifetime views
- trend: "rising" / "steady" / "cold"

Also aggregates per game ("most watched lately") so the Games page can
rank by recent activity.

Outputs:
- _data/video_momentum.json keyed by video_id
- _data/game_momentum.json keyed by game name

Runs after fetch_youtube_analytics.py in CI.
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

DATA_DIR = "_data"
IN_FILE = os.path.join(DATA_DIR, "video_history.json")
OUT_FILE = os.path.join(DATA_DIR, "video_momentum.json")
GAME_OUT_FILE = os.path.join(DATA_DIR, "game_momentum.json")


def _date_set(days):
    now = datetime.now(timezone.utc)
    return {((now - timedelta(days=i)).strftime("%Y-%m-%d")) for i in range(days)}


def main():
    if not os.path.exists(IN_FILE):
        print(f"  {IN_FILE} not found; skipping momentum computation")
        return

    with open(IN_FILE) as f:
        video_history = json.load(f)

    s7 = _date_set(7)
    s30 = _date_set(30)
    s90 = _date_set(90)

    out = {}
    game_agg = defaultdict(lambda: {"views_7d": 0, "views_30d": 0, "views_90d": 0, "active_videos": 0})

    for vid, vdata in video_history.items():
        daily = vdata.get("daily", {})
        total = sum(entry.get("views", 0) for entry in daily.values())
        views_7d = sum(entry.get("views", 0) for date_str, entry in daily.items() if date_str in s7)
        views_30d = sum(entry.get("views", 0) for date_str, entry in daily.items() if date_str in s30)
        views_90d = sum(entry.get("views", 0) for date_str, entry in daily.items() if date_str in s90)
        surge_pct = round(views_7d / max(1, total) * 100, 1) if total else 0.0

        if views_7d == 0 and views_30d == 0:
            trend = "cold"
        elif views_7d > 0 and views_30d > 0 and views_7d > views_30d / 4:
            trend = "rising"
        elif views_7d > 0:
            trend = "steady"
        else:
            trend = "cold"

        if views_7d > 0 or views_30d > 0 or views_90d > 0:
            out[vid] = {
                "views_7d": views_7d,
                "views_30d": views_30d,
                "views_90d": views_90d,
                "surge_pct": surge_pct,
                "trend": trend,
            }

        # Per-game aggregate
        game = vdata.get("game") or "Misc"
        g = game_agg[game]
        if views_7d > 0 or views_30d > 0:
            g["views_7d"] += views_7d
            g["views_30d"] += views_30d
            g["views_90d"] += views_90d
            g["active_videos"] += 1

    with open(OUT_FILE, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  Video momentum computed for {len(out)} videos")

    with open(GAME_OUT_FILE, "w") as f:
        json.dump(dict(game_agg), f, indent=2)
    print(f"  Game momentum computed for {len(game_agg)} games")


if __name__ == "__main__":
    main()
