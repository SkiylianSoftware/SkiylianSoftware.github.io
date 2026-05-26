import json
import os
from datetime import datetime, timedelta, timezone

DATA_DIR = "_data"
MILESTONES_FILE = os.path.join(DATA_DIR, "milestones.json")

P3 = [3**i for i in range(13)]
P2 = [2**i for i in range(21)]
RND = [1, 10, 25, 50, 100, 250, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
P3_MSG = {
    1: "The unitary state",
    3: "Three-body problem solved",
    9: "Nonary game complete",
    27: "Cube it!",
    81: "Trit-trit-trit!",
    243: "3^5 - Fifth power unlocked",
    729: "3^6 - One gross in balanced ternary",
    2187: "3^7 - Lucky sevens",
    6561: "3^8 - Octotrit",
    19683: "3^9 - Padovan sequence spotted",
    59049: "3^10 - Decitrit! Tenfold power!",
    177147: "3^11 - Ternary galaxy!",
    531441: "3^12 - Dozenal trit!",
}
P2_MSG = {
    2: "A pair!",
    4: "Four! Quadbit!",
    8: "Byte!",
    16: "Half-word!",
    32: "Word!",
    64: "Double-word!",
    128: "Kilobit!",
    256: "Byte plural!",
    512: "Half a K!",
    1024: "1K! A true kilobyte!",
    2048: "2K!",
    4096: "4K! Page boundary!",
    8192: "8K!",
    16384: "16K!",
    32768: "Half of 64K!",
    65536: "64K! Full address space!",
    131072: "128K! Expanded memory!",
    262144: "256K! High memory area!",
    524288: "512K! Extended memory!",
    1048576: "1M! Megabyte territory!",
}
RND_MSG = {
    10: "First double digits!",
    50: "Halfway to 100!",
    100: "Triple digits!",
    500: "Half a thousand!",
    1000: "The big 1K!",
    5000: "5K strong!",
    10000: "10K! Unreal!",
    50000: "50K! Halfway to 100K!",
    100000: "100K!!! Thank you!",
    500000: "Half a million!",
    1000000: "1 MILLION! Unbelievable!",
}


def _fmt(m, b):
    return f"{m:,}: {b}" if b else f"{m:,} units!"


FMT = _fmt

MILESTONE_SPECS = [
    ("subs", P3, P3_MSG, FMT),
    ("subs", P2, P2_MSG, FMT),
    ("subs", RND, RND_MSG, FMT),
    ("views", P3, P3_MSG, FMT),
    ("views", P2, P2_MSG, FMT),
    ("views", RND, RND_MSG, FMT),
    ("videos", P3, P3_MSG, FMT),
    ("videos", P2, P2_MSG, FMT),
    ("videos", RND, RND_MSG, FMT),
]

GAME_EP_THRESH = sorted(set(P3 + P2 + RND))
STREAK_THRESH = sorted([4, 8, 13, 26, 52, 104])
HOURS_THRESH = sorted(set(P3 + P2 + RND))
VIDEO_FIRST_THRESH = sorted([m for m in set(P3 + RND) if m >= 100])

GAME_DEFAULT = {
    "ep": "{{m}} episodes in {game}!",
    "views": "{{count}} views across {game}!",
    "hours": "{{hours}} hours in {game}!",
    "return": "Back to {game} after {{days}} days!",
}
GAME_OVERRIDES = {
    "Kerbal Space Program": {
        "ep": {
            1: "First launch at KSC!",
            2: "Orbit achieved!",
            3: "Munar flyby complete!",
            4: "Sub-orbital tourism!",
            8: "Minmus landing!",
            9: "Duna transfer!",
            10: "Duna landing!",
            16: "Interplanetary fleet!",
            25: "Jool arrival!",
            27: "Jool system fleet!",
            32: "Eeloo reached!",
            50: "Across the solar system!",
            64: "Space station network!",
            81: "Across the galaxy!",
            100: "Century of launches!",
        }
    },
    "Factorio": {
        "ep": {
            3: "Green science automated!",
            9: "Blue science online!",
            27: "Rocket silo constructed!",
            81: "Mega base operational!",
        }
    },
    "Minecraft": {
        "ep": {
            3: "Nether portal activated!",
            9: "Stronghold located!",
            27: "Ender Dragon defeated!",
            81: "Full beacon pyramid!",
        }
    },
    "Transport Fever": {
        "ep": {
            3: "Three lines running!",
            9: "Train network growing!",
            27: "Maglev network online!",
            81: "Transcontinental empire!",
        }
    },
    "Transport Fever 2": {
        "ep": {
            3: "Three lines running!",
            9: "Train network growing!",
            27: "Maglev network online!",
            81: "Transcontinental empire!",
        }
    },
    "Mars First Logistics": {
        "ep": {3: "Rover delivered!", 9: "Base camp established!", 27: "Three colonies linked!", 81: "Martian city!"}
    },
    "Station Flow": {
        "ep": {3: "Queue managed!", 9: "Station bustling!", 27: "Expansion complete!", 81: "Metroplex achieved!"}
    },
}


def read_json(name):
    p = os.path.join(DATA_DIR, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def first_date_from_history(history, label, threshold):
    """Return the first date in history where label >= threshold."""
    for entry in history:
        ym = entry.get("youtube_main", {}) or {}
        if ym.get(label, 0) >= threshold:
            return entry["date"]
    return None


def main():
    history = read_json("history.json") or []
    site_meta = read_json("site_meta.json") or {}
    yt_main = read_json("youtube_main.json") or {}

    debug = os.environ.get("DEBUG") == "1"
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    # Current values
    subs = site_meta.get("subscriber_count", 0)
    views = site_meta.get("view_count", 0)
    videos_count = site_meta.get("video_count", 0)

    # Load previous milestones for comparison
    prev = read_json("milestones.json") or {}
    prev_reached = prev.get("reached", {})
    new_reached = {}

    if debug:
        print(f"  Current: {subs} subs, {views} views, {videos_count} videos")
        print(
            f"  History: {len(history)} entries ({history[0]['date']} to {history[-1]['date']})"
            if history
            else "  History: empty"
        )

    # Process standard milestones (subs, views, videos)
    # Collect ALL thresholds (no break), then collapse same-label same-date later
    for label, thresholds, _msgs, _formatter in MILESTONE_SPECS:
        value = {"subs": subs, "views": views, "videos": videos_count}.get(label, 0)
        for m in sorted(thresholds, reverse=True):
            if value >= m:
                key = f"{label}_{m}"
                date = first_date_from_history(history, label, m)
                if not date and label == "videos":
                    dates = sorted(
                        [v.get("published", "")[:10] for v in yt_main.get("videos", []) if v.get("published")]
                    )
                    if len(dates) >= m:
                        date = dates[m - 1]
                if not date:
                    date = today
                new_reached[key] = date

    # Process game milestones from per-video cumulative data
    all_videos = yt_main.get("videos", [])
    game_cumulative = {}
    for v in all_videos:
        s = v.get("series", {})
        gname = (s or {}).get("game", "")
        pub = v.get("published", "")[:10]
        if gname and pub:
            game_cumulative.setdefault(gname, []).append(pub)

    for gname, video_dates in game_cumulative.items():
        video_dates.sort()
        ep_count = len(video_dates)

        # Episode milestones (from video publish dates)
        for m in sorted(GAME_EP_THRESH, reverse=True):
            if ep_count >= m:
                key = f"game_{gname}_ep_{m}"
                date = video_dates[m - 1]
                new_reached[key] = date

        # Return milestones (longest gap between consecutive videos)
        if len(video_dates) >= 2:
            try:
                dates_dt = sorted(datetime.strptime(d, "%Y-%m-%d") for d in video_dates)
                max_gap = 0
                gap_end_idx = 0
                for i in range(len(dates_dt) - 1):
                    gap = (dates_dt[i + 1] - dates_dt[i]).days
                    if gap > max_gap:
                        max_gap = gap
                        gap_end_idx = i + 1
                gap = max_gap
                gap_end = video_dates[gap_end_idx]
                key = f"game_{gname}_return_{gap}"
                new_reached[key] = gap_end
            except Exception:
                pass

    # Per-game view/hour milestones from video_history.json (YouTube Analytics API)
    video_history = read_json("video_history.json") or {}
    if video_history:
        # Build game -> [video_id] mapping
        game_videos = {}
        for v in all_videos:
            vid = v.get("video_id", "")
            s = v.get("series", {})
            gname = (s or {}).get("game", "")
            if gname and vid and vid in video_history:
                game_videos.setdefault(gname, []).append(vid)
            elif gname and vid:
                # Video in youtube_main but not yet in video_history; seed with current views
                game_videos.setdefault(gname, [])
                game_videos[gname].append(vid)

        game_view_thresh = [m for m in GAME_EP_THRESH if m >= 9]
        game_hour_thresh = [m for m in GAME_EP_THRESH if m >= 3]

        for gname, vids in game_videos.items():
            # Collect all dates from video_history for this game's videos
            date_views = {}
            for vid in vids:
                vh = video_history.get(vid, {})
                daily = vh.get("daily", {})
                for d, dv in daily.items():
                    date_views.setdefault(d, 0)
                    date_views[d] += dv.get("views", 0)

            if not date_views:
                continue

            sorted_dates = sorted(date_views.keys())

            # View milestones
            for m in sorted(game_view_thresh, reverse=True):
                found_date = None
                run_views = 0
                for d in sorted_dates:
                    run_views += date_views[d]
                    if run_views >= m:
                        found_date = d
                        break
                if found_date:
                    key = f"game_{gname}_views_{m}"
                    new_reached[key] = found_date

            # Hour milestones (watch_time is in minutes from analytics; convert to hours)
            date_watch = {}
            for d in sorted_dates:
                total_watch = 0
                for vid in vids:
                    vh = video_history.get(vid, {})
                    dd = vh.get("daily", {}).get(d, {})
                    total_watch += dd.get("watch_time", 0)
                date_watch[d] = total_watch // 60  # minutes to hours

            for m in sorted(game_hour_thresh, reverse=True):
                found_date = None
                run_hours = 0
                for d in sorted_dates:
                    run_hours += date_watch.get(d, 0)
                    if run_hours >= m:
                        found_date = d
                        break
                if found_date:
                    key = f"game_{gname}_hours_{m}"
                    new_reached[key] = found_date

    # Age milestone
    first_video_date = None
    for v in all_videos:
        pub = (v.get("published") or "")[:10]
        if pub and (first_video_date is None or pub < first_video_date):
            first_video_date = pub
    if first_video_date:
        fd = datetime.strptime(first_video_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        age_days = (now - fd).days
        for m in [3, 9, 27, 81, 243, 729, 2187, 6561]:
            if age_days >= m:
                key = f"age_{m}"
                age_date = (fd + timedelta(days=m)).strftime("%Y-%m-%d")
                new_reached[key] = age_date

    # Channel hiatus milestone (longest gap between any two video uploads)
    if len(all_videos) >= 2:
        hiatus_dates = sorted(set(v.get("published", "")[:10] for v in all_videos if v.get("published")))
        if len(hiatus_dates) >= 2:
            hiatus_dt = [datetime.strptime(d, "%Y-%m-%d") for d in hiatus_dates]
            max_gap = 0
            gap_end = None
            for i in range(len(hiatus_dt) - 1):
                gap = (hiatus_dt[i + 1] - hiatus_dt[i]).days
                if gap > max_gap:
                    max_gap = gap
                    gap_end = hiatus_dates[i + 1]
            if max_gap > 0 and gap_end:
                key = f"hiatus_{max_gap}"
                new_reached[key] = gap_end

    # Weekly upload streak (consecutive calendar weeks with at least one upload)
    if len(all_videos) >= 2:
        all_date_set = sorted(set(v.get("published", "")[:10] for v in all_videos if v.get("published")))
        if len(all_date_set) >= 2:
            week_dates = {}
            for d in all_date_set:
                dt = datetime.strptime(d, "%Y-%m-%d")
                iso = dt.isocalendar()
                wk = iso[0] * 100 + iso[1]
                week_dates.setdefault(wk, []).append(d)
            sorted_weeks = sorted(week_dates.keys())
            longest = 0
            cur = 0
            streak_end = None
            for i, wk in enumerate(sorted_weeks):
                if i == 0 or wk - sorted_weeks[i - 1] != 1:
                    cur = 1
                else:
                    cur += 1
                if cur > longest:
                    longest = cur
                    streak_end = max(week_dates[wk])
            if longest >= 2:
                for m in sorted(STREAK_THRESH, reverse=True):
                    if longest >= m:
                        key = f"streak_{m}"
                        new_reached[key] = streak_end

    # Video linking metadata stored alongside milestones
    milestone_links = {}

    # First video to reach N views (from video_history.json)
    if video_history and all_videos:
        vid_map = {}
        for v in all_videos:
            vid_map[v.get("video_id", "")] = v
        for m in sorted(VIDEO_FIRST_THRESH, reverse=True):
            best_date = None
            best_vid = None
            for vid, vh in video_history.items():
                daily = vh.get("daily", {})
                if not daily:
                    continue
                sd = sorted(daily.keys())
                cum = 0
                for d in sd:
                    cum += daily[d].get("views", 0)
                    if cum >= m:
                        if best_date is None or d < best_date:
                            best_date = d
                            best_vid = vid
                        break
            if best_date and best_vid:
                key = f"video_first_{m}"
                new_reached[key] = best_date
                vi = vid_map.get(best_vid, {})
                title = vi.get("title", video_history.get(best_vid, {}).get("title", ""))
                milestone_links[key] = {"url": f"/videos#vid-{best_vid}", "text": title}

    # Total watch time (hours) from video_history.json
    if video_history:
        daily_hours = {}
        for _vid, vh in video_history.items():
            for d, dv in vh.get("daily", {}).items():
                daily_hours.setdefault(d, 0)
                daily_hours[d] += dv.get("watch_time", 0) // 60
        if daily_hours:
            sorted_dates = sorted(daily_hours.keys())
            for m in sorted(HOURS_THRESH, reverse=True):
                cum = 0
                for d in sorted_dates:
                    cum += daily_hours[d]
                    if cum >= m:
                        key = f"hours_{m}"
                        new_reached[key] = d
                        break

    # Collapse milestones: for each label, keep only the highest threshold per date
    def collapse_key(key):
        return key.rsplit("_", 1)[0]

    def threshold_val(key):
        return int(key.rsplit("_", 1)[1])

    collapsed = {}
    groups = {}
    for key, date in new_reached.items():
        groups.setdefault((collapse_key(key), date), []).append(key)
    for (_, date), keys in groups.items():
        best = max(keys, key=threshold_val)
        collapsed[best] = date
    new_reached = collapsed

    for key, date in new_reached.items():
        if key not in prev_reached:
            parts = key.rsplit("_", 1)
            m = int(parts[1])
            if key.startswith("age_"):
                print(f"  New milestone: {m} days old (date={date})")
            elif key.startswith("hiatus_"):
                print(f"  New milestone: returned after hiatus of {m} days (date={date})")
            elif key.startswith("streak_"):
                print(f"  New milestone: {m} week upload streak (date={date})")
            elif key.startswith("video_first_"):
                link = milestone_links.get(key, {})
                title = link.get("text", "")
                print(f"  New milestone: first video to {m:,} views (date={date}) - {title}")
            elif key.startswith("hours_"):
                print(f"  New milestone: {m:,} total channel hours (date={date})")
            elif key.startswith("game_"):
                rest = key[len("game_") :]
                if "_ep_" in rest:
                    g, _, n = rest.partition("_ep_")
                    print(f"  New milestone: {n} episodes in {g} (date={date})")
                elif "_views_" in rest:
                    g, _, n = rest.partition("_views_")
                    print(f"  New milestone: {n} views across {g} (date={date})")
                elif "_hours_" in rest:
                    g, _, n = rest.partition("_hours_")
                    print(f"  New milestone: {n} hours in {g} (date={date})")
                elif "_return_" in rest:
                    g, _, n = rest.partition("_return_")
                    print(f"  New milestone: Back to {g} after {n} days (date={date})")
            else:
                print(f"  New milestone: {m:,} {parts[0]} (date={date})")

    # Sort milestones: descending by date, then by threshold descending within same date
    def sort_key(item):
        key, date = item
        parts = key.rsplit("_", 1)
        threshold = int(parts[-1]) if parts[-1].isdigit() else 0
        return (date, threshold)

    if debug:
        print(f"\n  Milestones detected: {len(new_reached)}")
        for k, v in sorted(new_reached.items(), key=sort_key, reverse=True)[:15]:
            print(f"    {k}: {v}")
        if len(new_reached) > 15:
            print(f"    ... and {len(new_reached) - 15} more")

    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    sorted_reached = dict(sorted(new_reached.items(), key=sort_key, reverse=True))
    result = {"current": {}, "reached": sorted_reached}
    if milestone_links:
        result["links"] = milestone_links
    with open(MILESTONES_FILE, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Written {MILESTONES_FILE} ({len(new_reached)} milestones)")


if __name__ == "__main__":
    main()
