import json
import os
from datetime import datetime, timezone

DATA_DIR = "_data"


def load(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def save(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written {path}")


def main():
    twitch = load("twitch.json") or {}
    youtube = load("livestream.json") or {}

    now = datetime.now(timezone.utc).isoformat()

    twitch_live = twitch.get("platform") == "twitch"
    youtube_live = youtube.get("platform") == "youtube"

    if twitch_live:
        combined = {
            "platform": "twitch",
            "title": twitch.get("title", ""),
            "game_name": twitch.get("game_name", ""),
            "viewer_count": twitch.get("viewer_count", 0),
            "started_at": twitch.get("started_at", ""),
            "thumbnail_url": twitch.get("thumbnail_url", ""),
            "checked_at": now,
        }
    elif youtube_live:
        combined = {
            "platform": "youtube",
            "title": youtube.get("title", ""),
            "video_id": youtube.get("video_id", ""),
            "thumbnail": youtube.get("thumbnail", ""),
            "checked_at": now,
        }
    else:
        combined = {
            "platform": None,
            "checked_at": now,
        }

    save("livestream.json", combined)


if __name__ == "__main__":
    main()