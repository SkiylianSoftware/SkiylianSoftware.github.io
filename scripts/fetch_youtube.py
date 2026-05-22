import json
import re
import os
import sys
from datetime import datetime, timezone

import requests

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
CHANNEL_ID = "UC4s4eXHuzj7OxwJXgiZgAYw"
UPLOADS_PLAYLIST_ID = "UU4s4eXHuzj7OxwJXgiZgAYw"
VODS_CHANNEL_ID = "UCC8qQOj7P2CWEcCDmOq0q7Q"
VODS_PLAYLIST_ID = "UUC8qQOj7P2CWEcCDmOq0q7Q"

DATA_DIR = "_data"
os.makedirs(DATA_DIR, exist_ok=True)


def api_get(url):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def parse_duration(iso_duration):
    if not iso_duration:
        return 0
    seconds = 0
    import re
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration)
    if m:
        h, mi, s = [int(g) if g else 0 for g in m.groups()]
        seconds = h * 3600 + mi * 60 + s
    return seconds


def fetch_video_details(video_ids):
    if not video_ids:
        return {}
    details = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        ids = ",".join(batch)
        url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=contentDetails,statistics"
            f"&id={ids}&key={YOUTUBE_API_KEY}"
        )
        data = api_get(url)
        for item in data.get("items", []):
            vid = item["id"]
            cd = item.get("contentDetails", {})
            stats = item.get("statistics", {})
            duration = cd.get("duration", "")
            details[vid] = {
                "duration": duration,
                "duration_seconds": parse_duration(duration),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
            }
    return details


import re
SERIES_RE = re.compile(r'^(?P<game>[^:]+):\s*(?P<series>.+?)#(?P<episode>\d+)\s*[-–]\s*(?P<subtitle>.+)$')

def parse_series(title):
    m = SERIES_RE.match(title)
    if m:
        return {
            "game": m.group("game").strip(),
            "series_name": m.group("series").strip(),
            "episode_number": int(m.group("episode")),
            "episode_title": m.group("subtitle").strip(),
        }
    return None


