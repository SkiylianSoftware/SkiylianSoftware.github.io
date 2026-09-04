"""
Ensure local video thumbnails exist.

Covers a niche CI case: the _data cache (which now stores
/assets/img/thumbs/<id>.jpg for each video) can be restored without the
thumbnails directory (e.g. first run after this change, or a thumbs-cache
eviction). Walks youtube_main.json + youtube_vods.json and downloads any
thumbnail that's missing locally. fetch_youtube.py already caches images
during a normal fetch; this is just a safety net.

Ignores videos where the data still points at a remote URL (they fall back
to that URL at render time via the onerror attribute).
"""

import json
import os

import requests

DATA_DIR = "_data"
THUMB_DIR = os.path.join("assets", "img", "thumbs")
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
}


def main():
    video_ids = set()
    for name in ("youtube_main.json", "youtube_vods.json"):
        path = os.path.join(DATA_DIR, name)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            data = json.load(f)
        for v in data.get("videos", []):
            vid = v.get("video_id")
            if vid:
                video_ids.add(vid)

    os.makedirs(THUMB_DIR, exist_ok=True)
    fetched = 0
    for vid in sorted(video_ids):
        path = os.path.join(THUMB_DIR, f"{vid}.jpg")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            continue
        url = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
        try:
            resp = requests.get(url, timeout=15, headers=_HEADERS)
            resp.raise_for_status()
            if resp.content and not resp.headers.get("content-type", "").startswith("text/"):
                with open(path, "wb") as f:
                    f.write(resp.content)
                fetched += 1
        except Exception as e:
            print(f"  skip {vid}: {e}")
    print(f"Thumbnails ensured ({fetched} fetched; {len(video_ids)} known)")


if __name__ == "__main__":
    main()
