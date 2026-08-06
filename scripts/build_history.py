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

    # Filter to start from the first analytics entry with real data to avoid a 0-value flatline
    analytics_dates = sorted([e["date"] for e in analytics if e.get("youtube_main", {}).get("subs", 0) > 0])
    if analytics_dates:
        all_dates = [d for d in all_dates if d >= analytics_dates[0]]

    # Find the LAST analytics entry with a valid Data API snapshot as anchor.
    # Walking forward from the first snapshot fails when the analytics window
    # starts mid-history, so anchor on the newest snapshot and walk backward.
    anchor = None
    for e in reversed(analytics):
        ym = e.get("youtube_main", {}) or {}
        if ym.get("subs", 0) > 0:
            anchor = {"date": e["date"], "subs": ym["subs"], "views": ym["views"]}
            break

    # Build daily entries
    entries = []
    cum_videos = 0
    last_subs = 0
    last_views = 0
    last_likes = 0
    last_comments = 0
    last_duration = 0
    hist_by_date = {e["date"]: e for e in analytics}

    # Precompute subs/views by walking backward from the anchor snapshot.
    # The anchor (newest real snapshot) includes all deltas since the start,
    # so subtracting each day's deltas reconstructs every earlier day exactly.
    subs_by_date = {}
    views_by_date = {}
    if anchor:
        running_subs = anchor["subs"]
        running_views = anchor["views"]
        anchor_dates = [d for d in all_dates if d <= anchor["date"]]
        for i in range(len(anchor_dates) - 1, -1, -1):
            d = anchor_dates[i]
            ha = hist_by_date.get(d) or {}
            an = ha.get("_analytics", {}) or {}
            subs_by_date[d] = max(0, running_subs)
            views_by_date[d] = max(0, running_views)
            # Snapshot at end of day d+1 minus day d+1's deltas gives day d
            running_subs -= an.get("subs_gained", 0) - an.get("subs_lost", 0)
            running_views -= an.get("views_gained", 0)

    for d in all_dates:
        cum_videos += video_dates.get(d, {}).get("videos", 0)

        entry = {
            "date": d,
            "youtube_main": {
                "subs": 0,
                "views": 0,
                "videos": cum_videos,
                "likes": 0,
                "comments": 0,
                "duration_seconds": 0,
            },
        }

        # Backward-walk values take precedence for every date up to the anchor
        if anchor and d in subs_by_date:
            entry["youtube_main"]["subs"] = subs_by_date[d]
            entry["youtube_main"]["views"] = views_by_date[d]

        ha = hist_by_date.get(d)
        if ha:
            ym = ha.get("youtube_main", {}) or {}
            an = ha.get("_analytics", {}) or {}
            entry["youtube_main"]["likes"] = ym.get("likes", 0)
            entry["youtube_main"]["comments"] = ym.get("comments", 0)
            entry["youtube_main"]["duration_seconds"] = ym.get("duration_seconds", 0)

            if not (anchor and d in subs_by_date):
                # No backward-walk value; use raw snapshot or carry forward
                entry["youtube_main"]["subs"] = ym.get("subs", 0) or last_subs
                entry["youtube_main"]["views"] = ym.get("views", 0) or last_views

            last_subs = entry["youtube_main"]["subs"]
            last_views = entry["youtube_main"]["views"]
            last_likes = ym.get("likes", 0)
            last_comments = ym.get("comments", 0)
            last_duration = ym.get("duration_seconds", 0)
            if an:
                entry["_analytics"] = an
            for pf in ("youtube_vods", "twitch", "github", "fourthwall"):
                if ha.get(pf):
                    entry[pf] = ha[pf]
        else:
            if not (anchor and d in subs_by_date):
                entry["youtube_main"]["subs"] = last_subs
                entry["youtube_main"]["views"] = last_views
            entry["youtube_main"]["likes"] = last_likes
            entry["youtube_main"]["comments"] = last_comments
            entry["youtube_main"]["duration_seconds"] = last_duration

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
