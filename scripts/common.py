"""Shared constants and utilities for milestone and game detection."""

import json
import os

DATA_DIR = "_data"

# Powers of three: ternary counting base (as a set for easy union)
P3 = {3**i for i in range(13)}

# Powers of two: binary counting base (as a set for easy union)
P2 = {2**i for i in range(21)}

# Round numbers (as a set for easy union)
RND = {1, 10} | {10**x * y for x in range(5) for y in (25, 50, 75, 100)}

# Combined threshold set for ALL milestone types (all scales)
ALL_THRESH = sorted(P3 | P2 | RND)

# Minimums for stats that grow to large values: sub-50 views or sub-5 hours
# milestones are noise (reached on day one), not achievements
VIEWS_MIN = 50
HOURS_MIN = 5
GAME_VIEWS_THRESH = [m for m in ALL_THRESH if m >= VIEWS_MIN]
GAME_HOURS_THRESH = [m for m in ALL_THRESH if m >= HOURS_MIN]

# Valid game names — canonical names from game_links.yml, used to distinguish
# actual games from content series (Railway Exhibition Vlogs, Infrastructure Programming, etc.)
_VALID_GAMES_PATH = os.path.join(DATA_DIR, "game_links.yml")
VALID_GAMES = set()
try:
    import yaml

    if os.path.exists(_VALID_GAMES_PATH):
        with open(_VALID_GAMES_PATH) as f:
            _gl = yaml.safe_load(f) or {}
        for canonical, _entry in _gl.items():
            VALID_GAMES.add(canonical)
        ALIAS_MAP = {}
        for canonical, entry in _gl.items():
            if isinstance(entry, dict):
                for alias in entry.get("aliases", []):
                    ALIAS_MAP[alias] = canonical
                    VALID_GAMES.add(alias)
except Exception as e:
    print(f"Warning: could not load {_VALID_GAMES_PATH}: {e}", file=__import__("sys").stderr)
    ALIAS_MAP = {}

# per-type threshold lists for game milestones — ALL use the full combined set
GAME_THRESHOLDS = {
    "ep": ALL_THRESH,
    "views": GAME_VIEWS_THRESH,
    "hours": GAME_HOURS_THRESH,
    "return": ALL_THRESH,
}

# Maps sequel game names to their base game for shared milestone messages
SEQUEL_BASE = {
    "Transport Fever 3": "Transport Fever 2",
}


def _fmt(m, b):
    return f"{m:,}: {b}" if b else f"{m:,} units!"


FMT = _fmt

P3_MSG = {
    1: "The unitary state.",
    3: "Three-body problem solved.",
    9: "Nonary game complete.",
    27: "Cube it!",
    81: "Trit-trit-trit-trit!",
    243: "Fifth power unlocked.",
    729: "729! A full Setun tryte.",
    2187: "Lucky sevens! The 7th power achieved.",
    6561: "A perfectly balanced octotrit.",
    19683: "19,683! A historic Setun half-word.",
    59049: "Decitrit! Tenfold power!",
    177147: "Welcome to the ternary galaxy!",
    531441: "531,441! The mighty dozenal trit.",
}
P2_MSG = {
    2: "Two. The foundation of binary.",
    4: "Four. A perfect nybble.",
    8: "Eight! A full byte.",
    16: "Sixteen. The hexadecimal base.",
    32: "32. Entering 32-bit territory.",
    64: "64. Stepping up to 64-bit.",
    128: "128. Crossing into three digits.",
    256: "256! A full 8-bit range.",
    512: "512. Closing in on 1K.",
    1024: "1K! A true binary kilobyte.",
    2048: "2K. Doubling the kilobyte.",
    4096: "4K! Hitting the page boundary.",
    8192: "8K. Scaling up the memory.",
    16384: "16K. A solid block of data.",
    32768: "32K. Pushing past the 15-bit mark.",
    65536: "64K! Classic 16-bit address space.",
    131072: "128K. Stepping into expanded memory.",
    262144: "256K. Gaining serious capacity.",
    524288: "512K. Halfway to a megabyte.",
    1048576: "1M! Megabyte territory achieved.",
}
RND_MSG = {
    10: "Double digits achieved.",
    25: "Gaining momentum at 25.",
    50: "Hitting the 50 mark.",
    75: "Cruising past 75.",
    100: "One hundred strong! Triple digits.",
    250: "A solid 250 on the board.",
    500: "Five hundred and climbing.",
    750: "Next major stop: one thousand.",
    1000: "One thousand! A major milestone.",
    2500: "Crossing the 2,500 threshold.",
    5000: "Five thousand! The community is growing.",
    7500: "Moving swiftly past 7,500.",
    10000: "Ten thousand! Welcome to five digits.",
    25000: "Twenty-five thousand and counting.",
    50000: "Fifty thousand! An impressive feat.",
    75000: "Seventy-five thousand strong.",
    100000: "One hundred thousand! Six digits achieved.",
    250000: "A massive 250,000.",
    500000: "Five hundred thousand! A monumental achievement.",
    750000: "750,000 and pushing forward.",
    1000000: "One million! A truly historic milestone.",
}

MILESTONE_SPECS = [
    ("subs", P3, P3_MSG, FMT),
    ("subs", P2, P2_MSG, FMT),
    ("subs", RND, RND_MSG, FMT),
    ("views", P3, P3_MSG, FMT),
    ("views", P2, P2_MSG, FMT),
    ("views", RND, RND_MSG, FMT),
    ("videos", P3, P3_MSG, FMT),
    ("videos", P2, P2_MSG, FMT),
    ("videos", RND, RND_MSG, FMT),
    ("likes", P3, P3_MSG, FMT),
    ("likes", P2, P2_MSG, FMT),
    ("likes", RND, RND_MSG, FMT),
    ("comments", P3, P3_MSG, FMT),
    ("comments", P2, P2_MSG, FMT),
    ("comments", RND, RND_MSG, FMT),
]

HOURS_THRESH = GAME_HOURS_THRESH
GAME_EP_THRESH = ALL_THRESH
VIDEO_FIRST_THRESH = ALL_THRESH
HIATUS_DAYS_THRESH = 60
ANNIVERSARY_THRESH = [m for m in ALL_THRESH if m <= 100]
AGE_DAYS_THRESH = [m for m in ALL_THRESH if m >= 30]


def read_json(filename):
    p = os.path.join(DATA_DIR, filename)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)
