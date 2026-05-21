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


def get_user_id(token):
    resp = requests.get(
        f"{API_URL}/users?login={TWITCH_USERNAME}",
        headers={"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    users = resp.json().get("data", [])
    return users[0]["id"] if users else None


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


def main():
    token = get_app_token()
    if not token:
        return

    user_id = get_user_id(token)
    if not user_id:
        print(f"Could not find Twitch user {TWITCH_USERNAME}", file=sys.stderr)
        return

    print(f"Checking Twitch stream status for {TWITCH_USERNAME}...")
    stream = fetch_stream(user_id, token)
    save("twitch.json", stream or {"platform": None, "checked_at": datetime.now(timezone.utc).isoformat()})


if __name__ == "__main__":
    main()