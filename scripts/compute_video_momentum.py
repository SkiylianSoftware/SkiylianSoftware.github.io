"""
Compute per-video momentum (hotness) from video_history.json.

For each tracked video, looks at the last 7 days of per-day view data and
computes:
- views_7d: total views gained in the last 7 days
- views_30d: total views gained in the last 30 days
- surge_pct: views_7d as percentage of total lifetime views
- trend: "rising" if 7d > 30d/4 (scaled), "peaked" if 30d much higher,
         "steady" otherwise

Output: _data/video_momentum.json keyed by video_id.

This script runs after fetch_youtube_analytics.py in CI.
"""

import json
import os
from datetime import datetime, timedelta, timezone

DATA_DIR = "_data"
IN_FILE = os.path.join(DATA_DIR, "video_history.json")
OUT_FILE = os.path.join(DATA_DIR, "video_momentum.json")


def main():
    if not os.path.exists(IN_FILE):
        print(f"  {IN_FILE} not found; skipping momentum computation")
        return

    with open(IN_FILE) as f:
        video_history = json.load(f)

    now = datetime.now(timezone.utc)

    # Walk back 7 and 30 days
    d7 = []
    for i in range(7):
        d = now - timedelta(days=i)
        d7.append(d.strftime("%Y-%m-%d"))
    d30 = []
    for i in range(30):
        d = now - timedelta(days=i)
        d30.append(d.strftime("%Y-%m-%d"))

    s7 = set(d7)
    s30 = set(d30)

    out = {}
    for vid, vdata in video_history.items():
        daily = vdata.get("daily", {})
        views_7d = sum(entry.get("views", 0) for date_str, entry in daily.items() if date_str in s7)
        views_30d = sum(entry.get("views", 0) for date_str, entry in daily.items() if date_str in s30)
        total = sum(entry.get("views", 0) for entry in daily.values())
        surge_pct = round(views_7d / max(1, total) * 100, 1) if total else 0.0

        # Trend classification
        if views_7d == 0 and views_30d == 0:
            trend = "cold"
        elif views_7d > 0 and views_30d > 0 and views_7d > views_30d / 4:
            trend = "rising"
        elif views_7d > 0:
            trend = "steady"
        else:
            trend = "cold"

        if views_7d > 0 or views_30d > 0:
            out[vid] = {
                "views_7d": views_7d,
                "views_30d": views_30d,
                "surge_pct": surge_pct,
                "trend": trend,
            }

    with open(OUT_FILE, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  Video momentum computed for {len(out)} videos")


if __name__ == "__main__":
    main()
