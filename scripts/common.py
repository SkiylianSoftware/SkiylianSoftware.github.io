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

# Keep GAME_EP_THRESH as an alias for backwards compatibility
GAME_EP_THRESH = ALL_THRESH

# Default milestone message templates for games (used by fetch_youtube.py legacy detector)
GAME_DEFAULT = {
    "ep": "{{m}} episodes in {game}!",
    "views": "{{count}} views across {game}!",
    "hours": "{{hours}} hours in {game}!",
    "return": "Back to {game} after {{days}} days!",
}

# per-type threshold lists for game milestones — ALL use the full combined set
GAME_THRESHOLDS = {
    "ep": ALL_THRESH,
    "views": ALL_THRESH,
    "hours": ALL_THRESH,
    "return": ALL_THRESH,
}

# Maps sequel game names to their base game for shared milestone messages
SEQUEL_BASE = {
    "Transport Fever 2": "Transport Fever",
    "Transport Fever 3": "Transport Fever",
}

# Per-game milestone message overrides — every threshold up to 100 has a custom message.
# Falls back to GAME_DEFAULT for any missing key, and SEQUEL_BASE for missing sequels.
GAME_OVERRIDES = {
    "Kerbal Space Program": {
        "ep": {
            1: "First launch at KSC!",
            2: "Orbit achieved!",
            3: "Munar flyby complete!",
            4: "Mun landing!",
            8: "Minmus landing!",
            9: "Duna transfer window!",
            10: "Duna landing!",
            16: "Interplanetary fleet assembled!",
            25: "Jool system arrival!",
            27: "Jool system fleet deployed!",
            32: "Eeloo reached!",
            50: "Kerbals across the solar system!",
            64: "Space station network established!",
            81: "Grand tour completed!",
            100: "Century of launches!",
        }
    },
    "Factorio": {
        "ep": {
            1: "First burner miner placed!",
            2: "Steam power online!",
            3: "Red science automated!",
            4: "Green science automated!",
            8: "Oil processing started!",
            9: "Blue science online!",
            10: "Logistic bots deployed!",
            16: "Rail network built!",
            25: "Logistic network active!",
            27: "Rocket silo constructed!",
            32: "Space science packed!",
            50: "Mega base expanding!",
            64: "Quad-blue belt main bus!",
            81: "Mega base operational!",
            100: "Factory must grow!",
        }
    },
    "Minecraft": {
        "ep": {
            1: "Wooden tools crafted!",
            2: "Coal mined!",
            3: "Nether portal activated!",
            4: "Iron armor equipped!",
            8: "Enchanting table built!",
            9: "Stronghold located!",
            10: "Brewing stand made!",
            16: "Netherite tools forged!",
            25: "Beacon assembled!",
            27: "Ender Dragon defeated!",
            32: "Elytra acquired!",
            50: "Ocean monument raided!",
            64: "Woodland mansion found!",
            81: "Full beacon pyramid!",
            100: "Wither defeated!",
        }
    },
    "Transport Fever": {
        "ep": {
            1: "First bus route!",
            2: "Cargo line opened!",
            3: "Three lines running!",
            4: "Train station built!",
            8: "Tram network started!",
            9: "Train network growing!",
            10: "Truck routes delivering!",
            16: "Airport constructed!",
            25: "High-speed rail built!",
            27: "Continent-spanning network!",
            32: "Ship lines launched!",
            50: "Metropolitan network!",
            64: "National rail grid!",
            81: "Transcontinental empire!",
            100: "Logistics tycoon!",
        }
    },
    "Mars First Logistics": {
        "ep": {
            1: "First contract signed!",
            2: "Wheels attached!",
            3: "Rover chassis assembled!",
            4: "Solar panels tested!",
            8: "Cargo lifted!",
            9: "Rocket launched!",
            10: "Second depot built!",
            16: "Hydraulic arm fitted!",
            25: "Third depot operational!",
            27: "Three depots connected!",
            32: "Wind turbine added!",
            50: "Across the dunes!",
            64: "Full workshop upgraded!",
            81: "Martian rover fleet!",
            100: "Logistics mastered!",
        }
    },
    "Station Flow": {
        "ep": {
            1: "First platform open!",
            2: "Ticket machine installed!",
            3: "Queue managed!",
            4: "Platform signage up!",
            8: "Second concourse built!",
            9: "Escalators installed!",
            10: "Express service started!",
            16: "Third platform added!",
            25: "Underground passage dug!",
            27: "Expansion complete!",
            32: "Grand concourse built!",
            50: "Regional hub!",
            64: "Intercity connections!",
            81: "Metroplex achieved!",
            100: "Station perfected!",
        }
    },
}


def _fmt(m, b):
    return f"{m:,}: {b}" if b else f"{m:,} units!"


FMT = _fmt

P3_MSG = {
    1: "The unitary state",
    3: "Three-body problem solved",
    9: "Nonary game complete",
    27: "Cube it!",
    81: "Trit-trit-trit!",
    243: "3^5 - Fifth power unlocked",
    729: "3^6 - One gross in balanced ternary",
    2187: "3^7 - Lucky sevens",
    6561: "3^8 - Octotrit",
    19683: "3^9 - Padovan sequence spotted",
    59049: "3^10 - Decitrit! Tenfold power!",
    177147: "3^11 - Ternary galaxy!",
    531441: "3^12 - Dozenal trit!",
}
P2_MSG = {
    2: "A pair!",
    4: "Four! Quadbit!",
    8: "Byte!",
    16: "Half-word!",
    32: "Word!",
    64: "Double-word!",
    128: "Kilobit!",
    256: "Byte plural!",
    512: "Half a K!",
    1024: "1K! A true kilobyte!",
    2048: "2K!",
    4096: "4K! Page boundary!",
    8192: "8K!",
    16384: "16K!",
    32768: "Half of 64K!",
    65536: "64K! Full address space!",
    131072: "128K! Expanded memory!",
    262144: "256K! High memory area!",
    524288: "512K! Extended memory!",
    1048576: "1M! Megabyte territory!",
}
RND_MSG = {
    1: "Just getting started",
    10: "First double digits!",
    25: "Quarter of a century!",
    50: "Halfway to 100!",
    75: "Three-quarters and thriving!",
    100: "Triple digits!",
    250: "Quarter thousand!",
    500: "Half a thousand!",
    750: "Three-quarters of a grand!",
    1000: "The big 1 Thousand!",
    2500: "Two and a half grand!",
    5000: "5 Thousand strong!",
    7500: "Seven and a half thousand!",
    10000: "10 Thousand! Unreal!",
    25000: "25 Thousand! Quarter of a hundred thousand!",
    50000: "50 Thousand! Halfway to 100 Thousand!",
    75000: "75 Thousand! Three-quarters there!",
    100000: "100 Thousand!!! Thank you!",
    500000: "Half a million!",
    1000000: "1 Million! Unbelievable!",
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

HOURS_THRESH = ALL_THRESH
VIDEO_FIRST_THRESH = [m for m in ALL_THRESH if m >= 100]
HIATUS_DAYS_THRESH = 60


def read_json(filename):
    p = os.path.join(DATA_DIR, filename)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)
