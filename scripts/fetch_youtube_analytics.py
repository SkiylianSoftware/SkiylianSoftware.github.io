"""
Fetch historical daily YouTube analytics and backfill track_history.py data.

Uses OAuth 2.0 (refresh token) to call the YouTube Analytics API.
Run daily (included in workflows) after the auth script has been used once.

Requires secrets:
  YOUTUBE_CLIENT_ID
  YOUTUBE_CLIENT_SECRET
  YOUTUBE_REFRESH_TOKEN
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests

CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
DATA_DIR = "_data"
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


def refresh_access_token():
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_report(access_token, start_date, end_date):
    url = "https://youtubeanalytics.googleapis.com/v2/reports"
    params = {
        "ids": "channel==MINE",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": "views,estimatedMinutesWatched,subscribersGained,subscribersLost,averageViewDuration",
        "dimensions": "day",
        "sort": "day",
        "maxResults": 1000,
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    if resp.status_code == 403:
        print("Analytics API not accessible (403). Is the API enabled?", file=sys.stderr)
        return None
    resp.raise_for_status()
    return resp.json()


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []


def save_history(history):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def main():
    if not CLIENT_ID or not CLIENT_SECRET or not REFRESH_TOKEN:
        print("Missing YouTube OAuth credentials. Skipping analytics fetch.", file=sys.stderr)
        return

    print("Refreshing access token...")
    try:
        access_token = refresh_access_token()
    except Exception as e:
        print(f"Failed to refresh token: {e}", file=sys.stderr)
        print("The refresh token may have expired. Re-run auth_youtube.py.", file=sys.stderr)
        return

    print("Fetching YouTube Analytics report...")
    report = fetch_report(access_token, "2010-01-01", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    if report is None:
        return

    rows = report.get("rows", [])
    if not rows:
        print("No analytics data returned.")
        return

    print(f"Got {len(rows)} days of analytics data")

    # Build a map: date -> {views, subs_gained, subs_lost, watch_time}
    analytics = {}
    for row in rows:
        date = row[0]
        views = int(row[1]) if row[1] else 0
        watch_time = int(row[2]) if row[2] else 0
        subs_gained = int(row[3]) if row[3] else 0
        subs_lost = int(row[4]) if row[4] else 0
        analytics[date] = {
            "views": views,
            "watch_time": watch_time,
            "subs_gained": subs_gained,
            "subs_lost": subs_lost,
        }

    # Load existing history and backfill
    history = load_history()
    existing_dates = {e["date"] for e in history}

    # Read current channel stats for the latest snapshot
    meta_path = os.path.join(DATA_DIR, "site_meta.json")
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)

    current_subs = meta.get("subscriber_count", 0)
    current_views = meta.get("view_count", 0)
    current_videos = meta.get("video_count", 0)

    # Sort analytics dates and compute cumulative values
    sorted_dates = sorted(analytics.keys())
    new_entries = 0

    # Running totals, starting from the earliest analytics data
    running_subs = 0
    running_views = 0
    running_watch = 0

    for date in sorted_dates:
        day = analytics[date]
        running_views += day["views"]
        running_subs += day["subs_gained"] - day["subs_lost"]
        running_watch += day["watch_time"]

        if date not in existing_dates:
            history.append(
                {
                    "date": date,
                    "youtube_main": {
                        "subs": max(0, running_subs),
                        "views": running_views,
                        "videos": 0,  # Analytics doesn't provide video count; track_history.py updates this
                    },
                    "_analytics": {
                        "views_gained": day["views"],
                        "watch_time_minutes": round(day["watch_time"] / 60),
                        "subs_gained": day["subs_gained"],
                        "subs_lost": day["subs_lost"],
                    },
                }
            )
            new_entries += 1

    # Update today's entry with the current snapshot from site_meta
    # (track_history.py will handle this on its next run, but do it here too for freshness)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for entry in history:
        if entry["date"] == today:
            entry.setdefault("youtube_main", {}).update(
                {
                    "subs": current_subs,
                    "views": current_views,
                    "videos": current_videos,
                }
            )
            break

    save_history(history)
    print(f"Added {new_entries} new analytics entries to history")
    print(f"History now has {len(history)} total entries")


if __name__ == "__main__":
    main()