def fetch_uploads(playlist_id, label="uploads"):
    if not YOUTUBE_API_KEY:
        print(f"No YOUTUBE_API_KEY set, skipping {label}", file=sys.stderr)
        return None
    videos = []
    video_ids = []
    page_token = None
    page_num = 0
    while True:
        url = (
            f"https://www.googleapis.com/youtube/v3/playlistItems"
            f"?part=snippet&maxResults=50"
            f"&playlistId={playlist_id}&key={YOUTUBE_API_KEY}"
        )
        if page_token:
            url += f"&pageToken={page_token}"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 404:
            print(f"Playlist {playlist_id} not found, skipping {label}", file=sys.stderr)
            return []
        if resp.status_code != 200:
            print(f"YouTube API error {resp.status_code} for {label}: {resp.text[:200]}", file=sys.stderr)
            return []
        data = resp.json()
        items = data.get("items", [])
        page_num += 1
        print(f"  Page {page_num}: {len(items)} items (total so far: {len(videos)})")
        for item in items:
            snippet = item.get("snippet", {})
            resource = snippet.get("resourceId", {})
            video_id = resource.get("videoId")
            if not video_id:
                continue
            video_ids.append(video_id)
            thumbnails = snippet.get("thumbnails", {})
            thumbnail = (
                thumbnails.get("maxres", {}) or thumbnails.get("high", {}) or thumbnails.get("medium", {})
            ).get("url", "")
            videos.append({
                "title": snippet.get("title", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "video_id": video_id,
                "thumbnail": thumbnail,
                "published": snippet.get("publishedAt", ""),
                "description": snippet.get("description", "")[:500],
                "series": parse_series(snippet.get("title", "")),
            })
        page_token = data.get("nextPageToken")
        if not page_token:
            break

    details = fetch_video_details(video_ids)
    for v in videos:
        vid = v["video_id"]
        if vid in details:
            v.update(details[vid])

    print(f"  Total: {len(videos)} videos fetched for {label}")
    return videos


def fetch_playlists():
    if not YOUTUBE_API_KEY:
        return None
    all_playlists = []
    page_token = None
    while True:
        url = (
            f"https://www.googleapis.com/youtube/v3/playlists"
            f"?part=snippet,contentDetails"
            f"&channelId={CHANNEL_ID}&maxResults=50&key={YOUTUBE_API_KEY}"
        )
        if page_token:
            url += f"&pageToken={page_token}"
        data = api_get(url)
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            thumb = snippet.get("thumbnails", {})
            all_playlists.append({
                "title": snippet.get("title", ""),
                "url": f"https://www.youtube.com/playlist?list={item['id']}",
                "playlist_id": item["id"],
                "item_count": item.get("contentDetails", {}).get("itemCount", 0),
                "thumbnail": (thumb.get("high", {}) or thumb.get("medium", {}) or thumb.get("default", {})).get("url", ""),
                "description": snippet.get("description", ""),
                "published": snippet.get("publishedAt", ""),
                "channel_title": snippet.get("channelTitle", ""),
            })
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return all_playlists


def fetch_livestream():
    if not YOUTUBE_API_KEY:
        return None
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet"
        f"&channelId={CHANNEL_ID}"
        f"&eventType=live&type=video"
        f"&key={YOUTUBE_API_KEY}"
    )
    data = api_get(url)
    items = data.get("items", [])
    if not items:
        return None
    item = items[0]
    video_id = item.get("id", {}).get("videoId")
    if not video_id:
        return None
    return {
        "platform": "youtube",
        "video_id": video_id,
        "title": item.get("snippet", {}).get("title", ""),
        "thumbnail": (item.get("snippet", {}).get("thumbnails", {}).get("high", {}) or {}).get("url", ""),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def read_config_flag(key, default="auto"):
    try:
        with open("_config.yml") as f:
            for line in f:
                if line.startswith(f"{key}:"):
                    val = line.split(":", 1)[1].strip()
                    if val.lower() == "true":
                        return True
                    if val.lower() == "false":
                        return False
                    return "auto"
    except FileNotFoundError:
        pass
    return default


def check_youtube_memberships():
    override = read_config_flag("youtube_memberships")
    if override != "auto":
        return override
    try:
        url = f"https://www.youtube.com/channel/{CHANNEL_ID}/join"
        resp = requests.get(url, timeout=10, allow_redirects=True)
        if resp.status_code != 200:
            return False
        text = resp.text
        # Look for a Membership tab in the channel page data
        m = re.search(r'ytInitialData\s*=\s*({.*?});', text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                tabs = data.get("contents", {}).get(
                    "twoColumnBrowseResultsRenderer", {}
                ).get("tabs", [])
                for tab in tabs:
                    title = tab.get("tabRenderer", {}).get("title", "")
                    if title and "membership" in title.lower():
                        return True
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        # Fallback: text search for specific join UI (not generic config strings)
        text_lower = text.lower()
        negatives = [
            "memberships aren't available",
            "memberships are not available",
            "no memberships",
            "not eligible",
        ]
        positives = [
            "join this channel",
            "become a member",
        ]
        for n in negatives:
            if n in text_lower:
                return False
        for p in positives:
            if p in text_lower:
                return True
        return False
    except requests.RequestException:
        pass
    return False


def fetch_channel_info(channel_id=None):
    if not YOUTUBE_API_KEY:
        return None
    cid = channel_id or CHANNEL_ID
    url = (
        f"https://www.googleapis.com/youtube/v3/channels"
        f"?part=snippet,brandingSettings,statistics"
        f"&id={cid}"
        f"&key={YOUTUBE_API_KEY}"
    )
    data = api_get(url)
    items = data.get("items", [])
    if not items:
        return None
    item = items[0]
    snippet = item.get("snippet", {})
    branding = item.get("brandingSettings", {})
    stats = item.get("statistics", {})
    thumbnails = snippet.get("thumbnails", {})
    avatar = (
        thumbnails.get("high", {}) or thumbnails.get("medium", {}) or thumbnails.get("default", {})
    ).get("url", "")
    memberships_available = check_youtube_memberships()
    return {
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "custom_url": snippet.get("customUrl", ""),
        "avatar_url": avatar,
        "banner_url": branding.get("image", {}).get("bannerExternalUrl", ""),
        "subscriber_count": int(stats.get("subscriberCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "view_count": int(stats.get("viewCount", 0)),
        "published_at": snippet.get("publishedAt", ""),
        "country": snippet.get("country", ""),
        "memberships_available": memberships_available,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def update_config_avatar(avatar_url):
    config_path = "_config.yml"
    with open(config_path) as f:
        content = f.read()
    old_line = [l for l in content.splitlines() if l.startswith("avatar:")][0]
    new_line = f"avatar: {avatar_url}"
    if old_line.strip() == new_line.strip():
        return
    content = content.replace(old_line, new_line)
    with open(config_path, "w") as f:
        f.write(content)
    print(f"Updated avatar in _config.yml: {avatar_url}")


def save(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written {path} ({len(data)} items)" if isinstance(data, list) else f"Written {path}")


MILESTONE_SUBS = [10, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]
MILESTONE_VIEWS = [1000, 5000, 10000, 50000, 100000, 500000, 1000000]
MILESTONE_VIDEOS = [10, 25, 50, 100, 250, 500, 1000]

MILESTONE_MESSAGES = {
    10: "First double digits!",
    50: "Halfway to 100!",
    100: "Triple digits!",
    250: "Quarter of the way!",
    500: "Half a thousand!",
    1000: "The big 1K!",
    2500: "2.5K and growing!",
    5000: "5K strong!",
    10000: "10K! Unreal!",
    25000: "25K! Amazing!",
    50000: "50K! Halfway to 100K!",
    100000: "100K!!! Thank you!",
}


def detect_milestones(subs, views, videos_count):
    current = {}
    for m in sorted(MILESTONE_SUBS, reverse=True):
        if subs >= m:
            current = {"type": "subs", "count": m, "message": MILESTONE_MESSAGES.get(m, "Milestone!")}
            break
    for m in sorted(MILESTONE_VIEWS, reverse=True):
        if views >= m:
            if not current or m > (current.get("count", 0) if current.get("type") == "views" else 0):
                current = {"type": "views", "count": m, "message": f"{m} views!"}
            break
    for m in sorted(MILESTONE_VIDEOS, reverse=True):
        if videos_count >= m:
            if not current or m > (current.get("count", 0) if current.get("type") == "videos" else 0):
                current = {"type": "videos", "count": m, "message": f"{m} videos uploaded!"}
            break
    return {"current": current, "milestones": None}


def compute_series_recency(videos):
    now = datetime.now(timezone.utc)
    series_data = {}
    for v in videos:
        s = v.get("series")
        if not s:
            continue
        name = s.get("series_name")
        if not name:
            continue
        if name not in series_data:
            series_data[name] = {"episode_count": 0, "latest": None}
        series_data[name]["episode_count"] += 1
        published = v.get("published")
        if not published:
            continue
        try:
            dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            continue
        if series_data[name]["latest"] is None or dt > series_data[name]["latest"]:
            series_data[name]["latest"] = dt

    recency = {}
    for name, data in series_data.items():
        dt = data["latest"]
        if not dt:
            recency[name] = {"status": "historical", "episodes": data["episode_count"]}
            continue
        days = (now - dt).days
        if days < 183:
            status = "current"
        elif days < 366:
            status = "recent"
        else:
            status = "historical"
        recency[name] = {"status": status, "episodes": data["episode_count"]}
    return recency


def main():
    print("Fetching YouTube uploads...")
    videos = fetch_uploads(UPLOADS_PLAYLIST_ID, "main channel uploads")
    if videos is not None:
        series_recency = compute_series_recency(videos)
        save("youtube_main.json", {"videos": videos, "series_recency": series_recency})

    print("Fetching YouTube VODs...")
    vods = fetch_uploads(VODS_PLAYLIST_ID, "VODs channel uploads")
    if vods is not None:
        save("youtube_vods.json", {"videos": vods})

    print("Fetching YouTube playlists...")
    playlists = fetch_playlists()
    if playlists is not None:
        save("playlists.json", {"playlists": playlists})

    print("Fetching livestream status...")
    live = fetch_livestream()
    save("livestream.json", live or {"platform": None, "checked_at": datetime.now(timezone.utc).isoformat()})

    print("Fetching channel info...")
    info = fetch_channel_info()
    if not info:
        return

    vods_info = fetch_channel_info(VODS_CHANNEL_ID)
    if vods_info:
        info["vods_subscriber_count"] = vods_info.get("subscriber_count", 0)
        info["vods_video_count"] = vods_info.get("video_count", 0)
        info["vods_view_count"] = vods_info.get("view_count", 0)
        info["vods_published_at"] = vods_info.get("published_at", "")

    save("site_meta.json", info)
    update_config_avatar(info.get("avatar_url", ""))

    milestones = detect_milestones(
        info.get("subscriber_count", 0),
        info.get("view_count", 0),
        info.get("video_count", 0),
    )
    save("milestones.json", milestones)


if __name__ == "__main__":
    main()