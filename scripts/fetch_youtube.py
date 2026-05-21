import json
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


def fetch_uploads(playlist_id, label="uploads"):
    if not YOUTUBE_API_KEY:
        print(f"No YOUTUBE_API_KEY set, skipping {label}", file=sys.stderr)
        return []
    videos = []
    page_token = None
    while True:
        url = (
            f"https://www.googleapis.com/youtube/v3/playlistItems"
            f"?part=snippet&maxResults=50"
            f"&playlistId={playlist_id}&key={YOUTUBE_API_KEY}"
        )
        if page_token:
            url += f"&pageToken={page_token}"
        data = api_get(url)
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            resource = snippet.get("resourceId", {})
            video_id = resource.get("videoId")
            if not video_id:
                continue
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
                "description": snippet.get("description", "")[:300],
            })
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return videos


def fetch_playlists():
    if not YOUTUBE_API_KEY:
        return []
    playlists = []
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
            playlists.append({
                "title": snippet.get("title", ""),
                "url": f"https://www.youtube.com/playlist?list={item['id']}",
                "playlist_id": item["id"],
                "item_count": item.get("contentDetails", {}).get("itemCount", 0),
                "thumbnail": (snippet.get("thumbnails", {}).get("high", {}) or snippet.get("thumbnails", {}).get("medium", {})).get("url", ""),
                "description": snippet.get("description", "")[:200],
            })
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return playlists


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


def save(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written {path} ({len(data)} items)" if isinstance(data, list) else f"Written {path}")


def fetch_channel_info():
    if not YOUTUBE_API_KEY:
        return None
    url = (
        f"https://www.googleapis.com/youtube/v3/channels"
        f"?part=snippet,brandingSettings"
        f"&id={CHANNEL_ID}"
        f"&key={YOUTUBE_API_KEY}"
    )
    data = api_get(url)
    items = data.get("items", [])
    if not items:
        return None
    item = items[0]
    snippet = item.get("snippet", {})
    branding = item.get("brandingSettings", {})
    thumbnails = snippet.get("thumbnails", {})
    avatar = (
        thumbnails.get("high", {}) or thumbnails.get("medium", {}) or thumbnails.get("default", {})
    ).get("url", "")
    return {
        "title": snippet.get("title", ""),
        "description": snippet.get("description", "")[:500],
        "custom_url": snippet.get("customUrl", ""),
        "avatar_url": avatar,
        "banner_url": branding.get("image", {}).get("bannerExternalUrl", ""),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def update_config_avatar(avatar_url):
    config_path = "_config.yml"
    with open(config_path) as f:
        content = f.read()
    marker = "avatar:"
    for line in content.splitlines():
        if line.startswith(marker):
            old_line = line
            break
    old_line = [l for l in content.splitlines() if l.startswith(marker)][0]
    new_line = f"avatar: {avatar_url}"
    if old_line.strip() == new_line.strip():
        return
    content = content.replace(old_line, new_line)
    with open(config_path, "w") as f:
        f.write(content)
    print(f"Updated avatar in _config.yml: {avatar_url}")


def main():
    print("Fetching YouTube uploads...")
    videos = fetch_uploads(UPLOADS_PLAYLIST_ID, "main channel uploads")
    save("youtube_main.json", {"videos": videos})

    print("Fetching YouTube VODs...")
    vods = fetch_uploads(VODS_PLAYLIST_ID, "VODs channel uploads")
    save("youtube_vods.json", {"videos": vods})

    print("Fetching YouTube playlists...")
    playlists = fetch_playlists()
    save("playlists.json", {"playlists": playlists})

    print("Fetching livestream status...")
    live = fetch_livestream()
    save("livestream.json", live or {"platform": None, "checked_at": datetime.now(timezone.utc).isoformat()})

    print("Fetching channel info...")
    info = fetch_channel_info()
    if info:
        save("site_meta.json", info)
        update_config_avatar(info.get("avatar_url", ""))


if __name__ == "__main__":
    main()