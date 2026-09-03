import json
import os
import sys
from datetime import datetime, timedelta, timezone

DATA_DIR = "_data"
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []


def read_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def build_snapshot():
    snapshot = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "_schema_version": 1,
    }

    meta = read_json("site_meta.json")
    snapshot["youtube_main"] = {
        "subs": meta.get("subscriber_count", 0) if meta else 0,
        "views": meta.get("view_count", 0) if meta else 0,
        "videos": meta.get("video_count", 0) if meta else 0,
        "duration_seconds": 0,
        "likes": 0,
        "comments": 0,
    }
    # Compute total duration and likes from youtube_main video data
    yt = read_json("youtube_main.json")
    if yt and yt.get("videos"):
        total_dur = 0
        total_likes = 0
        total_comments = 0
        total_views = 0
        for v in yt["videos"]:
            total_dur += v.get("duration_seconds", 0)
            total_likes += v.get("like_count", 0)
            total_comments += v.get("comment_count", 0)
            total_views += v.get("view_count", 0)
        snapshot["youtube_main"]["duration_seconds"] = total_dur
        snapshot["youtube_main"]["likes"] = total_likes
        snapshot["youtube_main"]["comments"] = total_comments
        if total_views > 0:
            snapshot["youtube_main"]["engagement_rate"] = round((total_likes + total_comments) / total_views * 100, 1)
        else:
            snapshot["youtube_main"]["engagement_rate"] = 0.0
        vods_subs = meta.get("vods_subscriber_count", 0)
        vods_views = meta.get("vods_view_count", 0)
        vods_videos = meta.get("vods_video_count", 0)
        if vods_subs or vods_views or vods_videos:
            vods_dur = 0
            vods_likes = 0
            vods_comments = 0
            vods = read_json("youtube_vods.json")
            if vods and vods.get("videos"):
                for v in vods["videos"]:
                    vods_dur += v.get("duration_seconds", 0)
                    vods_likes += v.get("like_count", 0)
                    vods_comments += v.get("comment_count", 0)
            snapshot["youtube_vods"] = {
                "subs": vods_subs,
                "views": vods_views,
                "videos": vods_videos,
                "duration_seconds": vods_dur,
                "likes": vods_likes,
                "comments": vods_comments,
            }

    twitch_stats = read_json("twitch_stats.json")
    if twitch_stats:
        snapshot["twitch"] = {
            "followers": twitch_stats.get("follower_count", 0),
            "views": twitch_stats.get("view_count", 0),
        }

    fourthwall = read_json("fourthwall.json")
    if fourthwall:
        snapshot["fourthwall"] = {
            "orders": fourthwall.get("total_orders", 0),
        }

    github = read_json("github.json")
    if github:
        snapshot["github"] = {
            "followers": github.get("followers", 0),
            "stars": github.get("total_stars", 0),
            "forks": github.get("total_forks", 0),
        }

    return snapshot


