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
GAME_VIEW_THRESH = [m for m in GAME_EP_THRESH if m >= 9]
GAME_HOUR_THRESH = [m for m in GAME_EP_THRESH if m >= 3]
GAME_RETURN_THRESH = [m for m in GAME_EP_THRESH if m >= 27]

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
    for label, thresholds, msgs, formatter in MILESTONE_SPECS:
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

                if key not in prev_reached:
                    msg = formatter(m, msgs.get(m, ""))
                    print(f"  New milestone: {msg} (date={date})")
                elif prev_reached.get(key, "").startswith(today):
                    # Was previously set to today - update to real date
                    pass  # date is already set correctly above

                new_reached[key] = date
                break

    # Process game milestones from per-video cumulative data
    all_videos = yt_main.get("videos", [])
    game_cumulative = {}
    for v in all_videos:
        s = v.get("series", {})
        gname = (s or {}).get("game", "")
        pub = v.get("published", "")[:10]
        views = v.get("view_count", 0) or 0
        hours = (v.get("duration_seconds", 0) or 0) // 3600
        if gname and pub:
            game_cumulative.setdefault(gname, []).append((pub, views, hours))

    for gname, videos_list in game_cumulative.items():
        videos_list.sort(key=lambda x: x[0])
        ep_count = len(videos_list)

        # Episode milestones (from video publish dates)
        for m in sorted(GAME_EP_THRESH, reverse=True):
            if ep_count >= m:
                key = f"game_{gname}_ep_{m}"
                date = videos_list[m - 1][0]
                override = GAME_OVERRIDES.get(gname, {}).get("ep", {}).get(m)
                msg = override or GAME_DEFAULT["ep"].replace("{game}", gname).replace("{{m}}", str(m))
                if key not in prev_reached:
                    print(f"  New game milestone: {msg} (date={date})")
                new_reached[key] = date
                break

        # View milestones: find first video where cumulative views >= threshold
        for m in sorted(GAME_VIEW_THRESH, reverse=True):
            found_date = None
            running = 0
            for pub, vv, _ in videos_list:
                running += vv
                if running >= m:
                    found_date = pub
                    break
            if found_date:
                key = f"game_{gname}_views_{m}"
                msg = GAME_DEFAULT["views"].replace("{game}", gname).replace("{{count}}", str(m))
                if key not in prev_reached:
                    print(f"  New game milestone: {msg} (date={found_date})")
                new_reached[key] = found_date

        # Hour milestones: find first video where cumulative hours >= threshold
        for m in sorted(GAME_HOUR_THRESH, reverse=True):
            found_date = None
            running = 0
            for pub, _, hh in videos_list:
                running += hh
                if running >= m:
                    found_date = pub
                    break
            if found_date:
                key = f"game_{gname}_hours_{m}"
                msg = GAME_DEFAULT["hours"].replace("{game}", gname).replace("{{hours}}", str(m))
                if key not in prev_reached:
                    print(f"  New game milestone: {msg} (date={found_date})")
                new_reached[key] = found_date

        # Return milestones
        if len(videos_list) >= 2:
            first = videos_list[0][0]
            latest = videos_list[-1][0]
            try:
                fd = datetime.strptime(first, "%Y-%m-%d")
                ld = datetime.strptime(latest, "%Y-%m-%d")
                gap = (ld - fd).days
                for m in sorted(GAME_RETURN_THRESH, reverse=True):
                    if gap >= m:
                        key = f"game_{gname}_return_{m}"
                        msg = GAME_DEFAULT["return"].replace("{game}", gname).replace("{{days}}", str(m))
                        if key not in prev_reached:
                            print(f"  New game milestone: {msg} (date={latest})")
                        new_reached[key] = latest
                        break
            except Exception:
                pass

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
                date = fd.strftime("%Y-%m-%d")  # channel reached m days old on that date
                # Actually: channel age m = first_video + m days
                age_date = (fd + timedelta(days=m)).strftime("%Y-%m-%d")
                if key not in prev_reached:
                    print(f"  New age milestone: {m} days old (date={age_date})")
                new_reached[key] = age_date
                break

    if debug:
        print(f"\n  Milestones detected: {len(new_reached)}")
        for k, v in sorted(new_reached.items())[:15]:
            print(f"    {k}: {v}")
        if len(new_reached) > 15:
            print(f"    ... and {len(new_reached) - 15} more")

    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    # Sort milestones by date for consistent display
    sorted_reached = dict(sorted(new_reached.items(), key=lambda x: x[1]))
    result = {"current": {}, "reached": sorted_reached}
    with open(MILESTONES_FILE, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Written {MILESTONES_FILE} ({len(new_reached)} milestones)")


if __name__ == "__main__":
    main()
