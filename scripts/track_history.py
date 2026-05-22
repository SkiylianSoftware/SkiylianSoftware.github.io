import json
import os
from datetime import datetime, timezone

DATA_DIR = "_data"
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []


def seed_initial(meta):
    published = meta.get("published_at", "")
    if published and len(published) >= 10:
        start_date = published[:10]
    else:
        start_date = "2024-04-07"
    return [
        {"date": start_date, "subs": 0, "views": 0, "videos": 0},
    ]


def main():
    meta_path = os.path.join(DATA_DIR, "site_meta.json")
    if not os.path.exists(meta_path):
        print("No site_meta.json found, skipping history", file=sys.stderr)
        return

    with open(meta_path) as f:
        meta = json.load(f)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    history = load_history()

    if not history:
        history = seed_initial(meta)
        print("Seeded initial history from channel start date")

    if history and history[-1].get("date") == today:
        history[-1].update({
            "subs": meta.get("subscriber_count", 0),
            "views": meta.get("view_count", 0),
            "videos": meta.get("video_count", 0),
        })
        print(f"Updated today's entry ({today})")
    else:
        history.append({
            "date": today,
            "subs": meta.get("subscriber_count", 0),
            "views": meta.get("view_count", 0),
            "videos": meta.get("video_count", 0),
        })
        print(f"Added new entry for {today}")

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
    print(f"History: {len(history)} entries")


if __name__ == "__main__":
    main()