def backfill_history():
    """Build a full backfilled history from available data sources."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot = build_snapshot()

    # Find earliest date from all available sources
    earliest = None
    now_dt = datetime.now(timezone.utc)

    # YouTube videos
    yt = read_json("youtube_main.json")
    earliest_video_date = None
    all_video_dates = set()
    if yt and yt.get("videos"):
        for v in yt["videos"]:
            pub = v.get("published", "")
            if pub and len(pub) >= 10:
                d = pub[:10]
                all_video_dates.add(d)
                if earliest_video_date is None or d < earliest_video_date:
                    earliest_video_date = d

    # Load existing analytics history if available
    analytics = {}
    hist = load_history()
    if hist:
        for entry in hist:
            d = entry.get("date", "")
            if d and d < today:
                ym = entry.get("youtube_main", {}) or {}
                analytics[d] = {
                    "subs": ym.get("subs", 0),
                    "views": ym.get("views", 0),
                    "videos": ym.get("videos", 0),
                    "duration_seconds": ym.get("duration_seconds", 0),
                    "likes": ym.get("likes", 0),
                    "comments": ym.get("comments", 0),
                }

    # Determine start date from earliest video
    earliest = earliest_video_date
    if not earliest:
        return [snapshot]

    # Build weekly entries from earliest to today
    entries_by_date = {}

    if earliest_video_date:
        start = datetime.strptime(earliest_video_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        current = start
        video_dates_sorted = sorted(all_video_dates)

        cum_videos = 0
        cum_duration = 0
        cum_likes = 0
        cum_comments = 0
        cum_views = 0
        vid_idx = 0

        while current <= now_dt:
            d = current.strftime("%Y-%m-%d")
            if d > today:
                break

            # Count videos published on or before this date
            while vid_idx < len(video_dates_sorted) and video_dates_sorted[vid_idx] <= d:
                # Find the matching video for duration/likes
                for v in yt.get("videos", []):
                    vd = (v.get("published") or "")[:10]
                    if vd == video_dates_sorted[vid_idx]:
                        cum_duration += v.get("duration_seconds", 0)
                        cum_likes += v.get("like_count", 0)
                        cum_comments += v.get("comment_count", 0)
                        cum_views += v.get("view_count", 0)
                        break
                cum_videos += 1
                vid_idx += 1

            if d not in entries_by_date:
                entries_by_date[d] = {
                    "date": d,
                    "youtube_main": {
                        "subs": 0,
                        "views": 0,
                        "videos": cum_videos,
                        "duration_seconds": cum_duration,
                        "likes": cum_likes,
                        "comments": cum_comments,
                        "views_cumulative": cum_views,
                        "engagement_rate": (
                            round((cum_likes + cum_comments) / cum_views * 100, 1) if cum_views > 0 else 0.0
                        ),
                    },
                    "youtube_vods": {},
                    "twitch": {},
                    "github": {},
                    "fourthwall": {},
                }
            else:
                # Fill in video count from analytics if missing
                e = entries_by_date[d]
                if e["youtube_main"]["videos"] == 0 and cum_videos > 0:
                    e["youtube_main"]["videos"] = cum_videos

            current += timedelta(days=7)

    # Sort and fill gaps by carrying forward the last known value
    sorted_dates = sorted(entries_by_date.keys())
    result = []
    last = {
        "youtube_main": {"subs": 0, "views": 0, "videos": 0, "duration_seconds": 0, "likes": 0, "comments": 0},
        "youtube_vods": {},
        "twitch": {},
        "github": {},
        "fourthwall": {},
    }

    for d in sorted_dates:
        entry = entries_by_date[d]
        # Carry forward fields from last entry if not set
        for platform in ("youtube_main", "youtube_vods", "twitch", "github", "fourthwall"):
            if platform not in entry or not entry[platform]:
                entry[platform] = dict(last.get(platform, {}))
            else:
                last[platform] = dict(entry[platform])
        result.append(entry)

    return result


def main():
    meta_path = os.path.join(DATA_DIR, "site_meta.json")
    if not os.path.exists(meta_path):
        print("No site_meta.json found, skipping history", file=sys.stderr)
        return

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    history = load_history()

    if not history:
        history = backfill_history()
        print(f"Backfilled {len(history)} entries from video data")
    else:
        # Schema migration: always recompute cumulative duration_seconds/likes/comments from video data
        yt = read_json("youtube_main.json")
        if yt and yt.get("videos"):
            videos = sorted(yt["videos"], key=lambda v: (v.get("published") or "")[:10])
            history.sort(key=lambda e: e.get("date", ""))
            vid_idx = 0
            cum_dur = 0
            cum_likes = 0
            cum_comments = 0
            for entry in history:
                d = entry.get("date", "")
                ym = entry.setdefault("youtube_main", {})
                while vid_idx < len(videos):
                    vd = (videos[vid_idx].get("published") or "")[:10]
                    if vd <= d:
                        cum_dur += videos[vid_idx].get("duration_seconds", 0)
                        cum_likes += videos[vid_idx].get("like_count", 0)
                        cum_comments += videos[vid_idx].get("comment_count", 0)
                        vid_idx += 1
                    else:
                        break
                ym["duration_seconds"] = cum_dur
                ym["likes"] = cum_likes
                ym["comments"] = cum_comments
            print(f"Migrated {len(history)} history entries: added duration/likes/comments")
    snapshot = build_snapshot()
    if history and history[-1].get("date") == today:
        existing = history[-1]
        # Preserve analytics deltas so build_history.py can use anchor-based accumulation
        if "_analytics" in existing:
            snapshot["_analytics"] = existing["_analytics"]
        history[-1] = snapshot
        print(f"Updated today's entry ({today})")
    else:
        history.append(snapshot)
        print(f"Added new entry for {today}")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
    print(f"History: {len(history)} total entries")


if __name__ == "__main__":
    main()
