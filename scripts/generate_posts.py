"""
Generate Jekyll _posts from YouTube video and VOD data for the RSS feed.

Each video/VOD gets a short post with title, date, description, and a link.
This populates feed.xml so subscribers can see new content in their feed reader.
"""

import json
import os
from datetime import datetime, timezone

DATA_DIR = "_data"
POSTS_DIR = "_posts"
os.makedirs(POSTS_DIR, exist_ok=True)


def read_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def write_post(filename, frontmatter, body):
    path = os.path.join(POSTS_DIR, filename)
    with open(path, "w") as f:
        f.write("---\n")
        for k, v in frontmatter.items():
            f.write(f"{k}: {v}\n")
        f.write("---\n\n")
        f.write(body)
    print(f"  {path}")


def generate_video_posts(videos, label, channel_url):
    if not videos:
        return
    for v in videos:
        vid = v.get("video_id", "")
        title = v.get("title", "Untitled")
        published = v.get("published", "")
        desc = v.get("description", "")
        series = v.get("series", {})
        game = series.get("game", "") if series else ""

        if not published or not vid:
            continue

        date = published[:10]
        slug = f"{date}-{vid}"
        filename = f"{slug}.md"

        category = label.lower()
        tags = []
        if game:
            tags.append(game)
        sname = series.get("series_name", "") if series else ""
        if sname:
            tags.append(sname)

        short_desc = (desc[:200] + "...") if desc and len(desc) > 200 else (desc or "No description available.")

        frontmatter = {
            "title": f'"{title}"',
            "date": published,
            "categories": category,
            "tags": f"[{', '.join(tags)}]" if tags else "",
            "pin": "false",
            "image": "",
            "description": f'"{short_desc}"',
        }

        body = f"[Watch on YouTube]({channel_url}/watch?v={vid})"
        if desc:
            body += f"\n\n{desc}"

        write_post(filename, frontmatter, body)


def generate_livestream_post(vods):
    if not vods:
        return
    for v in vods:
        vid = v.get("video_id", "")
        title = v.get("title", "Untitled")
        published = v.get("published", "")
        desc = v.get("description", "")

        if not published or not vid:
            continue

        date = published[:10]
        filename = f"{date}-vod-{vid}.md"

        short_desc = (desc[:200] + "...") if desc and len(desc) > 200 else (desc or "Stream archive available.")

        frontmatter = {
            "title": f'"{title}"',
            "date": published,
            "categories": "streams",
            "tags": "[vod, stream]",
            "pin": "false",
            "image": "",
            "description": f'"{short_desc}"',
        }

        body = f"[Watch VOD on YouTube](https://watch.skiylia.dev/watch?v={vid})"
        if desc:
            body += f"\n\n{desc}"

        write_post(filename, frontmatter, body)


def clean_old_posts():
    kept = set()
    for root, dirs, files in os.walk(POSTS_DIR):
        for f in files:
            if f.endswith(".md"):
                kept.add(f)

    # We only clean after generating new ones; old generated posts will be
    # overwritten. But posts from video IDs that no longer exist (deleted/replaced)
    # should be removed.
    # Strategy: after generating, compare to known filenames and delete orphans.
    return kept


def main():
    # Clear all generated posts first
    for f in os.listdir(POSTS_DIR):
        if f.endswith(".md"):
            os.remove(os.path.join(POSTS_DIR, f))
    print(f"Cleared {POSTS_DIR}/")

    youtube = read_json("youtube_main.json")
    if youtube:
        videos = youtube.get("videos", [])
        print(f"Generating posts for {len(videos)} videos...")
        generate_video_posts(videos, "videos", "https://watch.skiylia.dev")

    vods = read_json("youtube_vods.json")
    if vods:
        vods_list = vods.get("videos", [])
        print(f"Generating posts for {len(vods_list)} VODs...")
        generate_livestream_post(vods_list)

    twitch_vods = read_json("twitch_vods.json")
    if twitch_vods:
        tvods = twitch_vods.get("videos", [])
        print(f"Generating posts for {len(tvods)} Twitch VODs...")
        for v in tvods:
            vid = v.get("video_id", "")
            title = v.get("title", "Untitled")
            published = v.get("published", "")
            desc = v.get("description", "")
            vod_url = v.get("url", f"https://www.twitch.tv/videos/{vid}")

            if not published or not vid:
                continue

            date = published[:10]
            filename = f"{date}-twitch-{vid}.md"

            short_desc = (desc[:200] + "...") if desc and len(desc) > 200 else (desc or "Stream archive available.")

            frontmatter = {
                "title": f'"{title}"',
                "date": published,
                "categories": "streams",
                "tags": "[twitch, vod]",
                "pin": "false",
                "image": "",
                "description": f'"{short_desc}"',
            }

            body = f"[Watch VOD on Twitch]({vod_url})"
            if desc:
                body += f"\n\n{desc}"

            write_post(filename, frontmatter, body)

    print("Done.")


if __name__ == "__main__":
    main()
