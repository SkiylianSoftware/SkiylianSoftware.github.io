"""
Generate Jekyll _posts from YouTube video and VOD data for the RSS feed.

Each video/VOD gets a short post with title, date, description, and a link.
This populates feed.xml so subscribers can see new content in their feed reader.

Front matter is emitted with PyYAML's safe_dump rather than hand-rolled
"key: value" lines. Hand-rolled output silently corrupts the whole front
matter whenever a title or description contains a character YAML treats
specially (notably straight double quotes), which drops the post title,
date, and categories from the feed. safe_dump escapes everything for us and
keeps the output re-parseable.
"""

import json
import os

import yaml

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
        yaml.safe_dump(
            frontmatter,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=1000,
        )
        f.write("---\n\n")
        f.write(body)
    print(f"  {path}")


def _series_tags(video):
    tags = []
    series = video.get("series") or {}
    if series.get("game"):
        tags.append(series["game"])
    if series.get("series_name"):
        tags.append(series["series_name"])
    return tags


def _iso_duration(seconds):
    """ISO-8601 duration for schema.org, e.g. 3661 -> PT1H1M1S."""
    if not seconds:
        return None
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    total = "PT"
    if h:
        total += f"{h}H"
    if m:
        total += f"{m}M"
    total += f"{s}S"
    return total


def _video_json_ld(video, embed_url, content_url):
    """VideoObject schema.org JSON-LD for rich results on video posts."""
    desc = (video.get("description") or "").strip()
    data = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": video.get("title", "Untitled"),
        "description": desc[:3000],
        "thumbnailUrl": video.get("thumbnail", ""),
        "uploadDate": (video.get("published") or "")[:19],
        "contentUrl": content_url,
        "embedUrl": embed_url,
        "isFamilyFriendly": True,
    }
    duration = _iso_duration(video.get("duration_seconds"))
    if duration:
        data["duration"] = duration
    views = video.get("view_count")
    if views:
        data["interactionStatistic"] = [
            {
                "@type": "InteractionCounter",
                "interactionType": {"@type": "WatchAction"},
                "userInteractionCount": int(views),
            }
        ]
    return json.dumps(data, ensure_ascii=False)


def _json_ld_block(video, embed_url, content_url):
    return f'<script type="application/ld+json">\n{_video_json_ld(video, embed_url, content_url)}\n</script>'


def generate_video_posts(videos, label, channel_url):
    if not videos:
        return
    for v in videos:
        vid = v.get("video_id", "")
        title = v.get("title", "Untitled")
        published = v.get("published", "")
        desc = v.get("description", "")

        if not published or not vid:
            continue

        date = published[:10]
        filename = f"{date}-{vid}.md"

        frontmatter = {
            "title": title,
            "date": published,
            "categories": [label.lower()],
            "slug": vid,
            "pin": False,
        }
        tags = _series_tags(v)
        if tags:
            frontmatter["tags"] = tags
        # Branded OG card takes precedence; it is generated into
        # /assets/img/og/<vid>.jpg before this script runs in CI.
        og_card = f"/assets/img/og/{vid}.jpg"
        if os.path.exists(og_card[1:]):
            frontmatter["image"] = og_card
        elif v.get("thumbnail"):
            frontmatter["image"] = v["thumbnail"]
        if v.get("duration_seconds"):
            frontmatter["duration_seconds"] = v["duration_seconds"]
        if desc:
            frontmatter["description"] = desc

        content_url = f"https://www.youtube.com/watch?v={vid}"
        embed_url = f"https://www.youtube.com/embed/{vid}"
        body = _json_ld_block(v, embed_url, content_url)
        body += "\n\n"
        body += f"**[Watch on YouTube]({channel_url}/watch?v={vid})**"
        if desc:
            body += "\n\n"
            body += f"{desc[:300]}\u2026" if len(desc) > 300 else desc

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

        frontmatter = {
            "title": title,
            "date": published,
            "categories": ["streams"],
            "slug": f"vod-{vid}",
            "tags": ["vod", "stream"],
            "pin": False,
        }
        if v.get("thumbnail"):
            frontmatter["image"] = v["thumbnail"]
        if v.get("duration_seconds"):
            frontmatter["duration_seconds"] = v["duration_seconds"]
        if desc:
            frontmatter["description"] = desc

        content_url = f"https://www.youtube.com/watch?v={vid}"
        embed_url = f"https://www.youtube.com/embed/{vid}"
        body = _json_ld_block(v, embed_url, content_url)
        body += "\n\n"
        body += f"**[Watch VOD on YouTube](https://watch.skiylia.dev/watch?v={vid})**"
        if desc:
            body += "\n\n"
            body += f"{desc[:300]}\u2026" if len(desc) > 300 else desc

        write_post(filename, frontmatter, body)


def generate_twitch_post(vods):
    if not vods:
        return
    for v in vods:
        vid = v.get("video_id", "")
        title = v.get("title", "Untitled")
        published = v.get("published", "")
        desc = v.get("description", "")
        vod_url = v.get("url", f"https://www.twitch.tv/videos/{vid}")

        if not published or not vid:
            continue

        date = published[:10]
        filename = f"{date}-twitch-{vid}.md"

        frontmatter = {
            "title": title,
            "date": published,
            "categories": ["streams"],
            "slug": f"twitch-{vid}",
            "tags": ["twitch", "vod"],
            "pin": False,
        }
        if v.get("thumbnail"):
            frontmatter["image"] = v["thumbnail"]
        if v.get("duration_seconds"):
            frontmatter["duration_seconds"] = v["duration_seconds"]
        if desc:
            frontmatter["description"] = desc

        body = _json_ld_block(v, vod_url, vod_url)
        body += "\n\n"
        body += f"**[Watch VOD on Twitch]({vod_url})**"
        if desc:
            body += "\n\n"
            body += f"{desc[:300]}\u2026" if len(desc) > 300 else desc

        write_post(filename, frontmatter, body)


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
        generate_twitch_post(tvods)

    print("Done.")


if __name__ == "__main__":
    main()
