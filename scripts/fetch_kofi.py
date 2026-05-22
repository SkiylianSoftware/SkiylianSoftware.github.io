import json
import os
import sys
from datetime import datetime, timezone

import requests

KOFI_API_KEY = os.environ.get("KOFI_API_KEY", "")
KOFI_VERIFICATION_TOKEN = os.environ.get("KOFI_VERIFICATION_TOKEN", "")
KOFI_USERNAME = "skiylia"
DATA_DIR = "_data"
API_BASE = "https://api.ko-fi.com/api/v1"


def kofi_get(endpoint, api_key):
    url = f"{API_BASE}/{endpoint}"
    headers = {"x-api-key": api_key}
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"Ko-fi API error {resp.status_code} for {endpoint}: {resp.text[:300]}", file=sys.stderr)
        return None
    return resp.json()


def fetch_goal(api_key):
    data = kofi_get("goal", api_key)
    if not data:
        return None
    goal = data.get("data", data.get("goal", {}))
    if not goal:
        return None
    return {
        "title": goal.get("goalTitle") or goal.get("title", "Monthly Goal"),
        "current": float(goal.get("totalRaised") or goal.get("current", 0)),
        "target": float(goal.get("goalAmount") or goal.get("target", 0)),
        "active": bool(goal.get("active") or goal.get("active", False)),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def fetch_patrons(api_key):
    data = kofi_get("patrons", api_key)
    if not data:
        return None
    items = data.get("data", data.get("patrons", []))
    if not items:
        return {"count": 0, "total_monthly": 0.0, "fetched_at": datetime.now(timezone.utc).isoformat()}
    total = sum(float(p.get("amount", 0)) for p in items)
    return {
        "count": len(items),
        "total_monthly": total,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    if not KOFI_API_KEY:
        print("No KOFI_API_KEY set, skipping Ko-fi data", file=sys.stderr)
        return
    goal = fetch_goal(KOFI_API_KEY)
    if goal:
        pct = (goal["current"] / goal["target"] * 100) if goal["target"] > 0 else 0
        print(f"  Goal: {goal['title']} - {goal['current']:.2f}/{goal['target']:.2f} ({pct:.0f}%)")
    patrons = fetch_patrons(KOFI_API_KEY)
    if patrons:
        print(f"  Patrons: {patrons['count']} supporters ({patrons['total_monthly']:.2f}/month)")
    data = {
        "username": KOFI_USERNAME,
        "goal": goal,
        "patrons": patrons,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "kofi.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written {path}")


if __name__ == "__main__":
    main()
