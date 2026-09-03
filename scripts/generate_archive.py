"""
Generate Jekyll archive pages: one page per series and per game.

Reads games.json, youtube_main.json, playlists.json, and game_links.yml from
_data/ and writes static markdown pages under archive/ (series/ and games/).

- Series pages live at archive/series/<slug>.md -> permalink /series/<slug>/
- Game pages live at archive/games/<slug>.md -> permalink /games/<slug>/

Missing games.json or youtube_main.json exits gracefully without writing
anything. The whole archive/ directory is cleared before generation.
"""

import html
import json
import os
import re
import shutil
from datetime import datetime

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "_data")
ARCHIVE_DIR = os.path.join(ROOT, "archive")
SERIES_DIR = os.path.join(ARCHIVE_DIR, "series")
GAMES_DIR = os.path.join(ARCHIVE_DIR, "games")
RSS_DIR = os.path.join(ARCHIVE_DIR, "rss", "series")


def slugify(name):
    """Match Liquid's default slugify so links line up with videos.md data-slug attrs."""
    return re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")


def esc(text):
    return html.escape(str(text), quote=True)


def read_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def read_yaml(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def write_page(path, frontmatter, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
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
        f.write(body + "\n")
    print(f"  {os.path.relpath(path, ROOT)}")


def fmt_duration(seconds):
    seconds = int(seconds or 0)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def fmt_hours(seconds):
    seconds = int(seconds or 0)
    h, rem = divmod(seconds, 3600)
    m = rem // 60
    if h and m:
        return f"{h}h {m}m"
    if h:
        return f"{h}h"
    return f"{m}m"


def fmt_date(published):
    day = (published or "").strip()[:10]
    if len(day) == 10:
        try:
            return datetime.strptime(day, "%Y-%m-%d").strftime("%d %b %Y")
        except ValueError:
            pass
    return day


def canonical_game(name, games_data, game_links):
    """Map a video's game field (e.g. 'KSP', 'StationFlow') to the games.json key."""
    if name in games_data:
        return name
    for gname, g in games_data.items():
        aliases = set(g.get("original_names") or [])
        aliases.update((game_links.get(gname) or {}).get("aliases") or [])
        if name in aliases:
            return gname
    return None


def episode_card(video):
    vid = video.get("video_id", "")
    title = video.get("title", "Untitled")
    thumb = video.get("thumbnail", "")
    views = int(video.get("view_count") or 0)
    dur = int(video.get("duration_seconds") or 0)
    date = fmt_date(video.get("published"))
    series = video.get("series") or {}
    game = series.get("game") or ""
    sname = series.get("series_name") or ""
    ep = series.get("episode_number")

    parts = [
        f'<div class="video-card" data-video-id="{esc(vid)}" data-title="{esc(title)}"'
        f' data-published="{esc(video.get("published") or "")}" data-views="{views}"'
        f' data-likes="{video.get("like_count") or 0}" data-comments="{video.get("comment_count") or 0}"'
        f' data-duration="{dur}" data-series="{esc(sname)}" data-game="{esc(game)}"'
        f' data-series-slug="{esc(slugify(sname))}" data-game-slug="{esc(slugify(game))}"'
        f' data-description="{esc(video.get("description") or "")}" onclick="openPlayer(this)">'
    ]
    parts.append('<div class="thumb-wrap">')
    if thumb:
        onerror = f"this.onerror=null;this.src='https://i.ytimg.com/vi/{vid}/hqdefault.jpg'"
        parts.append(f'<img src="{esc(thumb)}" alt="{esc(title)}" loading="lazy" onerror="{esc(onerror)}">')
    parts.append('<div class="play-overlay"><i class="fas fa-play"></i></div>')
    if dur:
        parts.append(f'<span class="duration-badge">{fmt_duration(dur)}</span>')
    parts.append("</div>")
    parts.append('<div class="card-body">')
    parts.append(f"<h3>{esc(title)}</h3>")
    meta = []
    if date:
        meta.append(f'<span class="meta-date">{esc(date)}</span>')
    if views:
        meta.append(f'<span class="views">{views} views</span>')
    if meta:
        parts.append(f'<div class="meta-row">{" ".join(meta)}</div>')
    if ep:
        parts.append(f'<div class="series-badge">Episode {esc(ep)}</div>')
    parts.append("</div></div>")
    return "\n".join(parts)


def playlist_links(sname, playlists):
    matched = [pl for pl in playlists if sname in (pl.get("title") or "")]
    lines = []
    for pl in matched:
        title = pl.get("title") or sname
        url = pl.get("url") or ""
        lines.append(
            f'<a href="{escape_url(url)}" target="_blank" rel="noopener">Watch the {esc(title)} playlist on YouTube</a>'
        )
    return lines


def _stats_row(items):
    """HTML for a header stats strip: list of (label, value) pairs."""
    cells = "".join(
        f'<div class="stat-cell"><span class="stat-value">{esc(str(val))}</span>'
        f'<span class="stat-label">{esc(str(label))}</span></div>'
        for label, val in items
    )
    return f'<div class="card-stats">{cells}</div>'


def _modal_include():
    return "{% include video-modal.html %}"


def game_art_url(gname, game_links):
    """Resolve a game's artwork, mirroring the /games tab logic:
    game_links.yml 'icon' wins, else Steam header jpg from the app id."""
    links = (game_links or {}).get(gname) or {}
    icon = links.get("icon")
    if icon:
        return icon
    steam = links.get("steam") or ""
    parts = steam.split("/")
    if len(parts) >= 6 and parts[4]:
        return f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{parts[4]}/header.jpg"
    return ""


def playlist_cover_for(sname, playlists):
    """Find a downloaded playlist cover for this series (assets/img/playlists/)."""
    for pl in playlists:
        if sname in pl.get("title", "") or (pl.get("title") or "") in sname:
            return pl.get("thumbnail") or pl.get("cover") or ""
    return ""


def write_series_page(sname, svideos, game_name, playlists, game_links):
    sslug = slugify(sname)
    frontmatter = {
        "layout": "page",
        "title": sname,
        "permalink": f"/series/{sslug}/",
        "group": "media",
        "series_feed": f"/feed/series/{sslug}.xml",
    }
    if game_name:
        frontmatter["game"] = game_name
    # Art comes from the matching playlist cover when we have one, else the game art
    cover = playlist_cover_for(sname, playlists)
    if cover:
        frontmatter["game_art"] = cover
    elif game_name:
        art = game_art_url(game_name, game_links)
        if art:
            frontmatter["game_art"] = art

    body = ["{% include game-art.html %}", ""]

    if game_name:
        gslug = slugify(game_name)
        body.append(
            f'<p class="series-overview">Part of the '
            f'<a href="/games/{gslug}/"><strong>{esc(game_name)}</strong></a> series.</p>'
        )
        body.append("")

    ep_count = len(svideos)
    total_secs = sum(int(v.get("duration_seconds") or 0) for v in svideos)
    total_views = sum(int(v.get("view_count") or 0) for v in svideos)
    body.append(_stats_row([("Episodes", ep_count), ("Watch time", fmt_hours(total_secs)), ("Views", total_views)]))
    body.append("")

    pl_links = playlist_links(sname, playlists)
    if pl_links:
        body.append('<div class="card-cta-block">')
        body.append("<strong>Playlist:</strong>")
        body.extend(f"<p>{p}</p>" for p in pl_links)
        body.append("</div>")
        body.append("")

    body.append('<h2 class="section-title">Episodes</h2>')
    body.append("")
    if svideos:
        body.append('<div class="video-grid">')
        for v in svideos:
            body.append(episode_card(v))
        body.append("</div>")
    else:
        body.append('<p class="empty-state">No episodes listed yet.</p>')

    body.append("")
    body.append(_modal_include())

    write_page(os.path.join(SERIES_DIR, f"{sslug}.md"), frontmatter, "\n".join(body))
    write_series_feed(sname, sslug, svideos)


def write_game_page(gname, g, games_data, playlists, game_links):
    gslug = slugify(gname)
    frontmatter = {
        "layout": "page",
        "title": gname,
        "permalink": f"/games/{gslug}/",
        "group": "media",
    }
    frontmatter["game"] = gname
    art = game_art_url(gname, game_links)
    if art:
        frontmatter["game_art"] = art

    body = ["{% include game-art.html %}", ""]

    links = game_links.get(gname) or {}
    link_html = []
    if links.get("steam"):
        link_html.append(
            f'<a href="{escape_url(links["steam"])}" class="btn game-link-btn" target="_blank" rel="noopener">'
            '<i class="fab fa-steam"></i> Steam</a>'
        )
    if links.get("website"):
        link_html.append(
            f'<a href="{escape_url(links["website"])}" class="btn game-link-btn" target="_blank" rel="noopener">'
            '<i class="fas fa-globe"></i> Website</a>'
        )
    if link_html:
        body.append(f'<div class="game-links">{"".join(link_html)}</div>')
        body.append("")

    ep_count = g.get("episode_count") or 0
    total_secs = g.get("total_duration_seconds") or 0
    total_views = g.get("total_views") or 0
    stream_count = g.get("stream_count") or 0
    source = g.get("source")
    stats = [("Episodes", ep_count), ("Watch time", fmt_hours(total_secs)), ("Views", total_views)]
    if stream_count:
        stats.append(("Streams", stream_count))
    if source:
        stats.append(("Source", source.title()))
    body.append(_stats_row(stats))
    body.append("")

    series_names = g.get("series") or []
    series_data = g.get("series_data") or {}
    if series_names:
        body.append('<h2 class="section-title">Series</h2>')
        body.append("")
        for sname in series_names:
            sslug = slugify(sname)
            years = (series_data.get(sname) or {}).get("active_years")
            label = sname
            if years:
                label += f" ({years})"
            body.append(f'- <a href="/series/{sslug}/">{esc(label)}</a>')
        body.append("")

    body.append('<p class="back-link"><a href="/games/" class="btn">&larr; All games</a></p>')

    write_page(os.path.join(GAMES_DIR, f"{gslug}.md"), frontmatter, "\n".join(body))


def escape_url(url):
    # Keep URLs valid while still escaping quotes that would break the attribute.
    return html.escape(str(url), quote=True)


def iso_date(published):
    day = (published or "").strip()[:10]
    if len(day) == 10:
        try:
            datetime.strptime(day, "%Y-%m-%d")
            return day + "T00:00:00Z"
        except ValueError:
            pass
    return None


def truncate(text, length=400):
    t = str(text or "")
    if len(t) <= length:
        return t
    return t[:length].rsplit(" ", 1)[0] + "..."


def write_series_feed(sname, sslug, svideos):
    feed_path = os.path.join(RSS_DIR, f"{sslug}.xml")
    os.makedirs(RSS_DIR, exist_ok=True)

    sorted_videos = sorted(svideos, key=lambda v: v.get("published") or "", reverse=True)

    entries = []
    for v in sorted_videos:
        vid = v.get("video_id", "")
        title = v.get("title", "Untitled")
        published = iso_date(v.get("published"))
        if not published:
            continue
        desc = v.get("description", "")
        thumb = v.get("thumbnail", "")
        summary = truncate(desc)

        entry = f"""  <entry>
    <title>{esc(title)}</title>
    <link href="https://skiylia.dev/videos#{esc(vid)}"/>
    <published>{published}</published>
    <id>https://skiylia.dev/videos#{esc(vid)}</id>
    <summary>{esc(summary)}</summary>"""
        if thumb:
            entry += f'\n    <media:thumbnail url="{esc(thumb)}"/>'
        entry += "\n  </entry>"
        entries.append(entry)

    feed_body = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:media="http://search.yahoo.com/mrss/">
  <title>{esc(sname)} - Skye</title>
  <link href="https://skiylia.dev/series/{esc(sslug)}/"/>
  <updated>{(sorted_videos[0].get("published") or "")[:10] + "T00:00:00Z" if sorted_videos else ""}</updated>
  <id>https://skiylia.dev/feed/series/{esc(sslug)}.xml</id>
{chr(10).join(entries)}
</feed>
"""

    frontmatter = {
        "layout": None,
        "permalink": f"/feed/series/{sslug}.xml",
    }
    write_page(feed_path, frontmatter, feed_body)


def main():
    games = read_json("games.json")
    if games is None:
        print("games.json missing in _data/; skipping archive generation")
        return
    youtube = read_json("youtube_main.json")
    if youtube is None:
        print("youtube_main.json missing in _data/; skipping archive generation")
        return

    videos = youtube.get("videos") or []
    playlists = (read_json("playlists.json") or {}).get("playlists") or []
    game_links = read_yaml("game_links.yml")

    games_data = games.get("games") or {}
    non_game = games.get("non_game") or {}

    series_parents = {}
    for gname, g in games_data.items():
        info = g.get("series_data") or {}
        names = list(g.get("series") or []) + list(info.keys())
        for sname in names:
            series_parents.setdefault(sname, gname)
    for cat in (non_game.get("categories") or {}).values():
        for sname in cat.get("series_data") or {}:
            series_parents.setdefault(sname, None)

    for v in videos:
        s = v.get("series") or {}
        sname = s.get("series_name")
        if not sname:
            continue
        if sname not in series_parents:
            series_parents[sname] = canonical_game(s.get("game"), games_data, game_links)
        else:
            series_parents.setdefault(sname, None)

    for pl in playlists:
        title = (pl.get("title") or "").strip()
        if not title:
            continue
        sname = title.split(" | ")[0].strip() if " | " in title else title
        series_parents.setdefault(sname, None)

    if os.path.isdir(ARCHIVE_DIR):
        shutil.rmtree(ARCHIVE_DIR)
    os.makedirs(SERIES_DIR, exist_ok=True)
    os.makedirs(GAMES_DIR, exist_ok=True)
    print(f"Cleared {os.path.relpath(ARCHIVE_DIR, ROOT)}/")

    series_videos = {sname: [] for sname in series_parents}
    for v in videos:
        sname = (v.get("series") or {}).get("series_name")
        if sname in series_videos:
            series_videos[sname].append(v)
    for lst in series_videos.values():
        lst.sort(key=lambda v: v.get("published") or "")

    print("Generating series pages...")
    for sname in sorted(series_parents, key=lambda n: (series_parents[n] or "", n)):
        write_series_page(sname, series_videos[sname], series_parents[sname], playlists, game_links)

    print("Generating game pages...")
    for gname in sorted(games_data):
        write_game_page(gname, games_data[gname], games_data, playlists, game_links)

    print(f"Done: {len(series_parents)} series, {len(games_data)} games.")


if __name__ == "__main__":
    main()
