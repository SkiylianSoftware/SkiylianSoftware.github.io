import contextlib
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import requests
import yaml
from common import (
    ALIAS_MAP,
    DATA_DIR,
    GAME_THRESHOLDS,
    MILESTONE_SPECS,
    VALID_GAMES,
)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
CHANNEL_ID = "UC4s4eXHuzj7OxwJXgiZgAYw"
UPLOADS_PLAYLIST_ID = "UU4s4eXHuzj7OxwJXgiZgAYw"
VODS_CHANNEL_ID = "UCC8qQOj7P2CWEcCDmOq0q7Q"
VODS_PLAYLIST_ID = "UUC8qQOj7P2CWEcCDmOq0q7Q"

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
                "comment_count": int(stats.get("commentCount", 0)),
                "tags": snippet.get("tags", []),
                "game": (snippet.get("gameDetails") or {}).get("gameTitle", ""),
            }
    return details


PIPE_FULL_RE = re.compile(r"^(?P<subtitle>.+?)\s*\|\s*(?P<series>[^#]+?)\s*#\s*(?P<episode>\d+)\s*\|\s*(?P<game>.+)$")
PIPE_NO_GAME_RE = re.compile(r"^(?P<subtitle>.+?)\s*\|\s*(?P<series>[^#]+?)\s*#\s*(?P<episode>\d+)$")
PIPE_GAME_ONLY_RE = re.compile(r"^(?P<subtitle>.+?)\s*\|\s*(?P<game>.+)$")
SERIES_RE = re.compile(
    r"^(?P<game>[^:]+?):\s*(?P<series>[^\s#][^#]*?)\s*#\s*(?P<episode>\d+)\s*[-–]\s*(?P<subtitle>.+)$"
)
SERIES_NOSUB_RE = re.compile(r"^(?P<game>[^:]+?):\s*(?P<series>[^\s#][^#]*?)\s*#\s*(?P<episode>\d+)\s*$")
GAME_COLON_EP_SUB_RE = re.compile(r"^(?P<game>[^:]+?):\s*#\s*(?P<episode>\d+)\s*[-–]\s*(?P<subtitle>.+)$")
GAME_COLON_EP_RE = re.compile(r"^(?P<game>[^:]+?):\s*#\s*(?P<episode>\d+)\s*$")
GAME_EP_SUB_RE = re.compile(r"^(?P<game>[^:#]+?)\s*#\s*(?P<episode>\d+)\s*[-–]\s*(?P<subtitle>.+)$")
GAME_EP_RE = re.compile(r"^(?P<game>[^:#]+?)\s*#\s*(?P<episode>\d+)\s*$")
GAME_COLON_RE = re.compile(r"^(?P<game>[^:]+?):\s*(?P<title>.+)$")
CONTENT_SERIES_RE = re.compile(r"^(?P<content_series>[^#]+?)\s*#\d+\s*[-–]\s*(?P<subtitle>.+)$")


