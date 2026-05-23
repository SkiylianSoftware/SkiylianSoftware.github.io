import json
import os
import sys
from datetime import datetime, timezone

import requests

TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID", "")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET", "")
TWITCH_USERNAME = "skiylia"

DATA_DIR = "_data"
TOKEN_URL = "https://id.twitch.tv/oauth2/token"
API_URL = "https://api.twitch.tv/helix"


def get_app_token():
    if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
        print("No Twitch credentials set, skipping Twitch fetch", file=sys.stderr)
        return None
    resp = requests.post(TOKEN_URL, params={
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_user_info(token):
    resp = requests.get(
        f"{API_URL}/users?login={TWITCH_USERNAME}",
        headers={"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    users = resp.json().get("data", [])
    if not users:
        return None, None, None, None
    u = users[0]
    return u["id"], u.get("broadcaster_type", ""), u.get("view_count", 0), u.get("created_at", "")


def fetch_stream(user_id, token):
    resp = requests.get(
        f"{API_URL}/streams?user_id={user_id}",
        headers={"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    streams = resp.json().get("data", [])
    if not streams:
        return None
    s = streams[0]
    return {
        "platform": "twitch",
        "title": s.get("title", ""),
        "game_name": s.get("game_name", ""),
        "viewer_count": s.get("viewer_count", 0),
        "started_at": s.get("started_at", ""),
        "thumbnail_url": s.get("thumbnail_url", "").replace("{width}", "640").replace("{height}", "360"),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def save(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written {path}")


def fetch_followers(user_id, token):
    resp = requests.get(
        f"{API_URL}/channels/followers?broadcaster_id={user_id}&first=1",
        headers={"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("total", 0)


def fetch_schedule(user_id, token):
    resp = requests.get(
        f"{API_URL}/schedule?broadcaster_id={user_id}",
        headers={"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json().get("data", {})
    segments = data.get("segments", [])
    schedule = []
    for s in segments:
        schedule.append({
            "start_time": s.get("start_time", ""),
            "end_time": s.get("end_time", ""),
            "title": s.get("title", ""),
            "category": s.get("category", {}).get("name", "") if s.get("category") else "",
            "is_recurring": s.get("is_recurring", False),
        })
    return schedule


def fetch_vods(user_id, token):
    vods = []
    cursor = None
    while True:
        params = {"user_id": user_id, "type": "archive", "first": 100}
        if cursor:
            params["after"] = cursor
        resp = requests.get(
            f"{API_URL}/videos",
            headers={"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {token}"},
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("data", []):
            duration_str = item.get("duration", "")
            seconds = 0
            parts = duration_str.replace("h", ":").replace("m", ":").replace("s", "").split(":")
            if len(parts) == 3:
                seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                seconds = int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 1:
                seconds = int(parts[0])
            vods.append({
                "video_id": item["id"],
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "thumbnail": item.get("thumbnail_url", "").replace("{width}", "640").replace("{height}", "360"),
                "published": item.get("created_at", ""),
                "duration_seconds": seconds,
                "view_count": item.get("view_count", 0),
                "description": (item.get("description") or "")[:500],
            })
        cursor = data.get("pagination", {}).get("cursor")
        if not cursor:
            break
    return vods


def main():
    token = get_app_token()
    if not token:
        return

    user_id, broadcaster_type, twitch_views, twitch_created = get_user_info(token)
    if not user_id:
        print(f"Could not find Twitch user {TWITCH_USERNAME}", file=sys.stderr)
        return

    print(f"Checking Twitch stream status for {TWITCH_USERNAME}...")
    stream = fetch_stream(user_id, token)
    save("twitch.json", stream or {"platform": None, "checked_at": datetime.now(timezone.utc).isoformat()})

    print("Fetching Twitch follower count...")
    try:
        followers = fetch_followers(user_id, token)
        save("twitch_stats.json", {"follower_count": followers, "broadcaster_type": broadcaster_type, "view_count": twitch_views, "created_at": twitch_created, "fetched_at": datetime.now(timezone.utc).isoformat()})
        print(f"Twitch followers: {followers}")
    except Exception as e:
        print(f"Could not fetch Twitch followers: {e}", file=sys.stderr)

    print("Fetching Twitch schedule...")
    try:
        schedule = fetch_schedule(user_id, token)
        save("twitch_schedule.json", {"segments": schedule, "fetched_at": datetime.now(timezone.utc).isoformat()})
        print(f"Twitch schedule: {len(schedule)} upcoming segments")
    except Exception as e:
        print(f"Could not fetch Twitch schedule: {e}", file=sys.stderr)

    print("Fetching Twitch VODs...")
    try:
        vods = fetch_vods(user_id, token)
        save("twitch_vods.json", {"videos": vods})
        print(f"Twitch VODs: {len(vods)} past broadcasts")
    except Exception as e:
        print(f"Could not fetch Twitch VODs: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()