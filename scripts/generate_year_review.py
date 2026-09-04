"""
Generate "Year in Review" landing page from history + video data.

Writes archive/year.md -> permalink /year/ with all years combined,
an inline TOC at the top, and per-year sections with stats, highlights,
series info, and video thumbnails.
"""

import json
import os
from collections import defaultdict

import yaml

DATA_DIR = "_data"
OUTPUT_DIR = "archive"


def read_json(name):
    p = os.path.join(DATA_DIR, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def slugify(name):
    return os.path.normcase("".join(c.lower() if c.isalnum() else "-" for c in name)).strip("-")


def fmt(n):
    return f"{n:,}"


def write_page(path, frontmatter, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("---\n")
        yaml.safe_dump(frontmatter, f, sort_keys=False, allow_unicode=True, width=1000)
        f.write("---\n\n")
        f.write(body)
    print(f"  {path}")


def parse_active_years(active_years_str):
    """Parse a string like '2024-2025' or '2025' into a set of years."""
    if not active_years_str:
        return set()
    parts = active_years_str.split("-")
    if len(parts) == 1:
        return {int(parts[0])}
    if len(parts) == 2:
        start = int(parts[0])
        end = int(parts[1])
        return set(range(start, end + 1))
    return set()


def build_series_registry(videos):
    """Build a dict of series_name -> {games, active_years, start_year, end_year} from video data."""
    series = {}  # name -> {"games": set, "years": set}
    for v in videos:
        s = v.get("series")
        if not s or not isinstance(s, dict):
            continue
        sn = s.get("series_name", "")
        if not sn:
            continue
        g = s.get("game", "Other")
        pub = v.get("published", "")
        year = int(pub[:4]) if len(pub) >= 4 else None
        if sn not in series:
            series[sn] = {"games": set(), "years": set()}
        series[sn]["games"].add(g)
        if year:
            series[sn]["years"].add(year)
    return series


def build_year(year, videos, history, milestones):
    year_entries = [e for e in history if (e.get("date") or "").startswith(year)]
    if not year_entries:
        return None

    first, last = year_entries[0], year_entries[-1]

    def pick(e, pf, f):
        d = e.get(pf) or {}
        return d.get(f, 0) or 0

    subs_start = pick(first, "youtube_main", "subs")
    subs_end = pick(last, "youtube_main", "subs")
    views_start = pick(first, "youtube_main", "views")
    views_end = pick(last, "youtube_main", "views")
    videos_start = pick(first, "youtube_main", "videos")
    videos_end = pick(last, "youtube_main", "videos")

    watch_min = sum(e.get("_analytics", {}).get("watch_time_minutes", 0) for e in year_entries)
    watch_h = watch_min // 60

    year_videos = [v for v in videos if (v.get("published") or "").startswith(year)]
    total_views_year = sum(v.get("view_count", 0) for v in year_videos)
    most_viewed = max(year_videos, key=lambda v: v.get("view_count", 0)) if year_videos else None

    months = defaultdict(int)
    for v in year_videos:
        months[(v.get("published") or "")[:7]] += 1
    busiest = max(months, key=months.get) if months else None
    busiest_count = months.get(busiest, 0) if busiest else 0

    game_min = defaultdict(float)
    for v in year_videos:
        s = v.get("series") or {}
        g = s.get("game") or "Other"
        game_min[g] += v.get("duration_seconds", 0) / 60
    top_game = max(game_min, key=game_min.get) if game_min else None

    def eng(v):
        vc = v.get("view_count", 0)
        return (v.get("like_count", 0) + v.get("comment_count", 0)) / vc * 100 if vc else 0

    eng_leader = max(year_videos, key=eng) if year_videos else None

    ms_count = sum(1 for d in milestones.values() if str(d).startswith(year))

    # Per-game breakdown
    game_breakdown = defaultdict(lambda: {"episodes": 0, "watch_seconds": 0})
    for v in year_videos:
        s = v.get("series") or {}
        g = s.get("game") or "Other"
        game_breakdown[g]["episodes"] += 1
        game_breakdown[g]["watch_seconds"] += v.get("duration_seconds", 0)

    return {
        "year": int(year),
        "subs_start": subs_start,
        "subs_end": subs_end,
        "views_start": views_start,
        "views_end": views_end,
        "videos_start": videos_start,
        "videos_end": videos_end,
        "watch_h": watch_h,
        "uploads": len(year_videos),
        "total_views_year": total_views_year,
        "most_viewed": most_viewed,
        "busiest": busiest,
        "busiest_count": busiest_count,
        "top_game": top_game,
        "top_game_h": int(game_min.get(top_game, 0) // 60) if top_game else 0,
        "eng_leader": eng_leader,
        "ms_count": ms_count,
        "game_breakdown": dict(game_breakdown),
        "year_videos": year_videos,
    }


def render_year(r, series_registry, is_first=False):
    y = r["year"]
    lines = []

    # Distinct separator between years (skipped for the first one)
    if not is_first:
        lines.append('<hr class="year-divider">')
        lines.append("")

    # Section heading with anchor
    lines.append(f'<h2 id="year-{y}">{y}</h2>')
    lines.append("")

    # Stat cards
    subs_delta = r["subs_end"] - r["subs_start"]
    views_delta = r["views_end"] - r["views_start"]
    vids_delta = r["videos_end"] - r["videos_start"]

    def sc(val):
        prefix = "+" if val >= 0 else ""
        return prefix + f"{val:,}" if isinstance(val, int) else str(val)

    lines.append('<div class="card-stats">')
    _c = '<div class="stat-cell">'
    _v = '<span class="stat-value">'
    _l = '</span><span class="stat-label">'
    _e = "</span></div>"
    lines.append(_c + _v + sc(subs_delta) + _l + "Subs" + _e)
    lines.append(_c + _v + sc(views_delta) + _l + "Views" + _e)
    lines.append(_c + _v + "+" + str(vids_delta) + _l + "Videos" + _e)
    lines.append(_c + _v + str(r["uploads"]) + _l + "Uploads" + _e)
    lines.append(_c + _v + f"{r['watch_h']:,}h" + _l + "Watch time" + _e)
    lines.append("</div>")
    lines.append("")

    # Highlights
    lines.append('<h3 class="section-title">Highlights</h3>')
    if r["busiest"]:
        bc = r["busiest"]
        bcount = r["busiest_count"]
        lines.append(f'<div class="insight-box">Busiest month: <strong>{bc}</strong> ({bcount} uploads)</div>')

    if r["most_viewed"]:
        mv = r["most_viewed"]
        vid = mv.get("video_id", "")
        vt = mv.get("title", "")
        vc = mv.get("view_count", 0)
        lines.append(f'<p>Most watched: <a href="/videos#{vid}"><strong>{vt}</strong></a> ({vc:,} views)</p>')

    if r["top_game"]:
        lines.append(f"<p>Top game by watch time: <strong>{r['top_game']}</strong> ({r['top_game_h']}h)</p>")

    if r["eng_leader"]:
        el = r["eng_leader"]
        evid = el.get("video_id", "")
        etitle = el.get("title", "")
        lines.append(f'<p>Engagement leader: <a href="/videos#{evid}"><strong>{etitle}</strong></a></p>')

    if r["ms_count"]:
        lines.append(f"<p>Milestones crossed: <strong>{r['ms_count']}</strong></p>")

    # Per-game breakdown, merged alongside the highlights
    gb = r["game_breakdown"]
    if gb:
        lines.append('<p class="game-breakdown-label">Games played this year:</p>')
        lines.append('<div class="game-breakdown">')
        for gname in sorted(gb.keys()):
            gdata = gb[gname]
            gcount = gdata["episodes"]
            ghours = int(gdata.get("duration_seconds", 0) // 3600) if gdata.get("duration_seconds") else 0
            lines.append(
                f'<span class="game-breakdown-pill">'
                f"<strong>{gcount}</strong> &times; {gname}" + (f" &middot; {ghours}h" if ghours else "") + "</span>"
            )
        lines.append("</div>")
        lines.append("")

    # Top video thumbnails (first 4 by view count)
    top_vids = sorted(r["year_videos"], key=lambda v: v.get("view_count", 0), reverse=True)[:4]
    if top_vids:
        lines.append('<h3 class="section-title">Top Videos</h3>')
        lines.append('<div class="thumbnail-gallery">')
        for v in top_vids:
            vid = v.get("video_id", "")
            vt = v.get("title", "").replace('"', "&quot;")
            thumb = v.get("thumbnail", "")
            vc = v.get("view_count", 0)
            # Use a background-image div instead of <img> so Chirpy's
            # refactor-content doesn't wrap it in a nested lightbox anchor.
            lines.append(f'<a href="/videos#{vid}" class="video-thumb" title="{vt}">')
            lines.append(f'  <span class="video-thumb-img" style="background-image:url(\'{thumb}\')"></span>')
            lines.append(f'  <span class="thumb-views">{vc:,} views</span>')
            lines.append(f'  <span class="thumb-title">{vt}</span>')
            lines.append("</a>")
        lines.append("</div>")
        lines.append("")

    # Series active in this year
    active_in_year = []
    new_series = []
    ended_series = []
    for sname, sinfo in series_registry.items():
        if r["year"] in sinfo["years"]:
            active_in_year.append(sname)
        # Determine if this series started or ended this year
        syears = sorted(sinfo["years"])
        if syears and syears[0] == r["year"]:
            new_series.append(sname)
        if syears and syears[-1] == r["year"] and (len(syears) == 1 or r["year"] != max(syears)):
            ended_series.append(sname)

    if active_in_year:
        lines.append('<h3 class="section-title">Active Series</h3>')
        lines.append("<ul>")
        for s in sorted(active_in_year):
            games = series_registry[s]["games"]
            games_str = ", ".join(sorted(games))
            lines.append(f"  <li><strong>{s}</strong> ({games_str})</li>")
        lines.append("</ul>")

    if new_series:
        lines.append(f"<p><strong>New this year:</strong> {', '.join(sorted(new_series))}</p>")
    if ended_series:
        lines.append(f"<p><strong>Concluded this year:</strong> {', '.join(sorted(ended_series))}</p>")

    return "\n".join(lines)


def main():
    videos = (read_json("youtube_main.json") or {}).get("videos") or []
    history = read_json("history.json") or []
    milestones = (read_json("milestones.json") or {}).get("reached") or {}

    if not videos and not history:
        print("No data; skipping year page")
        return

    # Derive years from history, falling back to video publish years
    years = set()
    if history:
        years.update((e.get("date") or "")[:4] for e in history if e.get("date"))
    if videos:
        years.update((v.get("published") or "")[:4] for v in videos if v.get("published"))
    years = sorted(y for y in years if y)

    if not years:
        print("No years found; skipping")
        return

    series_registry = build_series_registry(videos)

    body_parts = []
    toc_entries = []

    for year in years:
        r = build_year(year, videos, history, milestones)
        if not r:
            continue
        toc_entries.append(f'- <a href="#year-{year}">{year}</a>')
        body_parts.append(render_year(r, series_registry, is_first=not body_parts))

    if not body_parts:
        print("No data rendered; skipping")
        return

    front = {
        "layout": "page",
        "title": "Year in Review",
        "permalink": "/year/",
        "group": "stats",
    }

    toc = "# Year in Review\n\nJump to year:\n\n" + "\n".join(toc_entries) + "\n\n---\n"
    body = toc + "\n\n".join(body_parts)
    write_page(os.path.join(OUTPUT_DIR, "year.md"), front, body)

    # Remove old individual year files if they exist
    old_dir = os.path.join(OUTPUT_DIR, "year")
    if os.path.isdir(old_dir):
        for fname in os.listdir(old_dir):
            fpath = os.path.join(old_dir, fname)
            if fname.endswith(".md") and fname != "index.md":
                os.remove(fpath)
                print(f"  Removed old: {fpath}")

    print(f"Year page written for: {', '.join(years)}")


if __name__ == "__main__":
    main()
