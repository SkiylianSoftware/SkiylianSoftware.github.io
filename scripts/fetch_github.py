import json
import os
import sys
from datetime import datetime, timezone

import requests

GITHUB_USERNAME = "SkiylianSoftware"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
DATA_DIR = "_data"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


def save(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written {path}")


def main():
    print("Fetching GitHub stats...")
    user_url = f"https://api.github.com/users/{GITHUB_USERNAME}"
    resp = requests.get(user_url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        print(f"GitHub user fetch failed: {resp.status_code}", file=sys.stderr)
        return
    user = resp.json()

    repos_url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&sort=updated&direction=desc"
    resp = requests.get(repos_url, headers=HEADERS, timeout=30)
    repos = resp.json() if resp.status_code == 200 else []
    if isinstance(repos, dict):
        print(f"GitHub repos fetch failed: {repos.get('message', '')}", file=sys.stderr)
        repos = []

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    forks = sum(r.get("forks_count", 0) for r in repos)
    top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:5]

    data = {
        "username": GITHUB_USERNAME,
        "public_repos": user.get("public_repos", len(repos)),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "total_stars": total_stars,
        "total_forks": forks,
        "created_at": user.get("created_at", ""),
        "avatar_url": user.get("avatar_url", ""),
        "top_repos": [
            {
                "name": r["name"],
                "url": r["html_url"],
                "stars": r.get("stargazers_count", 0),
                "forks": r.get("forks_count", 0),
                "language": r.get("language", ""),
                "description": r.get("description", "")[:200] if r.get("description") else "",
                "updated_at": r.get("updated_at", ""),
            }
            for r in top_repos
        ],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    save("github.json", data)

    for r in repos:
        print(f"  {r['name']}: {r.get('stargazers_count', 0)} stars")


if __name__ == "__main__":
    main()