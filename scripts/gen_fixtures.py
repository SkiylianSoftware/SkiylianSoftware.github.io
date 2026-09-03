"""
Generate minimal _data fixtures for local development without API keys.
Creates enough data that Jekyll builds without errors.
Designed for `make dev` workflow.
"""

import json
import os

DATA_DIR = "_data"
os.makedirs(DATA_DIR, exist_ok=True)

fixtures = {
    "site_meta.json": {
        "subscriber_count": 61,
        "view_count": 8879,
        "video_count": 62,
        "banner_url": "",
        "description": (
            "The official website for Skye / skiylia. Watch videos, "
            "catch livestreams, and explore the archive of content "
            "from YouTube, Twitch, and more."
        ),
    },
    "youtube_main.json": {
        "videos": [
            {
                "video_id": "BuDRQdp5vFY",
                "title": "Crashes and Coal | Skiylian Transport #17 | Transport Fever 2",
                "published": "2026-01-11T11:00:19+00:00",
                "thumbnail": "https://i.ytimg.com/vi/BuDRQdp5vFY/hqdefault.jpg",
                "description": "A sample video description for local development.",
                "duration_seconds": 3144,
                "view_count": 3,
                "series": {
                    "series_name": "Skiylian Transport",
                    "game": "Transport Fever 2",
                    "episode_number": 17,
                },
            }
        ],
        "series_recency": {"Skiylian Transport": {"status": "current", "episodes": 17}},
    },
    "youtube_vods.json": {"videos": []},
    "twitch_vods.json": {"videos": []},
    "twitch_stats.json": {
        "follower_count": 0,
        "broadcaster_type": "",
        "view_count": 0,
        "created_at": "2024-01-01T00:00:00Z",
    },
    "twitch_schedule.json": {"segments": []},
    "twitch.json": {"platform": None},
    "github.json": {
        "username": "SkiylianSoftware",
        "public_repos": 5,
        "followers": 0,
        "total_stars": 0,
        "total_forks": 0,
        "top_repos": [],
    },
    "fourthwall.json": {"total_orders": 0, "products": []},
    "kofi.json": {},
    "livestream.json": {"platform": None},
    "history.json": [],
    "milestones.json": {"current": [], "reached": {}},
    "video_history.json": {},
    "games.json": {
        "games": {},
        "non_game": {"total": {"episode_count": 0}, "categories": {}},
    },
    "playlists.json": {"playlists": []},
}

for name, data in fixtures.items():
    path = os.path.join(DATA_DIR, name)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  {path}")

print("Fixtures written. Run `bundle exec jekyll serve` now.")
