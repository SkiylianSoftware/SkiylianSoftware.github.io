import json
import os
import sys
from datetime import datetime, timezone

import requests

FW_CLIENT_ID = os.environ.get("FW_CLIENT_ID", "")
FW_CLIENT_SECRET = os.environ.get("FW_CLIENT_SECRET", "")
DATA_DIR = "_data"

AUTH_URL = "https://api.fourthwall.com/auth/oauth/token"
API_BASE = "https://api.fourthwall.com/api"


def get_token(client_id, client_secret):
    resp = requests.post(
        AUTH_URL,
        json={"client_id": client_id, "client_secret": client_secret},
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"Fourthwall auth error {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
        return None
    data = resp.json()
    return data.get("access_token")


def api_get(path, token):
    url = f"{API_BASE}/{path}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"Fourthwall API error {resp.status_code} for {path}: {resp.text[:200]}", file=sys.stderr)
        return None
    return resp.json()


def main():
    if not FW_CLIENT_ID or not FW_CLIENT_SECRET:
        print("No FW_CLIENT_ID or FW_CLIENT_SECRET set, skipping Fourthwall data", file=sys.stderr)
        return
    token = get_token(FW_CLIENT_ID, FW_CLIENT_SECRET)
    if not token:
        print("Failed to get Fourthwall access token", file=sys.stderr)
        return
    # Try various API endpoints to gather store stats
    data = {"fetched_at": datetime.now(timezone.utc).isoformat()}
    stats = api_get("merchant/v1/stats", token)
    if stats:
        d = stats.get("data", stats)
        data["stats"] = {
            "total_orders": d.get("totalOrders", d.get("orders", 0)),
            "total_revenue": d.get("totalRevenue", d.get("revenue", 0)),
            "currency": d.get("currency", d.get("defaultCurrency", "USD")),
        }
        print(f"  Orders: {data['stats']['total_orders']}, Revenue: {data['stats']['total_revenue']}")
    else:
        print("  No stats endpoint available, trying products...")
        products = api_get("merchant/v1/products", token)
        if products:
            items = products.get("data", products.get("items", []))
            if isinstance(items, list):
                data["product_count"] = len(items)
                print(f"  Products: {len(items)}")
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "fourthwall.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written {path}")


if __name__ == "__main__":
    main()
