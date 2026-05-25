import json
import os

DATA_DIR = "_data"
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


def read_json(name):
    p = os.path.join(DATA_DIR, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def main():
    yt_main = read_json("youtube_main.json") or {}
    analytics = read_json("history.json") or []

    debug = os.environ.get("DEBUG") == "1"

    # Collect all dates with video publishes
    video_dates = {}
    for v in yt_main.get("videos", []):
        pub = (v.get("published") or "")[:10]
        if pub:
            video_dates.setdefault(pub, {"videos": 0, "views": 0})
            video_dates[pub]["videos"] += 1
            video_dates[pub]["views"] += v.get("view_count", 0)

    all_dates = sorted(set(list(video_dates.keys()) + [e["date"] for e in analytics]))
    if not all_dates:
        print("No data to build history from")
        return

    # Build daily entries
    entries = []
    cum_videos = 0
    cum_views = 0
    hist_by_date = {e["date"]: e for e in analytics}

    for d in all_dates:
        cum_videos += video_dates.get(d, {}).get("videos", 0)
        cum_views += video_dates.get(d, {}).get("views", 0)

        entry = {"date": d, "youtube_main": {"subs": 0, "views": 0, "videos": cum_videos}}

        # Overlay analytics data if available
        ha = hist_by_date.get(d)
        if ha:
            ym = ha.get("youtube_main", {}) or {}
            an = ha.get("_analytics", {}) or {}
            entry["youtube_main"]["subs"] = ym.get("subs", 0)
            entry["youtube_main"]["views"] = ym.get("views", 0)
            if an:
                entry["_analytics"] = an

        # Always ensure videos count is accurate (analytics has videos=0)
        if entry["youtube_main"]["videos"] == 0 and cum_videos > 0:
            entry["youtube_main"]["videos"] = cum_videos

        entries.append(entry)

    if debug:
        print(f"  History built: {len(entries)} entries")
        print(f"  First: {entries[0]['date']} - {entries[0]['youtube_main']}")
        print(f"  Last:  {entries[-1]['date']} - {entries[-1]['youtube_main']}")
        print("  Sample dates with video counts:")
        for e in entries:
            if e["youtube_main"]["videos"] > 0:
                print(f"    {e['date']}: {e['youtube_main']}")
                break
        print("  All dates with video count changes:")
        last_v = -1
        for e in entries:
            if e["youtube_main"]["videos"] != last_v:
                vm = e["youtube_main"]
                print(f"    {e['date']}: subs={vm['subs']} views={vm['views']} videos={vm['videos']}")
                last_v = e["youtube_main"]["videos"]

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(entries, f, indent=2)
    print(f"Written {HISTORY_FILE} ({len(entries)} entries)")


if __name__ == "__main__":
    main()
