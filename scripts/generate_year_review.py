"""
Generate "Year in Review" landing pages from history + video data.

For each calendar year present in the history data, writes
archive/year/<year>.md -> permalink /year/<year>/ with:
- overall growth (subs/views/videos) that year
- most-watched video, top game by watch time, engagement leader
- busiest upload month, total watch time, milestone count
- a link to the History page for the full picture

Also writes archive/year/index.md -> /year/ listing all years.
"""

import json
import os
from collections import defaultdict

import yaml

DATA_DIR = "_data"
YEAR_DIR = os.path.join("archive", "year")


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


def build_year(year):
    history = read_json("history.json") or []
    yt = read_json("youtube_main.json") or {}
    videos = yt.get("videos") or []
    milestones = (read_json("milestones.json") or {}).get("reached") or {}

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

    # watch time from _analytics deltas within the year
    watch_min = sum(e.get("_analytics", {}).get("watch_time_minutes", 0) for e in year_entries)
    watch_h = watch_min // 60

    # per-video: that year's uploads
    year_videos = [v for v in videos if (v.get("published") or "").startswith(year)]
    total_views_year = sum(v.get("view_count", 0) for v in year_videos)
    most_viewed = max(year_videos, key=lambda v: v.get("view_count", 0)) if year_videos else None

    # busiest upload month
    months = defaultdict(int)
    for v in year_videos:
        months[(v.get("published") or "")[:7]] += 1
    busiest = max(months, key=months.get) if months else None
    busiest_count = months.get(busiest, 0) if busiest else 0

    # top game by watch time
    game_min = defaultdict(float)
    for v in year_videos:
        s = v.get("series") or {}
        g = s.get("game") or "Other"
        game_min[g] += v.get("duration_seconds", 0) / 60
    top_game = max(game_min, key=game_min.get) if game_min else None

    # engagement leader
    def eng(v):
        vc = v.get("view_count", 0)
        return (v.get("like_count", 0) + v.get("comment_count", 0)) / vc * 100 if vc else 0

    eng_leader = max(year_videos, key=eng) if year_videos else None

    ms_count = sum(1 for d in milestones.values() if str(d).startswith(year))

    return {
        "year": year,
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
    }


def render(r):
    y = r["year"]
    lines = []
    lines.append("{% include banner.html %}")
    lines.append("")
    subs_delta = r["subs_end"] - r["subs_start"]
    views_delta = r["views_end"] - r["views_start"]
    vids_delta = r["videos_end"] - r["videos_start"]

    def sc(val):
        prefix = "+" if val >= 0 else ""
        return prefix + f"{val:,}" if isinstance(val, int) else str(val)

    lines.append("<h1 class='dynamic-title'>" + y + " in Review</h1>")
    _c = '<div class="stat-cell">'
    _ec = "</div>"
    lines.append('<div class="card-stats">')
    lines.append(
        _c + f'<span class="stat-value">{sc(subs_delta)}</span>' + '<span class="stat-label">Subs</span>' + _ec
    )
    lines.append(
        _c + f'<span class="stat-value">{sc(views_delta)}</span>' + '<span class="stat-label">Views</span>' + _ec
    )
    lines.append(_c + f'<span class="stat-value">+{vids_delta}</span>' + '<span class="stat-label">Videos</span>' + _ec)
    lines.append(
        _c + f'<span class="stat-value">{r["uploads"]}</span>' + '<span class="stat-label">Uploads</span>' + _ec
    )
    lines.append(
        _c + f'<span class="stat-value">{r["watch_h"]:,}h</span>' + '<span class="stat-label">Watch time</span>' + _ec
    )
    lines.append("</div>")

    lines.append("<h2 class='section-title'>Highlights</h2>")
    if r["busiest"]:
        bc = r["busiest"]
        bcount = r["busiest_count"]
        lines.append(f'<div class="insight-box">Busiest month: <strong>{bc}</strong> ({bcount} uploads)</div>')
        lines.append("")
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
    lines.append("")
    lines.append('<p class="back-link"><a href="/year/" class="btn">&larr; All years</a></p>')
    return "\n".join(lines)


def main():
    history = read_json("history.json") or []
    if not history:
        print("No history data; skipping year pages")
        return
    years = sorted({(e.get("date") or "")[:4] for e in history if e.get("date")})

    index_rows = []
    for year in years:
        r = build_year(year)
        if not r:
            continue
        safe = slugify(r["year"])
        front = {
            "layout": "page",
            "title": f"{r['year']} in Review",
            "permalink": f"/year/{safe}/",
            "group": "stats",
        }
        write_page(os.path.join(YEAR_DIR, f"{safe}.md"), front, render(r))
        index_rows.append(f"- [{r['year']}](/year/{safe}/)")

    if index_rows:
        front = {
            "layout": "page",
            "title": "Year in Review",
            "permalink": "/year/",
            "group": "stats",
        }
        body = "# Year in Review\n\n" + "\n".join(sorted(index_rows)) + "\n"
        write_page(os.path.join(YEAR_DIR, "index.md"), front, body)

    print(f"Year pages written for: {', '.join(years)}")


if __name__ == "__main__":
    main()
