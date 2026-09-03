"""
Validate _schema_version in generated _data files.
Fails with non-zero exit if any expected file is missing or has a wrong version.
"""

import json
import os
import sys

DATA_DIR = "_data"

EXPECTED = {
    "youtube_main.json": 1,
    "youtube_vods.json": 1,
    "twitch_vods.json": 1,
    "games.json": 1,
    "site_meta.json": 1,
    "history.json": 1,
    "milestones.json": 1,
    "playlists.json": 1,
    "twitch_stats.json": 1,
}

problems = 0
for fname, expected in EXPECTED.items():
    path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(path):
        print(f"SKIP {fname}: not present")
        continue
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"FAIL {fname}: unreadable - {e}")
        problems += 1
        continue
    if isinstance(data, list):
        actual = data[0].get("_schema_version", None) if data else None
        if actual is None:
            print(f"WARN {fname}: no _schema_version key (pre-migration file)")
            continue
        if actual != expected:
            print(f"FAIL {fname}: expected v{expected}, got v{actual}")
            problems += 1
        else:
            print(f"OK   {fname}: v{actual} ({len(data)} entries)")
        continue
    actual = data.get("_schema_version", None)
    if actual is None:
        print(f"WARN {fname}: no _schema_version key (pre-migration file)")
        continue
    if actual != expected:
        print(f"FAIL {fname}: expected v{expected}, got v{actual}")
        problems += 1
    else:
        print(f"OK   {fname}: v{actual}")

if problems:
    print(f"\n{problems} schema violation(s) found - bump version in the generating script and CI cache key")
    sys.exit(1)
print("\nAll schema versions OK")
