import json
import os
from datetime import datetime, timedelta, timezone

import yaml
from common import (
    ALIAS_MAP,
    ALL_THRESH,
    DATA_DIR,
    GAME_EP_THRESH,
    HIATUS_DAYS_THRESH,
    HOURS_THRESH,
    MILESTONE_SPECS,
    VALID_GAMES,
    VIDEO_FIRST_THRESH,
    read_json,
)

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

    # Total likes across all videos
    total_likes = sum(v.get("like_count", 0) for v in yt_main.get("videos", []))
    total_comments = sum(v.get("comment_count", 0) for v in yt_main.get("videos", []))

    # Load previous milestones for comparison
    prev = read_json("milestones.json") or {}
    prev_reached = prev.get("reached", {})
    new_reached = {}

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
    values = {"subs": subs, "views": views, "videos": videos_count, "likes": total_likes, "comments": total_comments}
    for label, thresholds, _msgs, _formatter in MILESTONE_SPECS:
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
    game_first_series = {}
    game_video_list = {}
    for v in all_videos:
        s = v.get("series", {})
        gname_raw = (s or {}).get("game", "")
        pub = v.get("published", "")[:10]
        if gname_raw and pub:
            game_cumulative.setdefault(gname_raw, []).append(pub)
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

    # Load game icons from game_links.yml
    game_icons = {}
    gl_path = os.path.join(DATA_DIR, "game_links.yml")
    if os.path.exists(gl_path):
        try:
            with open(gl_path) as f:
                _gl = yaml.safe_load(f) or {}
            for name, entry in _gl.items():
                if isinstance(entry, dict) and entry.get("icon"):
                    game_icons[name] = entry["icon"]
        except Exception:
            pass

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
        return gl_ns == pt_ns or pt_ns.startswith(gl_ns) or gl_ns.startswith(pt_ns)

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

    for gname, video_dates in game_cumulative.items():  # noqa: B007
        video_dates.sort()
    ep_count = len(video_dates)

    # Episode milestones (from video publish dates)
    for m in sorted(GAME_EP_THRESH, reverse=True):
        if ep_count >= m:
            key = f"game_{gname}_ep_{m}"
            date = video_dates[m - 1]
            new_reached[key] = date

    # Return milestones (longest gap between consecutive videos)
    if len(video_dates) >= 2:
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

    # First video per game for "series started" milestone, and ordered video list for episode links
    game_first_series = {}
    game_video_list = {}  # gname -> [(date, video_id, thumbnail, title), ...]
    for v in sorted(all_videos, key=lambda x: x.get("published", "")):
        s = v.get("series", {})
        if not s:
            continue
        gname = resolve_gname((s or {}).get("game", ""))
        sname = (s or {}).get("series_name", "")
        pub = v.get("published", "")[:10]
        vid = v.get("video_id", "")
        thumb = v.get("thumbnail", "")
        title = v.get("title", "")
        if gname and sname and gname not in game_first_series:
            game_first_series[gname] = sname
        if gname and pub and vid:
            game_video_list.setdefault(gname, []).append((pub, vid, thumb, title))

    # Series started milestone per game
    for gname in game_cumulative:
        key = f"game_{gname}_started"
        if key not in new_reached:
            new_reached[key] = game_cumulative[gname][0]

    # Build playlist mappings: by game name and by series name (uses _matches_playlist)
    game_to_playlist, series_to_playlist = _build_playlist_index(playlist_data, game_cumulative, game_first_series)

    # Per-game view/hour milestones from video_history.json (YouTube Analytics API)
    video_history = read_json("video_history.json") or {}
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

    # Channel upload hours (content creation time)
    channel_upload_hours = channel_duration_secs // 3600
    for m in sorted(HOURS_THRESH, reverse=True):
        if channel_upload_hours >= m:
            key = f"upload_{m}"
            cum = 0
            for v in sorted(all_videos, key=lambda x: x.get("published", "")):
                cum += v.get("duration_seconds", 0)
                if cum // 3600 >= m:
                    date = v.get("published", "")[:10]
                    new_reached[key] = date
                    break

    # Age milestone
    first_video_date = None
    for v in all_videos:
        pub = (v.get("published") or "")[:10]
        if pub and (first_video_date is None or pub < first_video_date):
            first_video_date = pub
    if first_video_date:
        fd = datetime.strptime(first_video_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        age_days = (now - fd).days
        for m in reversed(ALL_THRESH):
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

    # Video linking metadata stored alongside milestones
    milestone_links = {}

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
                        # Link episode milestones to the specific video; use series/playlist thumbnail
                        try:
                            ep_num = int(rest.split(sep)[1])
                        except ValueError:
                            ep_num = 0
                        vlist = game_video_list.get(gname, [])
                        if 0 < ep_num <= len(vlist):
                            _, vid, _thumb, title = vlist[ep_num - 1]
                            entry = {"url": f"/videos#vid-{vid}", "text": title}
                            # Prefer playlist thumbnail as series thumbnail; fall back to game icon
                            if pl and pl.get("thumbnail"):
                                entry["thumb"] = pl["thumbnail"]
                            elif game_icon:
                                entry["thumb"] = game_icon

                    elif sep == "_started":
                        # Link to playlist; use game icon + series_name
                        if pl and pl.get("playlist_id"):
                            entry = {"url": f"/playlists#pl-{pl['playlist_id']}"}
                            if gname in game_first_series:
                                entry["series_name"] = game_first_series[gname]
                        else:
                            entry = {"url": "/games"}
                        if game_icon:
                            entry["thumb"] = game_icon
                        if gname in game_first_series:
                            entry["series_name"] = game_first_series[gname]

                    else:
                        # views/hours/return/upload: link to playlist; use game icon as thumb
                        if pl and pl.get("playlist_id"):
                            entry = {"url": f"/playlists#pl-{pl['playlist_id']}"}
                        else:
                            entry = {"url": "/games"}
                        if game_icon:
                            entry["thumb"] = game_icon

                    if entry:
                        milestone_links[key] = entry
                    break

    # Channel-level milestone thumbnails (use channel avatar)
    channel_avatar = site_meta.get("avatar_url", "")
    if channel_avatar:
        channel_thumb = {"thumb": channel_avatar}
        for key in list(new_reached.keys()):
            if key not in milestone_links and not key.startswith("game_") and not key.startswith("video_first_"):
                milestone_links[key] = channel_thumb

    # Total watch time (hours) from video_history.json
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
                        key = f"hours_{m}"
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
            elif key.startswith("streak_"):
                print(f"  New milestone: {m} week upload streak (date={date})")
            elif key.startswith("video_first_"):
                link = milestone_links.get(key, {})
                title = link.get("text", "")
                print(f"  New milestone: first video to {m:,} views (date={date}) - {title}")
            elif key.startswith("hours_"):
                print(f"  New milestone: {m:,} total channel hours (date={date})")
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
            elif key.startswith("upload_"):
                print(f"  New milestone: {m:,} content hours created (date={date})")
            else:
                print(f"  New milestone: {m:,} {parts[0]} (date={date})")

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

        if key.startswith("game_"):
            rest = key[5:]
            if "_ep_" in rest:
                g, _, n = rest.partition("_ep_")
                msg = f"{n} episodes in {g}"
            elif "_upload_" in rest:
                g, _, n = rest.partition("_upload_")
                msg = f"{n} hours uploaded in {g}"
            elif "_started" in rest:
                g = rest.replace("_started", "")
                msg = f"{g} series started"
            elif "_views_" in rest:
                g, _, n = rest.partition("_views_")
                msg = f"{n} views across {g}"
            elif "_hours_" in rest:
                g, _, n = rest.partition("_hours_")
                msg = f"{n} hours watched in {g}"
            elif "_return_" in rest:
                g, _, n = rest.partition("_return_")
                msg = f"Back to {g} after {n} days"
            else:
                msg = key
        elif key.startswith("age_"):
            msg = f"{key[4:]} days old"
        elif key.startswith("hiatus_vods_"):
            msg = f"VODs hiatus ended after {key[12:]} days"
        elif key.startswith("hiatus_"):
            msg = f"Returned after hiatus of {key[7:]} days"
        elif key.startswith("streak_"):
            msg = f"{key[7:]}-week upload streak"
        elif key.startswith("video_first_"):
            v = key[12:]
            link = milestone_links.get(key, {})
            title = link.get("text", "")
            msg = f"First video to {v} views: {title}" if title else f"First video to {v} views"
        elif key.startswith("hours_"):
            msg = f"{key[6:]} hours watched"
        elif key.startswith("upload_"):
            msg = f"{key[7:]} hours uploaded"
        else:
            parts = key.rsplit("_", 1)
            try:
                m = int(parts[1])
            except ValueError:
                continue
            msg = f"{m:,} {parts[0]}"

        current_list.append({"message": msg})

    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    sorted_reached = dict(sorted(new_reached.items(), key=sort_key, reverse=True))
    result = {"current": current_list, "reached": sorted_reached}
    if milestone_links:
        result["links"] = milestone_links
    with open(MILESTONES_FILE, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Written {MILESTONES_FILE} ({len(new_reached)} milestones, {len(current_list)} current)")


if __name__ == "__main__":
    main()
