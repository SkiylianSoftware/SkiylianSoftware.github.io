import json
import os
import sys
from datetime import datetime, timezone

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
    snapshot = {"date": datetime.now(timezone.utc).strftime("%Y-%m-%d")}

    meta = read_json("site_meta.json")
    if meta:
        snapshot["youtube_main"] = {
            "subs": meta.get("subscriber_count", 0),
            "views": meta.get("view_count", 0),
            "videos": meta.get("video_count", 0),
        }
        vods_subs = meta.get("vods_subscriber_count", 0)
        vods_views = meta.get("vods_view_count", 0)
        vods_videos = meta.get("vods_video_count", 0)
        if vods_subs or vods_views or vods_videos:
            snapshot["youtube_vods"] = {
                "subs": vods_subs,
                "views": vods_views,
                "videos": vods_videos,
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


def seed_initial():
    snapshot = build_snapshot()
    return [snapshot]


def main():
    meta_path = os.path.join(DATA_DIR, "site_meta.json")
    if not os.path.exists(meta_path):
        print("No site_meta.json found, skipping history", file=sys.stderr)
        return

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    history = load_history()

    # Migrate old flat-format entries to per-platform format
    migrated = 0
    for entry in history:
        if "subs" in entry and "youtube_main" not in entry:
            entry["youtube_main"] = {
                "subs": entry.pop("subs", 0),
                "views": entry.pop("views", 0),
                "videos": entry.pop("videos", 0),
            }
            migrated += 1
    if migrated:
        print(f"Migrated {migrated} history entries to new format")

    if not history:
        history = seed_initial()
        print("Seeded initial history from current data")

    snapshot = build_snapshot()

    if history and history[-1].get("date") == today:
        history[-1] = snapshot
        print(f"Updated today's entry ({today})")
    else:
        history.append(snapshot)
        print(f"Added new entry for {today}")

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
    print(f"History: {len(history)} entries")


if __name__ == "__main__":
    main()
