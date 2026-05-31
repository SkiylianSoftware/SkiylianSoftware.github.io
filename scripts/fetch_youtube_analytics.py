"""
Fetch historical daily YouTube analytics and per-video historical data.
Uses OAuth 2.0 (refresh token) to call the YouTube Analytics API.
Fetches channel-level and per-video data in 365-day chunks.
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
VIDEO_HISTORY_FILE = os.path.join(DATA_DIR, "video_history.json")


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
    if resp.status_code != 200:
        body = resp.text
        print(f"  Token refresh failed ({resp.status_code}): {body}", file=sys.stderr)
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


def load_video_history():
    if os.path.exists(VIDEO_HISTORY_FILE):
        with open(VIDEO_HISTORY_FILE) as f:
            return json.load(f)
    return {}


def save_video_history(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(VIDEO_HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def merge_video_metadata(video_history, yt_data):
    """Merge video metadata from youtube_main.json into video_history."""
    for v in yt_data.get("videos", []):
        vid = v.get("video_id", "")
        if not vid:
            continue
        if vid not in video_history:
            video_history[vid] = {}
        video_history[vid].setdefault("daily", {})
        s = v.get("series", {}) or {}
        video_history[vid].update(
            {
                "title": v.get("title", ""),
                "published": (v.get("published") or "")[:10],
                "game": s.get("game", ""),
                "series_name": s.get("series_name", ""),
                "episode_number": s.get("episode_number"),
                "duration_seconds": v.get("duration_seconds", 0),
            }
        )


def fetch_video_history(video_history, access_token, start_date, end_date):
    """Fetch per-video analytics one video at a time via filters=video==VID."""
    url = "https://youtubeanalytics.googleapis.com/v2/reports"
    sd = datetime.strptime(start_date, "%Y-%m-%d")
    ed = datetime.strptime(end_date, "%Y-%m-%d")

    need_fetch = []
    for vid, vdata in video_history.items():
        existing = set(vdata.get("daily", {}).keys())
        # Check if any date in range is missing
        cur = sd
        missing = False
        while cur <= ed:
            if cur.strftime("%Y-%m-%d") not in existing:
                missing = True
                break
            cur += timedelta(days=1)
        if missing:
            need_fetch.append(vid)

    if not need_fetch:
        print("  All videos have up-to-date data")
        return

    fetched = 0
    for vid in need_fetch:
        params = {
            "ids": "channel==MINE",
            "startDate": start_date,
            "endDate": end_date,
            "metrics": "views,estimatedMinutesWatched,likes,comments",
            "dimensions": "day",
            "filters": f"video=={vid}",
            "sort": "day",
            "maxResults": 1000,
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            if resp.status_code == 403:
                continue
            resp.raise_for_status()
            data = resp.json()
            rows = data.get("rows", [])
            if not rows:
                continue
            for row in rows:
                d = row[0]
                views = int(row[1]) if row[1] else 0
                watch_time = int(row[2]) if row[2] else 0
                likes = int(row[3]) if len(row) > 3 and row[3] else 0
                comments = int(row[4]) if len(row) > 4 and row[4] else 0
                if vid not in video_history:
                    video_history[vid] = {"daily": {}}
                video_history[vid].setdefault("daily", {})[d] = {
                    "views": views,
                    "watch_time": watch_time,
                    "likes": likes,
                    "comments": comments,
                }
            fetched += 1
            if fetched % 10 == 0:
                print(f"    Fetched {fetched}/{len(need_fetch)} videos...")
        except Exception as e:
            print(f"    Error fetching video {vid}: {e}", file=sys.stderr)
    print(f"  Fetched per-video data for {fetched}/{len(need_fetch)} videos")


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
    print(f"\nDone channel analytics: {total_new} new entries, history now {len(history)} entries")

    # Per-video analytics
    print("\nFetching per-video analytics...")
    yt_main = None
    yt_path = os.path.join(DATA_DIR, "youtube_main.json")
    if os.path.exists(yt_path):
        with open(yt_path) as f:
            yt_main = json.load(f)

    video_history = load_video_history()
    if yt_main:
        merge_video_metadata(video_history, yt_main)

    # Determine fetch range: from last tracked date or channel start up to today
    existing_dates = set()
    for vdata in video_history.values():
        existing_dates.update(vdata.get("daily", {}).keys())
    if existing_dates:
        last_date = max(existing_dates)
        fetch_start = (datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        fetch_start = "2010-01-01"
    if fetch_start < today:
        print(f"  Fetching missing per-video data from {fetch_start} to {today}...")
        fetch_video_history(video_history, access_token, fetch_start, today)

    if yt_main:
        merge_video_metadata(video_history, yt_main)
    save_video_history(video_history)
    print(f"Video history: {len(video_history)} videos tracked")


if __name__ == "__main__":
    main()
