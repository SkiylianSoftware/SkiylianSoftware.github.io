import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import requests
import yaml

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
CHANNEL_ID = "UC4s4eXHuzj7OxwJXgiZgAYw"
UPLOADS_PLAYLIST_ID = "UU4s4eXHuzj7OxwJXgiZgAYw"
VODS_CHANNEL_ID = "UCC8qQOj7P2CWEcCDmOq0q7Q"
VODS_PLAYLIST_ID = "UUC8qQOj7P2CWEcCDmOq0q7Q"

DATA_DIR = "_data"
os.makedirs(DATA_DIR, exist_ok=True)

CONFIG_PATH = "_config.yml"
try:
    with open(CONFIG_PATH) as f:
        _cfg = yaml.safe_load(f)
    _rt = _cfg.get("recency_thresholds", {})
    CURRENT_DAYS = _rt.get("current_days", 90)
    RECENT_DAYS = _rt.get("recent_days", 365)
except Exception:
    CURRENT_DAYS = 90
    RECENT_DAYS = 365

GAME_LINKS_PATH = "_data/game_links.yml"
try:
    with open(GAME_LINKS_PATH) as f:
        _gl = yaml.safe_load(f) or {}
    ALIAS_MAP = {}
    for canonical, entry in _gl.items():
        if isinstance(entry, dict):
            for alias in entry.get("aliases", []):
                ALIAS_MAP[alias] = canonical
except Exception as e:
    print(f"Warning: could not load {GAME_LINKS_PATH}: {e}", file=sys.stderr)
    ALIAS_MAP = {}

CONTENT_TYPES_PATH = "_data/content_types.yml"
try:
    with open(CONTENT_TYPES_PATH) as f:
        CONTENT_TYPES = yaml.safe_load(f) or []
except Exception as e:
    print(f"Warning: could not load {CONTENT_TYPES_PATH}: {e}", file=sys.stderr)
    CONTENT_TYPES = []


def api_get(url):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def parse_duration(iso_duration):
    if not iso_duration:
        return 0
    seconds = 0
    import re

    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration)
    if m:
        h, mi, s = [int(g) if g else 0 for g in m.groups()]
        seconds = h * 3600 + mi * 60 + s
    return seconds


def fetch_video_details(video_ids):
    if not video_ids:
        return {}
    details = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        ids = ",".join(batch)
        url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=contentDetails,statistics,snippet"
            f"&id={ids}&key={YOUTUBE_API_KEY}"
        )
        data = api_get(url)
        for item in data.get("items", []):
            vid = item["id"]
            cd = item.get("contentDetails", {})
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            duration = cd.get("duration", "")
            details[vid] = {
                "duration": duration,
                "duration_seconds": parse_duration(duration),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "tags": snippet.get("tags", []),
            }
    return details


SERIES_RE = re.compile(r"^(?P<game>[^:]+):\s*(?P<series>.+?)#(?P<episode>\d+)\s*[-–]\s*(?P<subtitle>.+)$")
CONTENT_SERIES_RE = re.compile(r"^(?P<content_series>[^#]+?)\s*#\d+\s*[-–]\s*(?P<subtitle>.+)$")


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


