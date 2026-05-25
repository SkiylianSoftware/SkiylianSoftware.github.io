"""
Fetch historical daily YouTube analytics and backfill track_history.py data.
Uses OAuth 2.0 (refresh token) to call the YouTube Analytics API.
Fetches in 365-day chunks to avoid the 1000-row limit.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import requests

CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
VODS_CHANNEL_ID = "UCC8qQOj7P2CWEcCDmOq0q7Q"
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


def fetch_report(access_token, start_date, end_date, ids="channel==MINE"):
    url = "https://youtubeanalytics.googleapis.com/v2/reports"
    params = {
        "ids": ids,
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
        print(f"  Analytics API not accessible for {ids} (403)", file=sys.stderr)
        return None
    resp.raise_for_status()
    data = resp.json()
    rows = data.get("rows", [])
    print(f"  {ids}: {start_date} to {end_date} -> {len(rows)} rows")
    return data


def fetch_all_reports(access_token, start_date, end_date, ids="channel==MINE"):
    """Fetch analytics in 365-day chunks to avoid the 1000-row API limit."""
    all_rows = []
    chunk_end = end_date
    chunk_num = 0
    while True:
        chunk_start = (datetime.strptime(chunk_end, "%Y-%m-%d") - timedelta(days=364)).strftime("%Y-%m-%d")
        if chunk_start < start_date:
            chunk_start = start_date
        chunk_num += 1
        report = fetch_report(access_token, chunk_start, chunk_end, ids=ids)
        if report is None:
            return None
        rows = report.get("rows", [])
        print(f"    Chunk {chunk_num}: got {len(rows)} rows ({chunk_start} to {chunk_end})")
        all_rows = rows + all_rows  # prepend oldest first
        if len(rows) < 364 or chunk_start <= start_date:
            break
        chunk_end = (datetime.strptime(chunk_start, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"  Total: {len(all_rows)} rows across {chunk_num} chunks")
    return {"rows": all_rows}


def build_analytics_map(rows):
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
    return analytics


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []


def save_history(history):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def process_channel_analytics(analytics, history, platform_key):
    sorted_dates = sorted(analytics.keys())
    new_entries = 0
    running_subs = 0
    running_views = 0

    for date in sorted_dates:
        day = analytics[date]
        running_views += day["views"]
        running_subs += day["subs_gained"] - day["subs_lost"]

        entry = None
        for e in history:
            if e["date"] == date:
                entry = e
                break

        if entry is None:
            entry = {"date": date}
            history.append(entry)
            new_entries += 1

        entry.setdefault("youtube_main", {})
        entry.setdefault("youtube_vods", {})
        if "subs" not in entry[platform_key]:
            entry[platform_key]["subs"] = max(0, running_subs)
        if "views" not in entry[platform_key]:
            entry[platform_key]["views"] = running_views
        if "videos" not in entry[platform_key]:
            entry[platform_key]["videos"] = 0

        if platform_key == "youtube_main" and "_analytics" not in entry:
            entry["_analytics"] = {
                "views_gained": day["views"],
                "watch_time_minutes": round(day["watch_time"] / 60),
                "subs_gained": day["subs_gained"],
                "subs_lost": day["subs_lost"],
            }

    return new_entries


def main():
    if not CLIENT_ID or not CLIENT_SECRET or not REFRESH_TOKEN:
        print("Missing YouTube OAuth credentials. Skipping analytics fetch.", file=sys.stderr)
        return

    print("Refreshing access token...")
    try:
        access_token = refresh_access_token()
    except Exception as e:
        print(f"Failed to refresh token: {e}", file=sys.stderr)
        return

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start = "2010-01-01"
    history = load_history()
    print(f"Loaded existing history: {len(history)} entries")
    total_new = 0

    channels = [
        ("channel==MINE", "youtube_main"),
        (f"channel=={VODS_CHANNEL_ID}", "youtube_vods"),
    ]

    for ids, platform_key in channels:
        label = platform_key.replace("youtube_", "")
        print(f"\nFetching analytics for {label} channel ({ids})...")
        report = fetch_all_reports(access_token, start, today, ids=ids)
        if report is None:
            continue
        rows = report.get("rows", [])
        if not rows:
            print(f"  No analytics data for {label}.")
            continue
        analytics = build_analytics_map(rows)
        n = process_channel_analytics(analytics, history, platform_key)
        total_new += n
        print(f"  {label}: {len(rows)} data days, {n} new history entries")

    history.sort(key=lambda e: e["date"])

    # Update today's entry with latest snapshots from site_meta
    meta_path = os.path.join(DATA_DIR, "site_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        for entry in history:
            if entry["date"] == today:
                entry.setdefault("youtube_main", {}).update(
                    {
                        "subs": meta.get("subscriber_count", 0),
                        "views": meta.get("view_count", 0),
                        "videos": meta.get("video_count", 0),
                    }
                )
                entry.setdefault("youtube_vods", {}).update(
                    {
                        "subs": meta.get("vods_subscriber_count", 0),
                        "views": meta.get("vods_view_count", 0),
                        "videos": meta.get("vods_video_count", 0),
                    }
                )
                break

    save_history(history)
    print(f"\nDone: {total_new} new entries, history now {len(history)} entries")


if __name__ == "__main__":
    main()
