"""
Copy live _data files into the site as public static JSON endpoints.

Each JSON file is emitted as a Jekyll page (frontmatter + raw JSON body),
so it is served verbatim at https://skiylia.dev/api/<name>.json.
render_with_liquid: false stops Liquid treating the JSON braces as tags
(which is also very slow on large files like history.json).
"""

import json
import os

DATA_DIR = "_data"
API_DIR = os.path.join("archive", "api")

WHITELIST = [
    "games.json",
    "history.json",
    "site_meta.json",
    "milestones.json",
    "youtube_main.json",
    "playlists.json",
    "twitch_stats.json",
    "twitch_schedule.json",
]


def _page_for(name, raw):
    return f"---\nlayout: null\npermalink: /api/{name}\nrender_with_liquid: false\n---\n\n{raw.strip()}\n"


os.makedirs(API_DIR, exist_ok=True)
INDEX = {}
for name in WHITELIST:
    src = os.path.join(DATA_DIR, name)
    if not os.path.exists(src):
        continue
    with open(src) as f:
        raw = f.read()
    # Reuse the same filename so _site/api/<name> is served as <name>.
    with open(os.path.join(API_DIR, name), "w") as f:
        f.write(_page_for(name, raw))
    try:
        data = json.loads(raw)
    except Exception:
        data = None
    INDEX[name] = {
        "size": len(raw),
        "entries": len(data) if isinstance(data, list) else None,
    }

meta_md = "# Public API\n\nRead-only JSON snapshots of the site data pipeline, refreshed on each deploy.\n\n"
for name in sorted(INDEX):
    meta_md += f"- `/api/{name}` ({INDEX[name]['size']} bytes"
    if INDEX[name]["entries"] is not None:
        meta_md += f", {INDEX[name]['entries']} entries"
    meta_md += ")\n"

with open(os.path.join(API_DIR, "index.md"), "w") as f:
    f.write(f"---\nlayout: page\ntitle: API\npermalink: /api/\n---\n\n{meta_md}")

print(f"API endpoint pages written: {len(INDEX)} files")