def parse_series(title):
    for regex, has_series, has_sub in [
        (PIPE_FULL_RE, True, True),
        (PIPE_NO_GAME_RE, True, True),
        (PIPE_GAME_ONLY_RE, False, True),
        (SERIES_RE, True, True),
        (SERIES_NOSUB_RE, True, False),
        (GAME_COLON_EP_SUB_RE, False, True),
        (GAME_COLON_EP_RE, False, False),
        (GAME_EP_SUB_RE, False, True),
        (GAME_EP_RE, False, False),
        (GAME_COLON_RE, False, False),
    ]:
        m = regex.match(title)
        if m:
            result = {
                "game": m.group("game").strip() if "game" in regex.groupindex else "",
                "series_name": m.group("series").strip() if has_series else "",
                "episode_number": int(m.group("episode")) if "episode" in regex.groupindex else 0,
                "episode_title": m.group("subtitle").strip() if has_sub else "",
            }
            if regex == GAME_COLON_RE:
                result["episode_title"] = m.group("title").strip()
            if not result["game"] and result["series_name"]:
                result["game"] = result["series_name"]
            return result
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
                thumbnails.get("high", {})
                or thumbnails.get("medium", {})
                or thumbnails.get("standard", {})
                or thumbnails.get("maxres", {})
                or thumbnails.get("default", {})
            ).get("url", "")
            videos.append(
                {
                    "title": snippet.get("title", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "video_id": video_id,
                    "thumbnail": thumbnail,
                    "published": snippet.get("publishedAt", ""),
                    "description": snippet.get("description", ""),
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
            d = details[vid]
            v.update(d)
            # Prefer the game attached in YouTube Studio; fall back to the title parse
            if d.get("game") and v.get("series"):
                v["series"]["game"] = d["game"]
                v["series"]["game_source"] = "api"
        # Cache the thumbnail locally (same-origin, CI-cached)
        if v.get("thumbnail"):
            v["thumbnail"] = _thumbnail_local(v["video_id"], v["thumbnail"])

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


PLAYLIST_COVER_DIR = os.path.join("assets", "img", "playlists")
THUMB_DIR = os.path.join("assets", "img", "thumbs")


def _yt_headers():
    """Headers + consent cookies so the playlist page scrape also works from EU IPs."""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "CONSENT=YES+cb.20210328-17-p0.en+FX+; SOCS=CAISEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg",
    }


def _fetch_playlist_cover(pid):
    """Scrape the YouTube playlist page for the signed pl_c cover URL."""
    try:
        resp = requests.get(
            f"https://www.youtube.com/playlist?list={pid}",
            timeout=10,
            headers=_yt_headers(),
        )
        m = re.search(r'/pl_c/[^"\'&?]+/studio_square_thumbnail\.jpg\?[^"\' ]+', resp.text)
        if m:
            return "https://i.ytimg.com" + m.group(0).replace("&amp;", "&")
    except Exception:
        pass
    return ""


def _download_playlist_cover(pid, cover_url):
    """Download the cover into the site assets so the signed pl_c URL can't expire."""
    if not cover_url:
        return ""
    try:
        os.makedirs(PLAYLIST_COVER_DIR, exist_ok=True)
        path = os.path.join(PLAYLIST_COVER_DIR, f"{pid}.jpg")
        resp = requests.get(cover_url, timeout=15, headers=_yt_headers())
        resp.raise_for_status()
        if not resp.content or resp.headers.get("content-type", "").startswith("text/"):
            return ""
        with open(path, "wb") as f:
            f.write(resp.content)
        return f"/{PLAYLIST_COVER_DIR}/{pid}.jpg"
    except Exception:
        return ""


def _thumbnail_local(video_id, remote_url):
    """Cache a video thumbnail into site assets so every page load is same-origin.

    Returns a local /assets/img/thumbs/<id>.jpg path when the download
    succeeds, falling back to the remote URL on any error. CI caches the
    thumbs directory so we don't re-download on every run.
    """
    if not remote_url or not video_id:
        return remote_url
    try:
        os.makedirs(THUMB_DIR, exist_ok=True)
        path = os.path.join(THUMB_DIR, f"{video_id}.jpg")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            resp = requests.get(remote_url, timeout=15, headers=_yt_headers())
            resp.raise_for_status()
            if not resp.content or resp.headers.get("content-type", "").startswith("text/"):
                return remote_url
            with open(path, "wb") as f:
                f.write(resp.content)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return f"/{THUMB_DIR}/{video_id}.jpg"
    except Exception:
        pass
    return remote_url


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
            api_thumb = (
                thumb.get("maxres", {}) or thumb.get("medium", {}) or thumb.get("high", {}) or thumb.get("default", {})
            ).get("url", "")
            cover = _fetch_playlist_cover(item["id"])
            cover_local = _download_playlist_cover(item["id"], cover)
            all_playlists.append(
                {
                    "title": snippet.get("title", ""),
                    "url": f"https://www.youtube.com/playlist?list={item['id']}",
                    "playlist_id": item["id"],
                    "item_count": item.get("contentDetails", {}).get("itemCount", 0),
                    "thumbnail": cover_local or api_thumb,
                    "thumbnail_fallback": api_thumb,
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


def _parse_iso_date(s):
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
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
            gname = ALIAS_MAP.get((s or {}).get("game", ""), (s or {}).get("game", ""))
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
                    tmpl = {
                        "ep": "{{m}} episodes in {game}",
                        "views": "{{count}} views across {game}",
                        "hours": "{{hours}} hours in {game}",
                    }[gtype]
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
                        msg = f"Back to {gname} after {m} days"
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

    # Debug: show video_first keys before stripping
    _vf_before = [k for k in prev_reached if "video_first" in k]
    if _vf_before:
        print(f"  DEBUG fetch_youtube: video_first keys before strip ({len(_vf_before)}):")
        for _k in sorted(_vf_before):
            print(f"    {_k!r}: {prev_reached[_k]}")

    # Strip stale _0 and empty-threshold keys (e.g. video_first_likes_0, video_first_likes_)
    _stripped = []
    for _k in list(prev_reached.keys()):
        if _k.endswith("_0") or _k.endswith("_"):
            _stripped.append(_k)
            del prev_reached[_k]
    if _stripped:
        print(f"  DEBUG fetch_youtube: stripped {len(_stripped)} stale keys: {_stripped}")

    # Debug: show video_first keys after stripping
    _vf_after = [k for k in prev_reached if "video_first" in k]
    if _vf_after:
        print(f"  DEBUG fetch_youtube: video_first keys after strip ({len(_vf_after)}):")
        for _k in sorted(_vf_after):
            print(f"    {_k!r}: {prev_reached[_k]}")

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
        av = all_videos
        print(f"  fr {label}={threshold}: av type={type(av).__name__} len={len(av) if av else 0}", flush=True)
        if label == "videos" and av and threshold > 0:
            pub_dates = []
            for v in all_videos:
                p = v.get("published", "")
                if p and len(p) >= 10:
                    pub_dates.append(p[:10])
            pub_dates.sort()
            if pub_dates:
                nth = pub_dates[threshold - 1] if len(pub_dates) >= threshold else "N/A"
                print(f"  fr videos={threshold}: {len(pub_dates)} dates, first={pub_dates[0]}, nth={nth}")
            else:
                print(f"  fr videos={threshold}: no dates (all_videos={len(all_videos)})")
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

    # Backfill existing milestones that have wrong (today) dates
    for skey in list(prev_reached.keys()):
        stored = prev_reached.get(skey, "")
        stored_dt = _parse_iso_date(stored)
        if not stored_dt or abs((stored_dt - now).total_seconds()) > 3600 * 24:
            continue  # already has a historical date
        # Extract value from key like subs_p3_27, views_rnd_5000, etc.
        try:
            m = int(skey.rsplit("_", 1)[1])
        except (ValueError, IndexError):
            continue
        for label in ("subs", "views", "videos"):
            if skey.startswith(label):
                better = _first_reached(label, m)
                if better:
                    diff = (stored_dt - better).days
                    print(f"  backfill {skey}: stored={stored_dt.date()}, better={better.date()}, diff={diff}d")
                if better and better < stored_dt:
                    prev_reached[skey] = better.isoformat()
                    print(f"  Backdated {skey} from {stored_dt.date()} to {better.date()}")
                break

    active = [v for v in current.values() if v.get("priority", 0) > 0]
    best = max(active, key=lambda x: (x["priority"], x["count"])) if active else {}
    _site_hash = prev.get("_site_hash") or ""
    if prev_reached:
        with contextlib.suppress(Exception), open("_data/youtube_main.json", "rb") as _f:
            _site_hash = hashlib.md5(_f.read()).hexdigest()
    save("milestones.json", {"current": best, "reached": prev_reached, "_schema_version": 1, "_site_hash": _site_hash})


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


def compute_game_stats(videos, alias_map=None, content_types=None, valid_games=None):
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

    def _add_to_non_game(v, cat_name):
        non_game_total["episode_count"] += 1
        non_game_total["total_duration_seconds"] += v.get("duration_seconds", 0)
        non_game_total["total_views"] += v.get("view_count", 0)
        non_game_total["total_likes"] += v.get("like_count", 0)
        published = v.get("published", "")
        if published:
            if non_game_total["first_video"] is None or published < non_game_total["first_video"]:
                non_game_total["first_video"] = published
            if non_game_total["latest_video"] is None or published > non_game_total["latest_video"]:
                non_game_total["latest_video"] = published
        if cat_name not in non_game_categories:
            non_game_categories[cat_name] = {
                "episode_count": 0,
                "total_duration_seconds": 0,
                "total_views": 0,
                "total_likes": 0,
                "total_comments": 0,
                "first_video": None,
                "latest_video": None,
                "series_data": {},
            }
        cat = non_game_categories[cat_name]
        cat["episode_count"] += 1
        cat["total_duration_seconds"] += v.get("duration_seconds", 0)
        cat["total_views"] += v.get("view_count", 0)
        cat["total_likes"] += v.get("like_count", 0)
        cat["total_comments"] += v.get("comment_count", 0)
        if published:
            if cat["first_video"] is None or published < cat["first_video"]:
                cat["first_video"] = published
            if cat["latest_video"] is None or published > cat["latest_video"]:
                cat["latest_video"] = published

    for v in videos:
        s = v.get("series")
        published = v.get("published", "")
        if s and s.get("game"):
            game = s["game"]
            if alias_map and game in alias_map:
                game = alias_map[game]
            # Skip videos whose game name isn't in valid_games (non-game content falsely detected as game)
            # unless the game came from YouTube's API (gameDetails), which is authoritative
            if valid_games and game not in valid_games and s.get("game_source") != "api":
                cat_name = "Misc"
                if content_types:
                    for ct in content_types:
                        if ct.get("catch_all"):
                            continue
                        title = v.get("title", "")
                        for pattern in ct.get("patterns", []):
                            if re.search(pattern, title, re.IGNORECASE):
                                cat_name = ct["name"]
                                break
                        if cat_name != "Misc":
                            break
                        if not cat_name or cat_name == "Misc":
                            for tag_pattern in ct.get("tags", []):
                                tag_lower = tag_pattern.lower()
                                if tag_lower in [t.lower() for t in v.get("tags", [])]:
                                    cat_name = ct["name"]
                                    break
                        if cat_name != "Misc":
                            break
                _add_to_non_game(v, cat_name)
                continue
            if game not in games:
                games[game] = {
                    "episode_count": 0,
                    "total_duration_seconds": 0,
                    "total_views": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "first_video": None,
                    "latest_video": None,
                    "series": set(),
                    "series_data": {},
                    "original_names": [game],
                    "active_years": set(),
                }
            g = games[game]
            g["episode_count"] += 1
            g["total_duration_seconds"] += v.get("duration_seconds", 0)
            g["total_views"] += v.get("view_count", 0)
            g["total_likes"] += v.get("like_count", 0)
            g["total_comments"] += v.get("comment_count", 0)
            if published:
                if g["first_video"] is None or published < g["first_video"]:
                    g["first_video"] = published
                if g["latest_video"] is None or published > g["latest_video"]:
                    g["latest_video"] = published
                g["active_years"].add(published[:4])
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
                        "total_comments": 0,
                        "first_video": None,
                        "latest_video": None,
                        "series_data": {},
                    }
                cat = non_game_categories[cat_name]
                cat["episode_count"] += 1
                cat["total_duration_seconds"] += v.get("duration_seconds", 0)
                cat["total_views"] += v.get("view_count", 0)
                cat["total_likes"] += v.get("like_count", 0)
                cat["total_comments"] += v.get("comment_count", 0)
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
        with open("_data/game_links.yml") as f:
            _gl_links = yaml.safe_load(f) or {}
    except Exception:
        pass

    now = datetime.now(timezone.utc)
    result = {}
    for name, g in sorted(games.items(), key=lambda x: x[1].get("latest_video", ""), reverse=True):
        g["series"] = sorted(g["series"])
        for _sname, sd in g.get("series_data", {}).items():
            sd["active_years"] = format_years(sd["active_years"])
        # Game-level activity: sorted list of years for the activity bars
        ay = sorted(int(x) for x in g.get("active_years", set()))
        g["active_years"] = [str(x) for x in ay]
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
        # Per-series episode bar data for the Games page sidebar
        series_bars = []
        _max_ep = max((sd.get("episode_count", 0) for sd in g.get("series_data", {}).values()), default=0)
        for _sn, _sd in g.get("series_data", {}).items():
            _ec = _sd.get("episode_count", 0)
            _pct = round(_ec / _max_ep * 100) if _max_ep > 0 else 0
            series_bars.append({"name": _sn, "count": _ec, "pct": _pct})
        g["series_bars"] = series_bars
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


def compute_twitch_game_stats():
    """Aggregate game stats from Twitch VODs and clips.

    Games that are streamed but never uploaded to YouTube should still
    appear on the Games page. VODs and clips both carry a game_name (the
    Twitch category at broadcast time).
    """
    stats = {}
    for fname in ("twitch_vods.json", "twitch_clips.json"):
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception:
            continue
        items = data.get("videos") if fname == "twitch_vods.json" else data.get("clips", [])
        if not items:
            continue
        for item in items:
            gname = item.get("game_name") or item.get("game") or "Misc"
            if gname in ("", "Just Chatting", "Science & Technology", "Software and Game Development"):
                gname = "Misc"
            if gname not in stats:
                stats[gname] = {
                    "episode_count": 0,
                    "total_duration_seconds": 0,
                    "total_views": 0,
                    "first_video": None,
                    "latest_video": None,
                    "active_years": set(),
                    "series_data": {},
                }
            g = stats[gname]
            g["episode_count"] += 1
            g["total_duration_seconds"] += item.get("duration_seconds", 0)
            g["total_views"] += item.get("view_count", 0)
            published = item.get("published") or item.get("created_at") or item.get("started_at") or ""
            if published:
                if g["first_video"] is None or published < g["first_video"]:
                    g["first_video"] = published
                if g["latest_video"] is None or published > g["latest_video"]:
                    g["latest_video"] = published
                g["active_years"].add(published[:4])
            # A pseudo-series per game so series pages have something to show
            sname = gname
            if sname not in g["series_data"]:
                g["series_data"][sname] = {
                    "episode_count": 0,
                    "first_video": None,
                    "latest_video": None,
                    "active_years": set(),
                }
            sd = g["series_data"][sname]
            sd["episode_count"] += 1
            if published:
                if sd["first_video"] is None or published < sd["first_video"]:
                    sd["first_video"] = published
                if sd["latest_video"] is None or published > sd["latest_video"]:
                    sd["latest_video"] = published
                sd["active_years"].add(published[:4])

    # Convert active_years sets and drop empty extra
    for g in stats.values():
        g["active_years"] = format_years(g["active_years"])
        for sd in g["series_data"].values():
            sd["active_years"] = format_years(sd["active_years"])
        g["series"] = list(g["series_data"].keys())
    return stats


def main():
    print("Fetching YouTube uploads...")
    videos = fetch_uploads(UPLOADS_PLAYLIST_ID, "main channel uploads")
    if videos is not None:
        series_recency = compute_series_recency(videos)
        d = {"videos": videos, "series_recency": series_recency, "_schema_version": 1}
        save("youtube_main.json", d)

    print("Fetching YouTube VODs...")
    vods = fetch_uploads(VODS_PLAYLIST_ID, "VODs channel uploads")
    if vods is not None:
        for v in vods:
            v["platform"] = "youtube"
        d = {"videos": vods, "_schema_version": 1}
        save("youtube_vods.json", d)

    all_videos = (videos or []) + (vods or [])
    game_stats = None
    if all_videos:
        game_stats = compute_game_stats(
            all_videos, alias_map=ALIAS_MAP, content_types=CONTENT_TYPES, valid_games=VALID_GAMES
        )
        game_stats["_schema_version"] = 1

        # Merge in Twitch-sourced game stats (games played on stream but
        # never uploaded to YouTube). This ensures stream-only games appear
        # on the Games page and get series pages alongside video games.
        twitch_games = compute_twitch_game_stats()
        for gname, gdata in twitch_games.items():
            if gname in game_stats.get("games", {}):
                existing = game_stats["games"][gname]
                existing["episode_count"] += gdata.get("episode_count", 0)
                existing["total_duration_seconds"] += gdata.get("total_duration_seconds", 0)
                existing["total_views"] += gdata.get("total_views", 0)
                if not existing.get("latest_video") or (
                    gdata.get("latest_video") and gdata["latest_video"] > existing["latest_video"]
                ):
                    existing["latest_video"] = gdata.get("latest_video")
                if not existing.get("first_video") or (
                    gdata.get("first_video") and gdata["first_video"] < existing["first_video"]
                ):
                    existing["first_video"] = gdata.get("first_video")
                existing.setdefault("series_data", {}).update(gdata.get("series_data", {}))
                existing.setdefault("stream_count", 0)
                existing["stream_count"] += gdata.get("episode_count", 0)
                existing.setdefault("source", "video")
            else:
                gdata["source"] = "twitch"
                gdata.setdefault("stream_count", gdata.get("episode_count", 0))
                gdata["series"] = list(gdata.get("series_data", {}).keys())
                game_stats.setdefault("games", {})[gname] = gdata

        save("games.json", game_stats)

    print("Fetching YouTube playlists...")
    playlists = fetch_playlists()
    if playlists is not None:
        print("Enriching playlist stats...")
        playlists = enrich_playlist_stats(playlists)
        d = {"playlists": playlists, "_schema_version": 1}
        save("playlists.json", d)

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

    info["_schema_version"] = 1
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