def format_years(years):
    if not years:
        return ""
    years = sorted(int(y) for y in years)
    ranges = []
    start = end = years[0]
    for y in years[1:]:
        if y == end + 1:
            end = y
        else:
            ranges.append((start, end))
            start = end = y
    ranges.append((start, end))
    parts = []
    for s, e in ranges:
        parts.append(str(s) if s == e else f"{s}-{e}")
    return ", ".join(parts)


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
            videos.append(
                {
                    "title": snippet.get("title", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "video_id": video_id,
                    "thumbnail": thumbnail,
                    "published": snippet.get("publishedAt", ""),
                    "description": snippet.get("description", "")[:500],
                    "series": parse_series(snippet.get("title", "")),
                }
            )
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


def enrich_playlist_stats(playlists):
    if not YOUTUBE_API_KEY or not playlists:
        return playlists
    playlist_video_ids = {}
    for pl in playlists:
        pid = pl["playlist_id"]
        video_ids = []
        page_token = None
        while True:
            url = (
                f"https://www.googleapis.com/youtube/v3/playlistItems"
                f"?part=contentDetails"
                f"&playlistId={pid}&maxResults=50&key={YOUTUBE_API_KEY}"
            )
            if page_token:
                url += f"&pageToken={page_token}"
            try:
                data = api_get(url)
            except Exception:
                break
            for item in data.get("items", []):
                vid = item.get("contentDetails", {}).get("videoId", "")
                if vid:
                    video_ids.append(vid)
            page_token = data.get("nextPageToken")
            if not page_token:
                break
        playlist_video_ids[pid] = video_ids
    all_vids = list(set(vid for ids in playlist_video_ids.values() for vid in ids))
    video_details = {}
    for i in range(0, len(all_vids), 50):
        batch = all_vids[i : i + 50]
        ids = ",".join(batch)
        url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=contentDetails,statistics,snippet"
            f"&id={ids}&key={YOUTUBE_API_KEY}"
        )
        try:
            data = api_get(url)
        except Exception:
            continue
        for item in data.get("items", []):
            vid = item["id"]
            cd = item.get("contentDetails", {})
            dur = parse_duration(cd.get("duration", ""))
            stats = item.get("statistics", {})
            pub = item.get("snippet", {}).get("publishedAt", "")
            video_details[vid] = {
                "duration_seconds": dur,
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "published_at": pub,
            }
    for pl in playlists:
        pid = pl["playlist_id"]
        vids = playlist_video_ids.get(pid, [])
        pl["total_duration_seconds"] = sum(video_details.get(v, {}).get("duration_seconds", 0) for v in vids)
        pl["total_views"] = sum(video_details.get(v, {}).get("view_count", 0) for v in vids)
        pl["total_likes"] = sum(video_details.get(v, {}).get("like_count", 0) for v in vids)
        dates = [
            video_details.get(v, {}).get("published_at", "")
            for v in vids
            if video_details.get(v, {}).get("published_at")
        ]
        pl["last_updated"] = max(dates) if dates else pl.get("published", "")
    return playlists


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
            all_playlists.append(
                {
                    "title": snippet.get("title", ""),
                    "url": f"https://www.youtube.com/playlist?list={item['id']}",
                    "playlist_id": item["id"],
                    "item_count": item.get("contentDetails", {}).get("itemCount", 0),
                    "thumbnail": (
                        thumb.get("maxres", {})
                        or thumb.get("medium", {})
                        or thumb.get("high", {})
                        or thumb.get("default", {})
                    ).get("url", ""),
                    "description": snippet.get("description", ""),
                    "description_parts": snippet.get("description", "").split("\n"),
                    "published": snippet.get("publishedAt", ""),
                    "channel_title": snippet.get("channelTitle", ""),
                }
            )
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
        m = re.search(r"ytInitialData\s*=\s*({.*?});", text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                tabs = data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
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
        return any(p in text_lower for p in positives)
    except requests.RequestException:
        pass
    return False


def _high_res_banner(url):
    if not url:
        return ""
    url = re.sub(r"(?<=[=/])s\d+", "s2560", url)
    url = re.sub(r"(?<=[=/])w\d+", "w2560", url)
    if "s2560" not in url and "w2560" not in url:
        url += "=w2560"
    return url


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
    avatar = (thumbnails.get("high", {}) or thumbnails.get("medium", {}) or thumbnails.get("default", {})).get(
        "url", ""
    )
    memberships_available = check_youtube_memberships()
    return {
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "custom_url": snippet.get("customUrl", ""),
        "avatar_url": avatar,
        "banner_url": _high_res_banner(branding.get("image", {}).get("bannerExternalUrl", "")),
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
    old_line = [ln for ln in content.splitlines() if ln.startswith("avatar:")][0]
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


P3 = [3**i for i in range(13)]
P2 = [2**i for i in range(21)]
RND = [1, 10, 25, 50, 100, 250, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]

P3_MSG = {
    1: "The unitary state",
    3: "Three-body problem solved",
    9: "Nonary game complete",
    27: "Cube it!",
    81: "Trit-trit-trit!",
    243: "3^5 - Fifth power unlocked",
    729: "3^6 - One gross in balanced ternary",
    2187: "3^7 - Lucky sevens",
    6561: "3^8 - Octotrit",
    19683: "3^9 - Padovan sequence spotted",
    59049: "3^10 - Decitrit! Tenfold power!",
    177147: "3^11 - Ternary galaxy!",
    531441: "3^12 - Dozenal trit!",
}
P2_MSG = {
    2: "A pair!",
    4: "Four! Quadbit!",
    8: "Byte!",
    16: "Half-word!",
    32: "Word!",
    64: "Double-word!",
    128: "Kilobit!",
    256: "Byte plural!",
    512: "Half a K!",
    1024: "1K! A true kilobyte!",
    2048: "2K!",
    4096: "4K! Page boundary!",
    8192: "8K!",
    16384: "16K!",
    32768: "Half of 64K!",
    65536: "64K! Full address space!",
    131072: "128K! Expanded memory!",
    262144: "256K! High memory area!",
    524288: "512K! Extended memory!",
    1048576: "1M! Megabyte territory!",
}
RND_MSG = {
    10: "First double digits!",
    50: "Halfway to 100!",
    100: "Triple digits!",
    500: "Half a thousand!",
    1000: "The big 1K!",
    5000: "5K strong!",
    10000: "10K! Unreal!",
    50000: "50K! Halfway to 100K!",
    100000: "100K!!! Thank you!",
    500000: "Half a million!",
    1000000: "1 MILLION! Unbelievable!",
}


def _fmt_ms(m, b):
    return f"{m:,}: {b}" if b else f"{m:,} units!"


FORMAT_MS = _fmt_ms

MILESTONE_SPECS = [
    ("subs", P3, P3_MSG, FORMAT_MS),
    ("subs", P2, P2_MSG, FORMAT_MS),
    ("subs", RND, RND_MSG, FORMAT_MS),
    ("views", P3, P3_MSG, FORMAT_MS),
    ("views", P2, P2_MSG, FORMAT_MS),
    ("views", RND, RND_MSG, FORMAT_MS),
    ("videos", P3, P3_MSG, FORMAT_MS),
    ("videos", P2, P2_MSG, FORMAT_MS),
    ("videos", RND, RND_MSG, FORMAT_MS),
]

# All game milestone types use the combined P3 + P2 + RND threshold lists
# Sorted unique gives a nice spread: 1, 2, 3, 4, 8, 9, 10, 16, 25, 27, 32, 50, 64, 81, 100...
GAME_EP_THRESH = sorted(set(P3 + P2 + RND))
# Views and hours filter out very low thresholds
GAME_VIEW_THRESH = [m for m in sorted(set(P3 + P2 + RND)) if m >= 9]
GAME_HOUR_THRESH = [m for m in sorted(set(P3 + P2 + RND)) if m >= 3]
GAME_RETURN_THRESH = [m for m in sorted(set(P3 + P2 + RND)) if m >= 27]

GAME_DEFAULT = {
    "ep": "{{m}} episodes in {game}!",
    "views": "{{count}} views across {game}!",
    "hours": "{{hours}} hours in {game}!",
    "return": "Back to {game} after {{days}} days!",
}
GAME_THRESHOLDS = {
    "ep": GAME_EP_THRESH,
    "views": GAME_VIEW_THRESH,
    "hours": GAME_HOUR_THRESH,
    "return": GAME_RETURN_THRESH,
}
GAME_OVERRIDES = {
    "Kerbal Space Program": {
        "ep": {
            1: "First launch at KSC!",
            2: "Orbit achieved!",
            3: "Munar flyby complete!",
            4: "Sub-orbital tourism opened!",
            8: "Minmus landing!",
            9: "Duna transfer window!",
            10: "Duna landing!",
            16: "Interplanetary fleet assembled!",
            25: "Jool system arrival!",
            27: "Jool system fleet deployed!",
            32: "Eeloo reached!",
            50: "Kerbals across the solar system!",
            64: "Space station network established!",
            81: "Kerbals across the galaxy!",
            100: "Century of launches!",
        }
    },
    "Factorio": {
        "ep": {
            3: "Green science automated!",
            9: "Blue science online!",
            27: "Rocket silo constructed!",
            81: "Mega base operational!",
        }
    },
    "Minecraft": {
        "ep": {
            3: "Nether portal activated!",
            9: "Stronghold located!",
            27: "Ender Dragon defeated!",
            81: "Full beacon pyramid!",
        }
    },
    "Transport Fever": {
        "ep": {
            3: "Three lines running!",
            9: "Train network growing!",
            27: "Maglev network online!",
            81: "Transcontinental empire!",
        }
    },
    "Transport Fever 2": {
        "ep": {
            3: "Three lines running!",
            9: "Train network growing!",
            27: "Maglev network online!",
            81: "Transcontinental empire!",
        }
    },
    "Mars First Logistics": {
        "ep": {3: "Rover delivered!", 9: "Base camp established!", 27: "Three colonies linked!", 81: "Martian city!"}
    },
    "Station Flow": {
        "ep": {3: "Queue managed!", 9: "Station bustling!", 27: "Expansion complete!", 81: "Metroplex achieved!"}
    },
}
GAME_THRESHOLDS = {
    "ep": P3,
    "views": [27, 81, 243, 729, 2187, 6561],
    "hours": [3, 9, 27, 81, 243],
    "return": [27, 81, 243, 729],
}
# Per-game per-type overrides. Falls back to GAME_DEFAULT for any missing key.
GAME_OVERRIDES = {
    "Kerbal Space Program": {
        "ep": {
            3: "Mun flyby complete!",
            9: "Duna landing!",
            27: "Jool system fleet deployed!",
            81: "Kerbals across the galaxy!",
        }
    },
    "Factorio": {
        "ep": {
            3: "Green science automated!",
            9: "Blue science online!",
            27: "Rocket silo constructed!",
            81: "Mega base operational!",
        }
    },
    "Minecraft": {
        "ep": {
            3: "Nether portal activated!",
            9: "Stronghold located!",
            27: "Ender Dragon defeated!",
            81: "Full beacon pyramid!",
        }
    },
    "Transport Fever": {
        "ep": {
            3: "Three lines running!",
            9: "Train network growing!",
            27: "Maglev network online!",
            81: "Transcontinental empire!",
        }
    },
    "Transport Fever 2": {
        "ep": {
            3: "Three lines running!",
            9: "Train network growing!",
            27: "Maglev network online!",
            81: "Transcontinental empire!",
        }
    },
    "Mars First Logistics": {
        "ep": {3: "Rover delivered!", 9: "Base camp established!", 27: "Three colonies linked!", 81: "Martian city!"}
    },
    "Station Flow": {
        "ep": {3: "Queue managed!", 9: "Station bustling!", 27: "Expansion complete!", 81: "Metroplex achieved!"}
    },
}
GAME_RETURN_MSG_TMPL = "Back to {game} after {{days}} days!"
GAME_EP_OVERRIDE = {
    "Kerbal Space Program": {
        3: "Mun flyby complete!",
        9: "Duna landing!",
        27: "Jool system fleet deployed!",
        81: "Kerbals across the galaxy!",
    },
    "Factorio": {
        3: "Green science automated!",
        9: "Blue science online!",
        27: "Rocket silo constructed!",
        81: "Mega base operational!",
    },
    "Minecraft": {
        3: "Nether portal activated!",
        9: "Stronghold located!",
        27: "Ender Dragon defeated!",
        81: "Full beacon pyramid!",
    },
    "Transport Fever": {
        3: "Three lines running!",
        9: "Train network growing!",
        27: "Maglev network online!",
        81: "Transcontinental empire!",
    },
    "Transport Fever 2": {
        3: "Three lines running!",
        9: "Train network growing!",
        27: "Maglev network online!",
        81: "Transcontinental empire!",
    },
    "Mars First Logistics": {
        3: "Rover delivered!",
        9: "Base camp established!",
        27: "Three colonies linked!",
        81: "Martian city!",
    },
    "Station Flow": {3: "Queue managed!", 9: "Station bustling!", 27: "Expansion complete!", 81: "Metroplex achieved!"},
    "STATIONflow": {3: "Queue managed!", 9: "Station bustling!", 27: "Expansion complete!", 81: "Metroplex achieved!"},
}


def _parse_iso_date(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _detect_game_milestones(games, prev_reached, now, cutoff, all_videos=None):
    reached = {}
    current = {}
    # Build a map: game name -> sorted list of video publish dates
    game_dates = {}
    if all_videos:
        for v in all_videos:
            s = v.get("series", {})
            gname = (s or {}).get("game", "")
            pub = v.get("published", "")
            if gname and pub and len(pub) >= 10:
                game_dates.setdefault(gname, []).append(pub[:10])
        for gname in game_dates:
            game_dates[gname].sort()
    for gname, g in games.items():
        ep = g.get("episode_count", 0)
        gv = g.get("total_views", 0)
        gh = g.get("total_duration_seconds", 0) // 3600
        first = g.get("first_video", "")
        latest = g.get("latest_video", "")

        for gtype, thresholds, key_suffix, value in [
            ("ep", GAME_THRESHOLDS["ep"], "ep", ep),
            ("views", GAME_THRESHOLDS["views"], "views", gv),
            ("hours", GAME_THRESHOLDS["hours"], "hours", gh),
        ]:
            for m in sorted(thresholds, reverse=True):
                if value >= m:
                    key = f"game_{gname}_{key_suffix}_{m}"
                    override = GAME_OVERRIDES.get(gname, {}).get(gtype, {}).get(m)
                    if override:
                        msg = override
                    else:
                        tmpl = GAME_DEFAULT[gtype]
                        msg = (
                            tmpl.replace("{{m}}", str(m))
                            .replace("{{count}}", str(m))
                            .replace("{{hours}}", str(m))
                            .replace("{game}", gname)
                        )
                    if key not in prev_reached:
                        game_pub_dates = game_dates.get(gname, [])
                        if gtype == "ep" and len(game_pub_dates) >= m:
                            try:
                                dt = datetime.strptime(game_pub_dates[m - 1], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                                reached[key] = dt.isoformat()
                            except Exception:
                                reached[key] = now.isoformat()
                        else:
                            reached[key] = now.isoformat()
                        current[key] = {"type": f"game_{gtype}", "game": gname, "count": m, "message": msg}
                    elif (
                        prev_reached.get(key)
                        and _parse_iso_date(prev_reached[key])
                        and _parse_iso_date(prev_reached[key]) >= cutoff
                    ):
                        current[key] = {"type": f"game_{gtype}", "game": gname, "count": m, "message": msg}
                    break

        if first and latest:
            try:
                fd = datetime.fromisoformat(first.replace("Z", "+00:00"))
                ld = datetime.fromisoformat(latest.replace("Z", "+00:00"))
                gap_days = (ld - fd).days
                for m in sorted(GAME_THRESHOLDS["return"], reverse=True):
                    if gap_days >= m:
                        key = f"game_{gname}_return_{m}"
                        msg = GAME_DEFAULT["return"].replace("{game}", gname).replace("{{days}}", str(m))
                        if key not in prev_reached:
                            reached[key] = now.isoformat()
                            current[key] = {"type": "game_return", "game": gname, "count": m, "message": msg}
                        break
            except Exception:
                pass

    return reached, current


def detect_milestones(
    subs, views, videos_count, games_data=None, first_video_date=None, gh_data=None, twitch_data=None, all_videos=None
):
    prev = {}
    prev_path = os.path.join(DATA_DIR, "milestones.json")
    if os.path.exists(prev_path):
        try:
            with open(prev_path) as f:
                prev = json.load(f)
        except Exception:
            prev = {}

    prev_reached = prev.get("reached", {})

    # Migrate old key format (subs_10 → subs_rnd_10) to preserve historical timestamps
    for old_key in list(prev_reached.keys()):
        parts = old_key.split("_")
        if len(parts) == 2 and parts[0] in ("subs", "views", "videos"):
            try:
                int(parts[1])  # verify second part is a number
                new_key = f"{parts[0]}_rnd_{parts[1]}"
                if new_key not in prev_reached:
                    prev_reached[new_key] = prev_reached[old_key]
                del prev_reached[old_key]
            except ValueError:
                pass

    current = {}
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=14)
    values = {"subs": subs, "views": views, "videos": videos_count}
    priority_map = {"subs": 4, "views": 3, "videos": 2, "age": 1}

    # Load history once for accurate milestone dates
    _history = []
    try:
        hist_path = os.path.join(DATA_DIR, "history.json")
        if os.path.exists(hist_path):
            with open(hist_path) as f:
                _history = json.load(f)
            _history.sort(key=lambda e: e.get("date", ""))
    except Exception:
        pass

    def _first_reached(label, threshold):
        for entry in _history:
            ym = entry.get("youtube_main", {}) or {}
            val = ym.get(label, 0)
            if val >= threshold:
                try:
                    return datetime.strptime(entry["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except Exception:
                    break
        # Fallback: estimate from video publish dates for video count
        if label == "videos" and all_videos and threshold > 0:
            pub_dates = []
            for v in all_videos:
                p = v.get("published", "")
                if p and len(p) >= 10:
                    pub_dates.append(p[:10])
            pub_dates.sort()
            if len(pub_dates) >= threshold:
                try:
                    return datetime.strptime(pub_dates[threshold - 1], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except Exception:
                    pass
        return now

    for label, thresholds, msgs, formatter in MILESTONE_SPECS:
        value = values.get(label, 0)
        for m in sorted(thresholds, reverse=True):
            if value >= m:
                skey = f"{label}_{m}"
                if skey not in prev_reached:
                    reached_dt = _first_reached(label, m)
                    prev_reached[skey] = reached_dt.isoformat()
                    msg = formatter(m, msgs.get(m, ""))
                    print(f"New milestone: {msg}")
                break

    if first_video_date:
        try:
            fd = _parse_iso_date(first_video_date.replace("Z", "+00:00"))
            if fd:
                age_days = (now - fd).days
                for m in [3, 9, 27, 81, 243, 729, 2187, 6561]:
                    if age_days >= m:
                        key = f"age_{m}"
                        if key not in prev_reached:
                            prev_reached[key] = now.isoformat()
                            print(f"New milestone: channel age {m} days")
                        break
        except Exception:
            pass

    if games_data:
        game_reached, game_current = _detect_game_milestones(
            games_data, prev_reached, now, cutoff, all_videos=all_videos
        )
        prev_reached.update(game_reached)
        current.update(game_current)

    for label, thresholds, msgs, formatter in MILESTONE_SPECS:
        value = values.get(label, 0)
        for m in sorted(thresholds, reverse=True):
            if value >= m:
                skey = f"{label}_{m}"
                reached_at = prev_reached.get(skey, "")
                if reached_at and _parse_iso_date(reached_at) and _parse_iso_date(reached_at) >= cutoff:
                    msg = formatter(m, msgs.get(m, ""))
                    p = priority_map.get(label, 0)
                    current[skey + f"_{p}"] = {"type": label, "count": m, "message": msg, "priority": p}
                break

    if first_video_date:
        fd = _parse_iso_date(first_video_date.replace("Z", "+00:00"))
        if fd:
            age_days = (now - fd).days
            for m in [3, 9, 27, 81, 243, 729, 2187, 6561]:
                if age_days >= m:
                    key = f"age_{m}"
                    reached_at = prev_reached.get(key, "")
                    if reached_at and _parse_iso_date(reached_at) and _parse_iso_date(reached_at) >= cutoff:
                        msg = {
                            3: "3 days old!",
                            9: "9 days!",
                            27: "27 days! A cubic month!",
                            81: "81 days!",
                            243: "243 days old!",
                            729: "729 days!",
                            2187: "2187 days!",
                            6561: "6561 days!",
                        }.get(m, f"{m} days!")
                        current[key + "_1"] = {"type": "age", "count": m, "message": msg, "priority": 1}
                    break

    expired = [k for k, v in prev_reached.items() if _parse_iso_date(v) and _parse_iso_date(v) < cutoff]
    for k in expired:
        del prev_reached[k]

    active = [v for v in current.values() if v.get("priority", 0) > 0]
    best = max(active, key=lambda x: (x["priority"], x["count"])) if active else {}
    save("milestones.json", {"current": best, "reached": prev_reached})


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
        if days < CURRENT_DAYS:
            status = "current"
        elif days < RECENT_DAYS:
            status = "recent"
        else:
            status = "historical"
        recency[name] = {"status": status, "episodes": data["episode_count"]}
    return recency


def _extract_content_series(title):
    m = CONTENT_SERIES_RE.match(title)
    return m.group("content_series").strip() if m else None


def _extract_steam_appid(steam_url):
    if not steam_url:
        return None
    parts = steam_url.split("/")
    for i, p in enumerate(parts):
        if p == "app" and i + 1 < len(parts):
            return parts[i + 1]
    return None


def _extract_image_color(url):
    """Download an image and return its dominant colour as a hex string."""
    try:
        from io import BytesIO

        from PIL import Image

        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        small = img.resize((1, 1))
        r, g, b = small.getpixel((0, 0))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return None


def _categorize_non_game(video, content_types):
    title = video.get("title", "")
    tags = [t.lower() for t in video.get("tags", [])]
    for ct in content_types:
        for pattern in ct.get("patterns", []):
            if re.search(pattern, title, re.IGNORECASE):
                return ct["name"]
        for tag_pattern in ct.get("tags", []):
            if tag_pattern.lower() in tags:
                return ct["name"]
    for ct in content_types:
        if ct.get("catch_all"):
            return ct["name"]
    return "Misc"


def compute_game_stats(videos, alias_map=None, content_types=None):
    games = {}
    non_game_total = {
        "episode_count": 0,
        "total_duration_seconds": 0,
        "total_views": 0,
        "total_likes": 0,
        "first_video": None,
        "latest_video": None,
    }
    non_game_categories = {}
    for v in videos:
        s = v.get("series")
        published = v.get("published", "")
        if s and s.get("game"):
            game = s["game"]
            if alias_map and game in alias_map:
                game = alias_map[game]
            if game not in games:
                games[game] = {
                    "episode_count": 0,
                    "total_duration_seconds": 0,
                    "total_views": 0,
                    "total_likes": 0,
                    "first_video": None,
                    "latest_video": None,
                    "series": set(),
                    "series_data": {},
                    "original_names": [game],
                }
            g = games[game]
            g["episode_count"] += 1
            g["total_duration_seconds"] += v.get("duration_seconds", 0)
            g["total_views"] += v.get("view_count", 0)
            g["total_likes"] += v.get("like_count", 0)
            if published:
                if g["first_video"] is None or published < g["first_video"]:
                    g["first_video"] = published
                if g["latest_video"] is None or published > g["latest_video"]:
                    g["latest_video"] = published
            series_name = s.get("series_name", "")
            g["series"].add(series_name)
            original_name = s["game"]
            if original_name not in g["original_names"]:
                g["original_names"].append(original_name)
            if series_name not in g["series_data"]:
                g["series_data"][series_name] = {
                    "episode_count": 0,
                    "first_video": None,
                    "latest_video": None,
                    "active_years": set(),
                }
            sd = g["series_data"][series_name]
            sd["episode_count"] += 1
            if published:
                if sd["first_video"] is None or published < sd["first_video"]:
                    sd["first_video"] = published
                if sd["latest_video"] is None or published > sd["latest_video"]:
                    sd["latest_video"] = published
                sd["active_years"].add(published[:4])
        else:
            non_game_total["episode_count"] += 1
            non_game_total["total_duration_seconds"] += v.get("duration_seconds", 0)
            non_game_total["total_views"] += v.get("view_count", 0)
            non_game_total["total_likes"] += v.get("like_count", 0)
            if published:
                if non_game_total["first_video"] is None or published < non_game_total["first_video"]:
                    non_game_total["first_video"] = published
                if non_game_total["latest_video"] is None or published > non_game_total["latest_video"]:
                    non_game_total["latest_video"] = published

            if content_types:
                cat_name = _categorize_non_game(v, content_types)
                if cat_name not in non_game_categories:
                    non_game_categories[cat_name] = {
                        "episode_count": 0,
                        "total_duration_seconds": 0,
                        "total_views": 0,
                        "total_likes": 0,
                        "first_video": None,
                        "latest_video": None,
                        "series_data": {},
                    }
                cat = non_game_categories[cat_name]
                cat["episode_count"] += 1
                cat["total_duration_seconds"] += v.get("duration_seconds", 0)
                cat["total_views"] += v.get("view_count", 0)
                cat["total_likes"] += v.get("like_count", 0)
                if published:
                    if cat["first_video"] is None or published < cat["first_video"]:
                        cat["first_video"] = published
                    if cat["latest_video"] is None or published > cat["latest_video"]:
                        cat["latest_video"] = published

                content_series = _extract_content_series(v.get("title", ""))
                if not content_series:
                    content_series = v.get("title", "")
                if content_series not in cat["series_data"]:
                    cat["series_data"][content_series] = {
                        "episode_count": 0,
                        "first_video": None,
                        "latest_video": None,
                        "active_years": set(),
                    }
                csd = cat["series_data"][content_series]
                csd["episode_count"] += 1
                if published:
                    if csd["first_video"] is None or published < csd["first_video"]:
                        csd["first_video"] = published
                    if csd["latest_video"] is None or published > csd["latest_video"]:
                        csd["latest_video"] = published
                    csd["active_years"].add(published[:4])

    _gl_links = {}
    try:
        with open(GAME_LINKS_PATH) as f:
            _gl_links = yaml.safe_load(f) or {}
    except Exception:
        pass

    now = datetime.now(timezone.utc)
    result = {}
    for name, g in sorted(games.items(), key=lambda x: x[1].get("latest_video", ""), reverse=True):
        g["series"] = sorted(g["series"])
        for _sname, sd in g.get("series_data", {}).items():
            sd["active_years"] = format_years(sd["active_years"])
        latest = g.get("latest_video")
        if latest:
            try:
                dt = datetime.fromisoformat(latest.replace("Z", "+00:00"))
                delta = now - dt
                if delta <= timedelta(days=CURRENT_DAYS):
                    g["status"] = "current"
                elif delta <= timedelta(days=RECENT_DAYS):
                    g["status"] = "recent"
                else:
                    g["status"] = "historical"
            except Exception:
                g["status"] = "historical"
        else:
            g["status"] = "historical"
        result[name] = g

        if not g.get("accent_color"):
            gl_entry = _gl_links.get(name, {}) if isinstance(_gl_links, dict) else {}
            img_url = gl_entry.get("icon") if isinstance(gl_entry, dict) else None
            if not img_url and isinstance(gl_entry, dict):
                appid = _extract_steam_appid(gl_entry.get("steam", ""))
                if appid:
                    img_url = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/header.jpg"
            if img_url:
                color = _extract_image_color(img_url)
                if color:
                    result[name]["accent_color"] = color

    if content_types:
        ordered = {}
        for ct in content_types:
            n = ct["name"]
            if n in non_game_categories:
                ordered[n] = non_game_categories.pop(n)
        ordered.update(non_game_categories)
    else:
        ordered = non_game_categories

    for _cat_name, cat in ordered.items():
        for _cs_name, csd in cat.get("series_data", {}).items():
            csd["active_years"] = format_years(csd["active_years"])

    return {
        "games": result,
        "non_game": {
            "total": non_game_total,
            "categories": ordered,
        },
    }


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

    all_videos = (videos or []) + (vods or [])
    game_stats = None
    if all_videos:
        game_stats = compute_game_stats(all_videos, alias_map=ALIAS_MAP, content_types=CONTENT_TYPES)
        save("games.json", game_stats)

    print("Fetching YouTube playlists...")
    playlists = fetch_playlists()
    if playlists is not None:
        print("Enriching playlist stats...")
        playlists = enrich_playlist_stats(playlists)
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

    first_video_date = None
    if all_videos:
        dates = [v.get("published") for v in all_videos if v.get("published")]
        if dates:
            first_video_date = min(dates)

    detect_milestones(
        info.get("subscriber_count", 0),
        info.get("view_count", 0),
        info.get("video_count", 0),
        games_data=game_stats.get("games") if all_videos else None,
        first_video_date=first_video_date,
        all_videos=all_videos,
    )


if __name__ == "__main__":
    main()
