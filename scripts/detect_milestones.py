import contextlib
import json
import os
import re
from datetime import date as dt_date
from datetime import datetime, timedelta, timezone

import yaml
from common import (
    AGE_DAYS_THRESH,
    ALIAS_MAP,
    ALL_THRESH,
    ANNIVERSARY_THRESH,
    DATA_DIR,
    GAME_EP_THRESH,
    HIATUS_DAYS_THRESH,
    HOURS_THRESH,
    MILESTONE_SPECS,
    P2,
    P3,
    RND,
    SEQUEL_BASE,
    VALID_GAMES,
    VIDEO_FIRST_THRESH,
    read_json,
)
from dateutil.relativedelta import relativedelta

MILESTONES_FILE = os.path.join(DATA_DIR, "milestones.json")


def first_date_from_history(history, label, threshold):
    """Return the first date in history where label >= threshold."""
    for entry in history:
        ym = entry.get("youtube_main", {}) or {}
        if ym.get(label, 0) >= threshold:
            return entry["date"]
    return None


def main():
    history = read_json("history.json") or []
    site_meta = read_json("site_meta.json") or {}
    yt_main = read_json("youtube_main.json") or {}

    debug = os.environ.get("DEBUG") == "1"
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    # Current values
    subs = site_meta.get("subscriber_count", 0)
    views = site_meta.get("view_count", 0)
    videos_count = site_meta.get("video_count", 0)

    # Total likes/comments across all videos (per platform and combined)
    yt_vods_data = read_json("youtube_vods.json") or {}
    total_likes = sum(v.get("like_count", 0) for v in yt_main.get("videos", []))
    total_comments = sum(v.get("comment_count", 0) for v in yt_main.get("videos", []))
    vods_likes = sum(v.get("like_count", 0) for v in yt_vods_data.get("videos", []))
    vods_comments = sum(v.get("comment_count", 0) for v in yt_vods_data.get("videos", []))
    combined_likes = total_likes + vods_likes
    combined_comments = total_comments + vods_comments

    # Load previous milestones for comparison
    prev = read_json("milestones.json") or {}
    prev_reached = prev.get("reached", {})
    new_reached = {}
    _vf_before = [k for k in prev_reached if k.startswith("video_first_")]
    if _vf_before:
        print(f"  DEBUG video_first in prev_reached on load ({len(_vf_before)}):")
        for _k in sorted(_vf_before):
            print(f"    {_k!r}: {prev_reached[_k]}")
    if prev_reached:
        _zk = [k for k in prev_reached if k.endswith("_0") or k.endswith("_")]
        if _zk:
            print(f"  Stripping {len(_zk)} stale milestone keys from prev_reached")
            for _k in _zk:
                print(f"    {_k!r}: {prev_reached[_k]}")
                del prev_reached[_k]

    _vf_after_strip = [k for k in prev_reached if k.startswith("video_first_")]
    if _vf_after_strip:
        print(f"  DEBUG video_first left in prev_reached after strip ({len(_vf_after_strip)}):")
        for _k in sorted(_vf_after_strip):
            print(f"    {_k!r}: {prev_reached[_k]}")

    if debug:
        print(
            "  Current:"
            f" {subs} subs, {views} views, {videos_count} videos,"
            f" {total_likes} likes, {total_comments} comments"
        )
        print(
            f"  History: {len(history)} entries ({history[0]['date']} to {history[-1]['date']})"
            if history
            else "  History: empty"
        )

    # Process standard milestones (subs, views, videos)
    # Collect ALL thresholds (no break), then collapse same-label same-date later
    custom_msgs = {}
    values = {"subs": subs, "views": views, "videos": videos_count}
    for label, thresholds, *_ in MILESTONE_SPECS:
        if label in ("likes", "comments"):
            continue
        value = values.get(label, 0)
        for m in sorted(thresholds, reverse=True):
            if value >= m:
                key = f"{label}_{m}"
                date = first_date_from_history(history, label, m)
                if not date and label == "videos":
                    dates = sorted(
                        [v.get("published", "")[:10] for v in yt_main.get("videos", []) if v.get("published")]
                    )
                    if len(dates) >= m:
                        date = dates[m - 1]
                if not date:
                    date = today
                new_reached[key] = date

    # Process game milestones from per-video cumulative data
    all_videos = yt_main.get("videos", [])
    game_cumulative = {}
    series_cumulative = {}
    game_first_series = {}
    game_video_list = {}
    for v in all_videos:
        s = v.get("series", {})
        gname_raw = (s or {}).get("game", "")
        pub = v.get("published", "")[:10]
        if gname_raw and pub:
            game_cumulative.setdefault(gname_raw, []).append(pub)
            sname = (s or {}).get("series_name", "")
            if sname:
                series_cumulative.setdefault(sname, []).append(pub)
    # Build game_first_series and game_video_list from sorted videos
    for v in sorted(all_videos, key=lambda x: x.get("published", "")):
        s = v.get("series", {})
        if not s:
            continue
        gname_raw = (s or {}).get("game", "")
        sname = (s or {}).get("series_name", "")
        pub = v.get("published", "")[:10]
        vid = v.get("video_id", "")
        thumb = v.get("thumbnail", "")
        title = v.get("title", "")
        if gname_raw and sname and gname_raw not in game_first_series:
            game_first_series[gname_raw] = sname
        if gname_raw and pub and vid:
            game_video_list.setdefault(gname_raw, []).append((pub, vid, thumb, title))

    # Per-platform and combined likes/comments milestones
    # Use video publish dates to find when cumulative totals crossed each threshold
    def _track_like_comment(source, prefix, videos, field):
        """Generate likes or comments milestones for a specific source."""
        total = sum(v.get(field, 0) for v in videos)
        for thresholds in (P3, P2, RND):
            for m in sorted(thresholds, reverse=True):
                if total >= m:
                    key = f"{prefix}_{m}"
                    cum = 0
                    date = today
                    for v in sorted(videos, key=lambda x: x.get("published", "")):
                        cum += v.get(field, 0)
                        if cum >= m:
                            date = v.get("published", "")[:10]
                            break
                    new_reached[key] = date

    for label, field in (("likes", "like_count"), ("comments", "comment_count")):
        _track_like_comment(label, f"youtube_{label}", all_videos, field)
        _track_like_comment(label, f"vods_{label}", yt_vods_data.get("videos", []), field)
        combined_field = combined_likes if label == "likes" else combined_comments
        combined_total = combined_field
        for thresholds in (P3, P2, RND):
            for m in sorted(thresholds, reverse=True):
                if combined_total >= m:
                    key = f"combined_{label}_{m}"
                    # Find first video across both sources that pushed us past threshold
                    all_sorted = sorted(
                        all_videos + yt_vods_data.get("videos", []), key=lambda x: x.get("published", "")
                    )
                    cum = 0
                    date = today
                    for v in all_sorted:
                        cum += v.get(field, 0)
                        if cum >= m:
                            date = v.get("published", "")[:10]
                            break
                    new_reached[key] = date

    def _steam_icon_url(steam_url):
        """Construct Steam store header image URL from store page URL."""
        m = re.search(r"/app/(\d+)", steam_url)
        if m:
            return f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{m.group(1)}/header.jpg"
        return ""

    # Load game icons from game_links.yml
    game_icons = {}
    gl_path = os.path.join(DATA_DIR, "game_links.yml")
    if os.path.exists(gl_path):
        try:
            with open(gl_path) as f:
                _gl = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"  Warning: could not load {gl_path}: {e}")
            _gl = {}
        for name, entry in _gl.items():
            if isinstance(entry, dict):
                icon = entry.get("icon", "")
                if not icon and entry.get("steam"):
                    icon = _steam_icon_url(entry["steam"])
                if icon:
                    game_icons[name] = icon
        if debug:
            _with_icons = [k for k, v in game_icons.items() if v]
            _missing = [k for k in _gl if k not in game_icons]
            print(f"  DEBUG game_icons: {len(_with_icons)} loaded, {len(_missing)} missing")
            if _missing:
                print(f"    Missing icons for: {', '.join(_missing)}")

    def _matches_playlist(gname, pl_title):
        """Match game name to playlist title using word-level matching with space-normalized fallback."""
        gl = gname.lower().strip()
        pt = pl_title.lower().strip()
        if gl == pt:
            return True
        gl_words = set(gl.split())
        pt_words = set(pt.split())
        if gl_words and pt_words and (gl_words <= pt_words or pt_words <= gl_words):
            return True
        gl_ns = gl.replace(" ", "").replace("-", "").replace("_", "").replace(":", "")
        pt_ns = pt.replace(" ", "").replace("-", "").replace("_", "").replace(":", "")
        return gl_ns == pt_ns or pt_ns.startswith(gl_ns) or gl_ns.startswith(pt_ns) or gl_ns in pt_ns

    def _build_playlist_index(playlist_data, game_cumulative, game_first_series):
        """Build game_to_playlist and series_to_playlist mappings with normalized matching."""
        game_to_playlist = {}
        series_to_playlist = {}
        for pl in playlist_data.get("playlists", []):
            pt = pl.get("title", "")
            for gname in game_cumulative:
                if _matches_playlist(gname, pt):
                    game_to_playlist[gname] = pl
                    break
            for gname, sname in game_first_series.items():
                if sname and (_matches_playlist(sname, pt) or _matches_playlist(gname, pt)):
                    if gname not in game_to_playlist:
                        series_to_playlist[gname] = pl
                    break
        return game_to_playlist, series_to_playlist

    # Filter out content series that aren't actual games (Railway Exhibition Vlogs, etc.)
    playlist_data = read_json("playlists.json") or {}
    if VALID_GAMES:
        game_cumulative = {g: d for g, d in game_cumulative.items() if g in VALID_GAMES}
    elif playlist_data.get("playlists"):
        game_cumulative = {
            g: d
            for g, d in game_cumulative.items()
            if any(_matches_playlist(g, pl.get("title", "")) for pl in playlist_data["playlists"])
        }

    def resolve_gname(raw):
        return ALIAS_MAP.get(raw, raw)

    # Cascade sequel game names to base games for shared milestone tracking
    for v in yt_main.get("videos", []):
        s = v.get("series")
        if s:
            gname = resolve_gname(s.get("game", ""))
            if gname in SEQUEL_BASE:
                s["game"] = SEQUEL_BASE[gname]

    # Resolve game_cumulative aliases so milestone keys use canonical names
    game_cumulative_resolved = {}
    for raw_gname, dates in game_cumulative.items():
        canon = resolve_gname(raw_gname)
        game_cumulative_resolved.setdefault(canon, []).extend(dates)
    game_cumulative = game_cumulative_resolved

    # Resolve game_first_series and game_video_list aliases
    game_first_series_resolved = {}
    for raw_gname, sname in game_first_series.items():
        canon = resolve_gname(raw_gname)
        if canon not in game_first_series_resolved:
            game_first_series_resolved[canon] = sname
    game_first_series = game_first_series_resolved

    game_video_list_resolved = {}
    for raw_gname, entries in game_video_list.items():
        canon = resolve_gname(raw_gname)
        game_video_list_resolved.setdefault(canon, []).extend(entries)
    game_video_list = game_video_list_resolved

    # Warn about games with no matching playlist
    if playlist_data.get("playlists"):
        no_playlist = [
            g
            for g in game_cumulative
            if not any(_matches_playlist(g, pl.get("title", "")) for pl in playlist_data["playlists"])
        ]
        if no_playlist:
            print(f"  Warning: {len(no_playlist)} game(s) have no matching playlist: {', '.join(no_playlist)}")

    for gname, video_dates in game_cumulative.items():
        video_dates.sort()
        ep_count = len(video_dates)

        # Episode milestones (from video publish dates)
        for m in sorted(GAME_EP_THRESH, reverse=True):
            if ep_count >= m:
                key = f"game_{gname}_ep_{m}"
                date = video_dates[m - 1]
                new_reached[key] = date

        # Return milestones (longest gap between consecutive videos)
        if ep_count >= 2:
            try:
                dates_dt = sorted(datetime.strptime(d, "%Y-%m-%d") for d in video_dates)
                max_gap = 0
                gap_end_idx = 0
                for i in range(len(dates_dt) - 1):
                    gap = (dates_dt[i + 1] - dates_dt[i]).days
                    if gap > max_gap:
                        max_gap = gap
                        gap_end_idx = i + 1
                gap = max_gap
                gap_end = video_dates[gap_end_idx]
                key = f"game_{gname}_return_{gap}"
                new_reached[key] = gap_end
            except Exception:
                pass

    # Series return milestones (longest gap between consecutive videos in a series)
    for sname, svideo_dates in series_cumulative.items():
        if len(svideo_dates) >= 2:
            try:
                svideo_dates.sort()
                s_dates_dt = [datetime.strptime(d, "%Y-%m-%d") for d in svideo_dates]
                s_max_gap = 0
                s_gap_end_idx = 0
                for i in range(len(s_dates_dt) - 1):
                    s_gap = (s_dates_dt[i + 1] - s_dates_dt[i]).days
                    if s_gap > s_max_gap:
                        s_max_gap = s_gap
                        s_gap_end_idx = i + 1
                if s_max_gap >= HIATUS_DAYS_THRESH:
                    skey = f"series_{sname}_return_{s_max_gap}"
                    new_reached[skey] = svideo_dates[s_gap_end_idx]
            except Exception:
                pass

    # Series started milestone per game
    for gname in game_cumulative:
        key = f"game_{gname}_started"
        if key not in new_reached:
            new_reached[key] = game_cumulative[gname][0]

    # Build playlist mappings: by game name and by series name (uses _matches_playlist)
    game_to_playlist, series_to_playlist = _build_playlist_index(playlist_data, game_cumulative, game_first_series)

    # Per-game view/hour milestones from video_history.json (YouTube Analytics API)
    video_history = read_json("video_history.json") or {}
    # Build series_first_game mapping from all videos (needed for milestone links)
    series_first_game = {}
    for v in all_videos:
        s = v.get("series", {})
        sname = (s or {}).get("series_name", "")
        gname = resolve_gname((s or {}).get("game", ""))
        if sname and gname and sname not in series_first_game:
            series_first_game[sname] = gname
    if video_history:
        # Build game -> [video_id] mapping (resolved names)
        game_videos = {}
        for v in all_videos:
            vid = v.get("video_id", "")
            s = v.get("series", {})
            gname = resolve_gname((s or {}).get("game", ""))
            if gname and vid and vid in video_history:
                game_videos.setdefault(gname, []).append(vid)
            elif gname and vid:
                # Video in youtube_main but not yet in video_history; seed with current views
                game_videos.setdefault(gname, [])
                game_videos[gname].append(vid)

        # Filter out non-game content series (Railway Exhibition Vlogs, etc.)
        if VALID_GAMES:
            game_videos = {g: v for g, v in game_videos.items() if g in VALID_GAMES}

        game_view_thresh = GAME_EP_THRESH
        game_hour_thresh = GAME_EP_THRESH

        for gname, vids in game_videos.items():
            # Collect all dates from video_history for this game's videos
            date_views = {}
            for vid in vids:
                vh = video_history.get(vid, {})
                daily = vh.get("daily", {})
                for d, dv in daily.items():
                    date_views.setdefault(d, 0)
                    date_views[d] += dv.get("views", 0)

            if not date_views:
                continue

            sorted_dates = sorted(date_views.keys())

            # View milestones
            for m in sorted(game_view_thresh, reverse=True):
                found_date = None
                run_views = 0
                for d in sorted_dates:
                    run_views += date_views[d]
                    if run_views >= m:
                        found_date = d
                        break
                if found_date:
                    key = f"game_{gname}_views_{m}"
                    new_reached[key] = found_date

            # Hour milestones (watch_time is in minutes from analytics; convert to hours)
            date_watch = {}
            for d in sorted_dates:
                total_watch = 0
                for vid in vids:
                    vh = video_history.get(vid, {})
                    dd = vh.get("daily", {}).get(d, {})
                    total_watch += dd.get("watch_time", 0)
                date_watch[d] = total_watch // 60  # minutes to hours

            for m in sorted(game_hour_thresh, reverse=True):
                found_date = None
                run_hours = 0
                for d in sorted_dates:
                    run_hours += date_watch.get(d, 0)
                    if run_hours >= m:
                        found_date = d
                        break
                if found_date:
                    key = f"game_{gname}_hours_{m}"
                    new_reached[key] = found_date

        # Per-series view/hour milestones from video_history.json
        # Build series -> [video_id] mapping
        series_videos = {}
        for v in all_videos:
            vid = v.get("video_id", "")
            s = v.get("series", {})
            sname = (s or {}).get("series_name", "")
            gname = resolve_gname((s or {}).get("game", ""))
            if sname and vid and gname and vid in video_history:
                series_videos.setdefault(sname, []).append(vid)
                if sname not in series_first_game:
                    series_first_game[sname] = gname

        for sname, svids in series_videos.items():
            s_date_views = {}
            s_date_watch = {}
            for vid in svids:
                vh = video_history.get(vid, {})
                daily = vh.get("daily", {})
                for d, dv in daily.items():
                    s_date_views.setdefault(d, 0)
                    s_date_views[d] += dv.get("views", 0)
                    s_date_watch.setdefault(d, 0)
                    s_date_watch[d] += dv.get("watch_time", 0)

            if not s_date_views:
                continue

            s_sorted = sorted(s_date_views.keys())

            for m in sorted(game_view_thresh, reverse=True):
                found = None
                run = 0
                for d in s_sorted:
                    run += s_date_views[d]
                    if run >= m:
                        found = d
                        break
                if found:
                    key = f"series_{sname}_views_{m}"
                    new_reached[key] = found

            for m in sorted(game_hour_thresh, reverse=True):
                found = None
                run = 0
                for d in s_sorted:
                    run += s_date_watch.get(d, 0) // 60
                    if run >= m:
                        found = d
                        break
                if found:
                    key = f"series_{sname}_hours_{m}"
                    new_reached[key] = found

    # Per-game upload hours (content creation time from video duration_seconds)
    game_durations = {}  # gname -> total seconds
    channel_duration_secs = 0
    for v in all_videos:
        s = v.get("series", {})
        gname = resolve_gname((s or {}).get("game", ""))
        dur = v.get("duration_seconds", 0)
        if gname and dur:
            game_durations.setdefault(gname, 0)
            game_durations[gname] += dur
        if dur:
            channel_duration_secs += dur

    vods_duration_secs = 0
    for v in yt_vods_data.get("videos", []):
        dur = v.get("duration_seconds", 0)
        if dur:
            vods_duration_secs += dur

    # Filter out non-game content series for upload milestones
    if VALID_GAMES:
        game_durations = {g: s for g, s in game_durations.items() if g in VALID_GAMES}

    upload_thresh = [m for m in GAME_EP_THRESH if m >= 1]
    for gname, total_secs in game_durations.items():
        upload_hours = total_secs // 3600
        for m in sorted(upload_thresh, reverse=True):
            if upload_hours >= m:
                key = f"game_{gname}_upload_{m}"
                # Use the publish date of the video that pushed us over the threshold
                cum = 0
                for v in sorted(all_videos, key=lambda x: x.get("published", "")):
                    vs = v.get("series", {})
                    if resolve_gname((vs or {}).get("game", "")) == gname:
                        cum += v.get("duration_seconds", 0)
                        if cum // 3600 >= m:
                            date = v.get("published", "")[:10]
                            new_reached[key] = date
                            break

    # Per-series upload hours from video duration_seconds
    series_durations = {}
    for v in all_videos:
        s = v.get("series", {})
        sname = (s or {}).get("series_name", "")
        dur = v.get("duration_seconds", 0)
        if sname and dur:
            series_durations.setdefault(sname, 0)
            series_durations[sname] += dur

    for sname, total_secs in series_durations.items():
        uh = total_secs // 3600
        for m in sorted(upload_thresh, reverse=True):
            if uh >= m:
                key = f"series_{sname}_upload_{m}"
                cum = 0
                for v in sorted(all_videos, key=lambda x: x.get("published", "")):
                    vs = v.get("series", {})
                    if (vs or {}).get("series_name", "") == sname:
                        cum += v.get("duration_seconds", 0)
                        if cum // 3600 >= m:
                            date = v.get("published", "")[:10]
                            new_reached[key] = date
                            break

    # Per-platform and combined upload hours (content creation time)
    def _track_upload(prefix, videos):
        dur = sum(v.get("duration_seconds", 0) for v in videos)
        upload_hours = dur // 3600
        for m in sorted(HOURS_THRESH, reverse=True):
            if upload_hours >= m:
                key = f"{prefix}_upload_{m}"
                cum = 0
                for v in sorted(videos, key=lambda x: x.get("published", "")):
                    cum += v.get("duration_seconds", 0)
                    if cum // 3600 >= m:
                        date = v.get("published", "")[:10]
                        new_reached[key] = date
                        break

    _track_upload("youtube", all_videos)
    _track_upload("vods", yt_vods_data.get("videos", []))
    _track_upload("combined", all_videos + yt_vods_data.get("videos", []))

    # Age milestone
    first_video_date = None
    for v in all_videos:
        pub = (v.get("published") or "")[:10]
        if pub and (first_video_date is None or pub < first_video_date):
            first_video_date = pub
    if first_video_date:
        fd = datetime.strptime(first_video_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        age_days = (now - fd).days
        for m in reversed(AGE_DAYS_THRESH):
            if age_days >= m:
                key = f"age_{m}"
                age_date = (fd + timedelta(days=m)).strftime("%Y-%m-%d")
                new_reached[key] = age_date

    # Channel hiatus milestones (every gap exceeding HIATUS_DAYS_THRESH)
    hiatus_thresh = ALL_THRESH

    def _track_hiatus(dates, prefix):
        if len(dates) < 2:
            return
        dt_list = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
        for i in range(len(dt_list) - 1):
            gap = (dt_list[i + 1] - dt_list[i]).days
            if gap < HIATUS_DAYS_THRESH:
                continue
            gap_end = dates[i + 1]
            for m in sorted(hiatus_thresh, reverse=True):
                if gap >= m:
                    key = f"hiatus_{prefix}{m}" if prefix else f"hiatus_{m}"
                    if key not in new_reached or gap_end < new_reached[key]:
                        new_reached[key] = gap_end
                    break

    main_dates = sorted(set(v.get("published", "")[:10] for v in all_videos if v.get("published")))
    _track_hiatus(main_dates, "")

    # VODs hiatus
    yt_vods = read_json("youtube_vods.json") or {}
    vods_videos = yt_vods.get("videos", [])
    if vods_videos:
        vods_dates = sorted(set(v.get("published", "")[:10] for v in vods_videos if v.get("published")))
        _track_hiatus(vods_dates, "vods_")

    # Weekly upload streak (consecutive calendar weeks with at least one upload)
    if len(all_videos) >= 2:
        all_date_set = sorted(set(v.get("published", "")[:10] for v in all_videos if v.get("published")))
        if len(all_date_set) >= 2:
            week_dates = {}
            for d in all_date_set:
                dt = datetime.strptime(d, "%Y-%m-%d")
                iso = dt.isocalendar()
                wk = iso[0] * 100 + iso[1]
                week_dates.setdefault(wk, []).append(d)
            sorted_weeks = sorted(week_dates.keys())
            longest = 0
            cur = 0
            streak_end = None
            for i, wk in enumerate(sorted_weeks):
                if i == 0 or wk - sorted_weeks[i - 1] != 1:
                    cur = 1
                else:
                    cur += 1
                if cur > longest:
                    longest = cur
                    streak_end = max(week_dates[wk])
            if longest >= 2:
                key = f"streak_{longest}"
                new_reached[key] = streak_end

    # VODs weekly upload streak
    if len(vods_videos) >= 2:
        vods_date_set = sorted(set(v.get("published", "")[:10] for v in vods_videos if v.get("published")))
        if len(vods_date_set) >= 2:
            vods_week_dates = {}
            for d in vods_date_set:
                dt = datetime.strptime(d, "%Y-%m-%d")
                iso = dt.isocalendar()
                wk = iso[0] * 100 + iso[1]
                vods_week_dates.setdefault(wk, []).append(d)
            vods_sorted_weeks = sorted(vods_week_dates.keys())
            vods_longest = 0
            vods_cur = 0
            vods_streak_end = None
            for i, wk in enumerate(vods_sorted_weeks):
                if i == 0 or wk - vods_sorted_weeks[i - 1] != 1:
                    vods_cur = 1
                else:
                    vods_cur += 1
                if vods_cur > vods_longest:
                    vods_longest = vods_cur
                    vods_streak_end = max(vods_week_dates[wk])
            if vods_longest >= 2:
                key = f"streak_vods_{vods_longest}"
                new_reached[key] = vods_streak_end

    # Video linking metadata stored alongside milestones
    milestone_links = {}

    # Anniversary milestones from custom milestone dates
    md_file = os.path.join(DATA_DIR, "..", "_data", "milestone_dates.yml")
    if os.path.exists(md_file):
        with open(md_file) as f:
            milestone_dates = yaml.safe_load(f) or []
        # Build caps map by category: each entry's milestones are capped at the
        # next entry's date in the same category (sorted chronologically).
        # Uncategorized entries are unaffected.
        caps = {}
        category_entries = {}
        for md_entry in milestone_dates:
            md_label = md_entry.get("label", "")
            raw_date = md_entry.get("date", "")
            category = md_entry.get("category", "")
            if not md_label or not raw_date or not category:
                continue
            if isinstance(raw_date, dt_date) and not isinstance(raw_date, datetime):
                md_date = raw_date.strftime("%Y-%m-%d")
            else:
                md_date = str(raw_date)[:10]
            slug = md_label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(",", "")
            category_entries.setdefault(category, []).append((md_date, slug))
        for _category, entries in category_entries.items():
            sorted_entries = sorted(entries, key=lambda x: x[0])
            for i, (_entry_date, slug) in enumerate(sorted_entries):
                if i + 1 < len(sorted_entries):
                    caps[slug] = sorted_entries[i + 1][0]
        for md_entry in milestone_dates:
            raw_date = md_entry.get("date", "")
            md_label = md_entry.get("label", "")
            if not raw_date or not md_label:
                continue
            if isinstance(raw_date, dt_date) and not isinstance(raw_date, datetime):
                md_date = raw_date.strftime("%Y-%m-%d")
            else:
                md_date = str(raw_date)[:10]
            try:
                base_dt = datetime.strptime(md_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if (now - base_dt).days < 0:
                continue  # future date, skip
            slug = md_label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(",", "")
            link_text = md_label
            # Compute cap date if this slug is superseeded by a later entry in its category
            cap_at = None
            if slug in caps:
                cap_raw = caps[slug]
                if isinstance(cap_raw, dt_date) and not isinstance(cap_raw, datetime):
                    cap_str = cap_raw.strftime("%Y-%m-%d")
                else:
                    cap_str = str(cap_raw)[:10]
                with contextlib.suppress(ValueError):
                    cap_at = datetime.strptime(cap_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            for m in reversed(ANNIVERSARY_THRESH):
                ann = base_dt + relativedelta(years=+m)
                if ann.month == 2 and ann.day == 29:
                    ann = ann.replace(month=3, day=1)
                ann_str = ann.strftime("%Y-%m-%d")
                if ann_str > today:
                    continue  # anniversary hasn't happened yet
                # If this entry belongs to a category, suppress milestones on or after
                # the next entry's date in that category
                if cap_at and ann >= cap_at:
                    continue
                key = f"anniversary_{slug}_{m}"
                new_reached[key] = ann_str
                if key not in milestone_links:
                    milestone_links[key] = {"label": link_text}

    # First video to reach N views (from video_history.json)
    if video_history and all_videos:
        vid_map = {}
        for v in all_videos:
            vid_map[v.get("video_id", "")] = v
        for m in sorted(VIDEO_FIRST_THRESH, reverse=True):
            best_date = None
            best_vid = None
            for vid, vh in video_history.items():
                daily = vh.get("daily", {})
                if not daily:
                    continue
                sd = sorted(daily.keys())
                cum = 0
                for d in sd:
                    cum += daily[d].get("views", 0)
                    if cum >= m:
                        if best_date is None or d < best_date:
                            best_date = d
                            best_vid = vid
                        break
            if best_date and best_vid:
                key = f"video_first_{m}"
                new_reached[key] = best_date
                vi = vid_map.get(best_vid, {})
                title = vi.get("title", video_history.get(best_vid, {}).get("title", ""))
                entry = {"url": f"/videos#vid-{best_vid}", "text": title}
                thumb = vi.get("thumbnail", "")
                if thumb:
                    entry["thumb"] = thumb
                milestone_links[key] = entry

    # Add game milestone links: episode milestones link to specific video; others link to playlist
    for key in list(new_reached.keys()):
        if key.startswith("game_"):
            rest = key[len("game_") :]
            for sep in ["_ep_", "_views_", "_hours_", "_return_", "_upload_", "_started"]:
                if sep in rest:
                    gname = rest.split(sep)[0]
                    entry = None
                    pl = game_to_playlist.get(gname) or series_to_playlist.get(gname)
                    game_icon = game_icons.get(gname, "")

                    if sep == "_ep_":
                        # Game-level: video-specific link, use game icon, fallback to playlist thumbnail
                        try:
                            ep_num = int(rest.split(sep)[1])
                        except ValueError:
                            ep_num = 0
                        vlist = game_video_list.get(gname, [])
                        if 0 < ep_num <= len(vlist):
                            _, vid, _thumb, title = vlist[ep_num - 1]
                            entry = {"url": f"/videos#vid-{vid}", "text": title}

                            if game_icon:
                                entry["thumb"] = game_icon
                            elif pl and pl.get("thumbnail"):
                                entry["thumb"] = pl["thumbnail"]
                            if gname in game_first_series:
                                entry["series_name"] = game_first_series[gname]

                    elif sep in ("_started", "_return_"):
                        # Game-level milestones: game icon for thumb, playlist url for link
                        if pl and pl.get("playlist_id"):
                            entry = {"url": f"/playlists#pl-{pl['playlist_id']}"}
                        else:
                            entry = {"url": "/games"}
                        if game_icon:
                            entry["thumb"] = game_icon
                        elif pl and pl.get("thumbnail"):
                            entry["thumb"] = pl["thumbnail"]
                        if gname in game_first_series:
                            entry["series_name"] = game_first_series[gname]

                    else:
                        # Game-level milestones (_views_, _hours_, _upload_): use game icon
                        if pl and pl.get("playlist_id"):
                            entry = {"url": f"/playlists#pl-{pl['playlist_id']}"}
                        else:
                            entry = {"url": "/games"}
                        if game_icon:
                            entry["thumb"] = game_icon
                        if gname in game_first_series:
                            entry["series_name"] = game_first_series[gname]

                    if entry:
                        milestone_links[key] = entry
                    break

    # Series milestone links: use playlist thumbnail if available, fallback to game icon
    try:
        _ = series_first_game
    except NameError:
        series_first_game = {}
    for key in list(new_reached.keys()):
        if key.startswith("series_"):
            rest = key[7:]
            for sep in ("_views_", "_hours_", "_upload_", "_return_"):
                if sep in rest:
                    sname = rest.split(sep)[0]
                    gname = series_first_game.get(sname, "")
                    pl = game_to_playlist.get(gname) or series_to_playlist.get(gname)
                    game_icon = game_icons.get(gname, "")
                    entry = {}
                    if pl and pl.get("playlist_id"):
                        entry["url"] = f"/playlists#pl-{pl['playlist_id']}"
                        if pl.get("thumbnail"):
                            entry["thumb"] = pl["thumbnail"]
                    else:
                        entry["url"] = "/games"
                    if not entry.get("thumb") and game_icon:
                        entry["thumb"] = game_icon
                    entry["series_name"] = sname
                    milestone_links[key] = entry
                    break

    # Platform milestones (Twitch followers/views, Fourthwall orders)
    twitch_stats = read_json("twitch_stats.json") or {}
    fourthwall = read_json("fourthwall.json") or {}
    platforms = [
        ("twitch_followers", twitch_stats.get("follower_count", 0)),
        ("twitch_views", twitch_stats.get("view_count", 0)),
        ("store_orders", fourthwall.get("total_orders", 0)),
    ]
    for prefix, value in platforms:
        for m in sorted(ALL_THRESH, reverse=True):
            if value >= m:
                key = f"{prefix}_{m}"
                if key in prev_reached:
                    new_reached[key] = prev_reached[key]
                else:
                    new_reached[key] = today

    # Channel-level milestone thumbnails (use channel avatar) and custom messages
    channel_avatar = site_meta.get("avatar_url", "")
    if channel_avatar:
        for key in list(new_reached.keys()):
            if (
                key not in milestone_links
                and not key.startswith("game_")
                and not key.startswith("video_first_")
                and not key.startswith("series_")
            ):
                entry = {"thumb": channel_avatar}
                if key in custom_msgs:
                    entry["msg"] = custom_msgs[key]
                milestone_links[key] = entry

    # Add channel avatar and text to anniversary milestones
    for key in list(milestone_links.keys()):
        if key.startswith("anniversary_") and "thumb" not in milestone_links[key]:
            milestone_links[key]["thumb"] = channel_avatar
            parts = key.split("_")
            m = parts[-1]
            label = milestone_links[key].get("label", "unknown")
            if m == "1":
                milestone_links[key]["text"] = f"1 year since {label}"
            else:
                milestone_links[key]["text"] = f"{m} years since {label}"

    # Catch-all: fill any game/series milestone missing a thumbnail with channel avatar
    if channel_avatar:
        for key in list(milestone_links.keys()):
            if not milestone_links[key].get("thumb"):
                milestone_links[key]["thumb"] = channel_avatar

    # Map milestone key to an icon HTML entity
    def _milestone_icon(key):
        if key.startswith("video_first_likes_"):
            return "&#128077;"  # thumbs up
        if key.startswith("video_first_comments_"):
            return "&#128172;"  # speech bubble
        if key.startswith("video_first_"):
            return "&#127916;"  # movie camera
        if key.startswith("game_") or key.startswith("series_"):
            return "&#127918;"  # joystick
        if key.startswith("anniversary_") or key.startswith("age_"):
            return "&#127800;"  # cherry blossom
        if key.startswith("hiatus_"):
            return "&#127987;"  # flag
        if key.startswith("streak_"):
            return "&#128293;"  # fire
        if ("hours_" in key) or ("_hours_" in key):
            return "&#9200;"  # clock
        if "upload_" in key:
            return "&#128221;"  # notebook
        if key.startswith("twitch_followers_") or key.startswith("store_orders_"):
            return "&#11088;"  # star (subs/store)
        if "views" in key or "views_" in key:
            return "&#128065;"  # eye
        if "videos" in key:
            return "&#127916;"  # movie camera
        if "likes" in key:
            return "&#128077;"  # thumbs up
        if "comments" in key:
            return "&#128172;"  # speech bubble
        return "&#11088;"  # star (default)

    # Generate display text for ALL milestones (single source of truth for marquee and timeline)
    def _milestone_msg(key):
        if key.startswith("game_"):
            rest = key[5:]
            if "_ep_" in rest:
                g, _, n = rest.partition("_ep_")
                return f"{n} episodes in {g}"
            if "_upload_" in rest:
                g, _, n = rest.partition("_upload_")
                return f"{n} hours uploaded in {g}"
            if "_started" in rest:
                g = rest.replace("_started", "")
                sname = game_first_series.get(g, "")
                return f"{sname} ({g}) started" if sname else f"{g} series started"
            if "_views_" in rest:
                g, _, n = rest.partition("_views_")
                return f"{n} views across {g}"
            if "_hours_" in rest:
                g, _, n = rest.partition("_hours_")
                return f"{n} hours watched in {g}"
            if "_return_" in rest:
                g, _, n = rest.partition("_return_")
                return f"Back to {g} after {n} days"
            return key
        if key.startswith("age_"):
            return f"{key[4:]} days old"
        if key.startswith("hiatus_vods_"):
            return f"VODs hiatus ended after {key[12:]} days"
        if key.startswith("hiatus_"):
            return f"Returned after hiatus of {key[7:]} days"
        if key.startswith("streak_vods_"):
            return f"{key[12:]}-week VODs upload streak"
        if key.startswith("streak_"):
            return f"{key[7:]}-week upload streak"
        if key.startswith("video_first_likes_"):
            v = key[18:]
            link = milestone_links.get(key, {})
            title = link.get("text", "")
            return f"First video to {v} likes: {title}" if title else f"First video to {v} likes"
        if key.startswith("video_first_comments_"):
            v = key[21:]
            link = milestone_links.get(key, {})
            title = link.get("text", "")
            return f"First video to {v} comments: {title}" if title else f"First video to {v} comments"
        if key.startswith("video_first_"):
            v = key[12:]
            link = milestone_links.get(key, {})
            title = link.get("text", "")
            return f"First video to {v} views: {title}" if title else f"First video to {v} views"
        if key.startswith("series_"):
            rest = key[7:]
            if "_views_" in rest:
                sname, _, n = rest.partition("_views_")
                return f"{n} views in {sname}"
            if "_hours_" in rest:
                sname, _, n = rest.partition("_hours_")
                return f"{n} hours watched in {sname}"
            if "_upload_" in rest:
                sname, _, n = rest.partition("_upload_")
                return f"{n} hours uploaded in {sname}"
            if "_return_" in rest:
                sname, _, n = rest.partition("_return_")
                return f"Back to {sname} after {n} days"
            return key
        if key.startswith("twitch_followers_"):
            return f"{key[17:]} Twitch followers"
        if key.startswith("twitch_views_"):
            return f"{key[13:]} Twitch views"
        if key.startswith("store_orders_"):
            return f"{key[13:]} store orders"
        if key.startswith("youtube_hours_"):
            return f"{key[14:]} hours watched on YouTube"
        if key.startswith("combined_hours_"):
            return f"{key[16:]} hours watched across all channels"
        if key.startswith("youtube_upload_"):
            return f"{key[15:]} hours uploaded on YouTube"
        if key.startswith("vods_upload_"):
            return f"{key[12:]} hours uploaded on VODs"
        if key.startswith("combined_upload_"):
            return f"{key[16:]} hours uploaded across all channels"
        if key.startswith("youtube_likes_"):
            return f"{key[14:]} likes on YouTube"
        if key.startswith("vods_likes_"):
            return f"{key[11:]} likes on VODs"
        if key.startswith("combined_likes_"):
            return f"{key[16:]} likes across all channels"
        if key.startswith("youtube_comments_"):
            return f"{key[17:]} comments on YouTube"
        if key.startswith("vods_comments_"):
            return f"{key[14:]} comments on VODs"
        if key.startswith("combined_comments_"):
            return f"{key[19:]} comments across all channels"
        if key.startswith("anniversary_"):
            link = milestone_links.get(key, {})
            text = link.get("text", "")
            if text:
                return text
            parts = key[len("anniversary_") :].split("_")
            y = parts[-1]
            label = " ".join(parts[:-1]).capitalize()
            return f"{y} year{'s' if y != '1' else ''} since {label}"
        if key in custom_msgs:
            return custom_msgs[key]
        parts = key.rsplit("_", 1)
        try:
            m = int(parts[1])
        except ValueError:
            return key
        return f"{m:,} {parts[0]}"

    for key in list(new_reached.keys()):
        if key not in milestone_links:
            milestone_links[key] = {}
        if "msg" not in milestone_links[key]:
            milestone_links[key]["msg"] = _milestone_msg(key)

    # Per-platform and combined watch time (hours) from video_history.json
    if video_history:
        daily_hours = {}
        for _vid, vh in video_history.items():
            for d, dv in vh.get("daily", {}).items():
                daily_hours.setdefault(d, 0)
                daily_hours[d] += dv.get("watch_time", 0) / 60.0
        if daily_hours:
            sorted_dates = sorted(daily_hours.keys())
            for m in sorted(HOURS_THRESH, reverse=True):
                cum = 0
                for d in sorted_dates:
                    cum += daily_hours[d]
                    if cum >= m:
                        key = f"youtube_hours_{m}"
                        new_reached[key] = d
                        break

    # Collapse milestones: for each label, keep only the highest threshold per date
    def collapse_key(key):
        return key.rsplit("_", 1)[0]

    def threshold_val(key):
        try:
            return int(key.rsplit("_", 1)[1])
        except ValueError:
            return -1

    collapsed = {}
    groups = {}
    for key, date in new_reached.items():
        groups.setdefault((collapse_key(key), date), []).append(key)
    for (_, date), keys in groups.items():
        best = max(keys, key=threshold_val)
        collapsed[best] = date
    new_reached = collapsed

    # Remove combined_likes/comments if they duplicate youtube likes/comments (same date)
    for key in list(new_reached.keys()):
        if key.startswith("youtube_likes_") or key.startswith("youtube_comments_"):
            combined_key = "combined_" + key[len("youtube_") :]
            if combined_key in new_reached and new_reached[combined_key] == new_reached[key]:
                del new_reached[combined_key]

    for key, date in new_reached.items():
        if key not in prev_reached:
            parts = key.rsplit("_", 1)
            try:
                m = int(parts[1])
            except ValueError:
                m = None
            if key.startswith("age_"):
                print(f"  New milestone: {m} days old (date={date})")
            elif key.startswith("hiatus_vods_"):
                print(f"  New milestone: VODs hiatus ended after {m} days (date={date})")
            elif key.startswith("hiatus_"):
                print(f"  New milestone: returned after hiatus of {m} days (date={date})")
            elif key.startswith("streak_vods_"):
                print(f"  New milestone: vods {m}-week upload streak (date={date})")
            elif key.startswith("streak_"):
                print(f"  New milestone: {m} week upload streak (date={date})")
            elif key.startswith("video_first_"):
                link = milestone_links.get(key, {})
                title = link.get("text", "")
                print(f"  New milestone: first video to {m:,} views (date={date}) - {title}")
            elif key.startswith("youtube_upload_"):
                print(f"  New milestone: {m:,} content hours on YouTube (date={date})")
            elif key.startswith("vods_upload_"):
                print(f"  New milestone: {m:,} content hours on VODs (date={date})")
            elif key.startswith("combined_upload_"):
                print(f"  New milestone: {m:,} content hours across all channels (date={date})")
            elif key.startswith("youtube_hours_"):
                print(f"  New milestone: {m:,} watch hours on YouTube (date={date})")
            elif key.startswith("combined_hours_"):
                print(f"  New milestone: {m:,} watch hours across all channels (date={date})")
            elif key.startswith("youtube_likes_"):
                print(f"  New milestone: {m:,} likes on YouTube (date={date})")
            elif key.startswith("vods_likes_"):
                print(f"  New milestone: {m:,} likes on VODs (date={date})")
            elif key.startswith("combined_likes_"):
                print(f"  New milestone: {m:,} likes across all channels (date={date})")
            elif key.startswith("youtube_comments_"):
                print(f"  New milestone: {m:,} comments on YouTube (date={date})")
            elif key.startswith("vods_comments_"):
                print(f"  New milestone: {m:,} comments on VODs (date={date})")
            elif key.startswith("combined_comments_"):
                print(f"  New milestone: {m:,} comments across all channels (date={date})")
            elif key.startswith("game_"):
                rest = key[len("game_") :]
                if "_ep_" in rest:
                    g, _, n = rest.partition("_ep_")
                    print(f"  New milestone: {n} episodes in {g} (date={date})")
                elif "_upload_" in rest:
                    g, _, n = rest.partition("_upload_")
                    print(f"  New milestone: {n} content hours in {g} (date={date})")
                elif "_started" in rest:
                    g = rest.replace("_started", "")
                    print(f"  New milestone: {g} series started (date={date})")
                elif "_views_" in rest:
                    g, _, n = rest.partition("_views_")
                    print(f"  New milestone: {n} views across {g} (date={date})")
                elif "_hours_" in rest:
                    g, _, n = rest.partition("_hours_")
                    print(f"  New milestone: {n} hours in {g} (date={date})")
                elif "_return_" in rest:
                    g, _, n = rest.partition("_return_")
                    print(f"  New milestone: Back to {g} after {n} days (date={date})")
            else:
                print(f"  New milestone: {m:,} {parts[0]} (date={date})")

    # Fallback: compute game/series view and video-first milestones from per-video totals
    # when video_history.json (YouTube Analytics) is unavailable
    if not video_history and all_videos:
        if debug:
            print("  INFO: video_history.json unavailable; estimating view milestones from per-video totals")

        # Game view milestones
        game_view_data = {}
        for v in all_videos:
            s = v.get("series", {})
            gname = resolve_gname((s or {}).get("game", ""))
            if gname:
                game_view_data.setdefault(gname, []).append(v)
        if VALID_GAMES:
            game_view_data = {g: vs for g, vs in game_view_data.items() if g in VALID_GAMES}

        for gname, vobs in game_view_data.items():
            sorted_vobs = sorted(vobs, key=lambda x: x.get("published", ""))
            cum = 0
            for v in sorted_vobs:
                cum += v.get("view_count", 0)
                pub = v.get("published", "")[:10]
                for m in sorted(GAME_EP_THRESH, reverse=True):
                    key = f"game_{gname}_views_{m}"
                    if cum >= m and key not in new_reached:
                        new_reached[key] = pub

        # Series view milestones
        series_view_data = {}
        for v in all_videos:
            s = v.get("series", {})
            sname = (s or {}).get("series_name", "")
            if sname:
                series_view_data.setdefault(sname, []).append(v)

        for sname, svobs in series_view_data.items():
            sorted_sv = sorted(svobs, key=lambda x: x.get("published", ""))
            cum = 0
            for v in sorted_sv:
                cum += v.get("view_count", 0)
                pub = v.get("published", "")[:10]
                for m in sorted(GAME_EP_THRESH, reverse=True):
                    key = f"series_{sname}_views_{m}"
                    if cum >= m and key not in new_reached:
                        new_reached[key] = pub

        # Video-first milestones: first video to individually reach N views
        sorted_main = sorted(all_videos, key=lambda x: x.get("published", ""))

        for m in sorted(VIDEO_FIRST_THRESH, reverse=True):
            for v in sorted_main:
                if v.get("view_count", 0) >= m:
                    key = f"video_first_{m}"
                    if key not in new_reached:
                        new_reached[key] = v.get("published", "")[:10]
                        entry = {"url": f"/videos#vid-{v.get('video_id', '')}", "text": v.get("title", "")}
                        thumb = v.get("thumbnail", "")
                        if thumb:
                            entry["thumb"] = thumb
                        milestone_links[key] = entry
                    break

    # Sort milestones: descending by date, then by threshold descending within same date
    def sort_key(item):
        key, date = item
        parts = key.rsplit("_", 1)
        threshold = int(parts[-1]) if parts[-1].isdigit() else 0
        return (date, threshold)

    if debug:
        print(f"\n  Milestones detected: {len(new_reached)}")
        for k, v in sorted(new_reached.items(), key=sort_key, reverse=True)[:15]:
            print(f"    {k}: {v}")
        if len(new_reached) > 15:
            print(f"    ... and {len(new_reached) - 15} more")

    # Build current milestone list for marquee (all milestones within cutoff)
    cutoff_dt = now - timedelta(days=14)
    current_list = []
    for key, date in sorted(new_reached.items(), key=sort_key, reverse=True):
        try:
            d = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if d < cutoff_dt:
            continue

        link = milestone_links.get(key, {})
        msg = link.get("msg", key)
        icon = _milestone_icon(key)
        current_list.append({"message": msg, "icon": icon})

    # Final cleanup: strip stale _0 and empty-threshold keys from all structures
    _nr_vf_before = [k for k in new_reached if k.startswith("video_first_")]
    if _nr_vf_before:
        print(f"  DEBUG video_first in new_reached before final cleanup ({len(_nr_vf_before)}):")
        for _k in sorted(_nr_vf_before):
            print(f"    {_k!r}: {new_reached[_k]}")
    for _k in list(new_reached.keys()):
        if _k.endswith("_0") or _k.endswith("_"):
            del new_reached[_k]
    for _k in list(milestone_links.keys()):
        if _k.endswith("_0") or _k.endswith("_"):
            del milestone_links[_k]
    _nr_vf_after = [k for k in new_reached if k.startswith("video_first_")]
    if _nr_vf_before and not _nr_vf_after:
        print("  DEBUG: final cleanup removed ALL video_first keys from new_reached")
    elif _nr_vf_after:
        print(f"  DEBUG video_first remaining after final cleanup ({len(_nr_vf_after)}):")
        for _k in sorted(_nr_vf_after):
            print(f"    {_k!r}: {new_reached[_k]}")
    else:
        print("  DEBUG: no video_first keys in new_reached at save time")

    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    sorted_reached = dict(sorted(new_reached.items(), key=sort_key, reverse=True))
    result = {"current": current_list, "reached": sorted_reached}
    if milestone_links:
        result["links"] = milestone_links
    with open(MILESTONES_FILE, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Written {MILESTONES_FILE} ({len(new_reached)} milestones, {len(current_list)} current)")
    with open(MILESTONES_FILE) as f:
        _reread = json.load(f)
    _rr_reached = _reread.get("reached", {})
    _rr_vf = {k: v for k, v in _rr_reached.items() if k.startswith("video_first_")}
    print(f"  REREAD VERIFY: {len(_rr_reached)} reached keys, {len(_rr_vf)} video_first_* entries")
    for _k in sorted(_rr_vf):
        print(f"    {_k!r}: {_rr_vf[_k]}")


if __name__ == "__main__":
    main()
