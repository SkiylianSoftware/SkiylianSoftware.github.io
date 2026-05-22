import json
import os
import sys
from base64 import b64encode
from datetime import datetime, timezone

import requests

FW_USERNAME = os.environ.get("FW_USERNAME", "")
FW_PASSWORD = os.environ.get("FW_PASSWORD", "")
DATA_DIR = "_data"
API_BASE = "https://api.fourthwall.com/open-api/v1.0"


def basic_auth_header(user, pw):
    token = b64encode(f"{user}:{pw}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def api_get(path, headers):
    url = f"{API_BASE}/{path}"
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code == 401:
        print(f"Fourthwall auth rejected for {path} -- check credentials", file=sys.stderr)
        return None
    if resp.status_code != 200:
        print(f"Fourthwall API error {resp.status_code} for {path}: {resp.text[:200]}", file=sys.stderr)
        return None
    return resp.json()


def main():
    if not FW_USERNAME or not FW_PASSWORD:
        print("No FW_USERNAME or FW_PASSWORD set, skipping Fourthwall data", file=sys.stderr)
        return
    headers = basic_auth_header(FW_USERNAME, FW_PASSWORD)
    data = {"fetched_at": datetime.now(timezone.utc).isoformat()}

    shop = api_get("shops/current", headers)
    if shop:
        data["shop"] = {
            "name": shop.get("name", ""),
            "domain": shop.get("publicDomain", ""),
        }
        print(f"  Shop: {data['shop']['name']} ({data['shop']['domain']})")

    orders = api_get("orders?limit=1", headers)
    if orders:
        items = orders.get("data", orders.get("items", []))
        total = orders.get("total", orders.get("totalCount", len(items)))
        data["total_orders"] = total
        print(f"  Total orders: {total}")
    else:
        print("  No orders endpoint available")

    products = api_get("products?limit=5", headers)
    if products:
        raw = products.get("data", products.get("items", []))
        top = []
        for p in raw[:5]:
            name = p.get("name", "")
            price = p.get("price", p.get("amount", None))
            currency = p.get("currency", p.get("defaultCurrency", ""))
            url = p.get("url", p.get("publicUrl", ""))
            if name:
                entry = {"name": name}
                if price:
                    entry["price"] = float(price)
                    entry["currency"] = currency
                if url:
                    entry["url"] = url
                top.append(entry)
        data["products"] = top
        print(f"  Products: {len(top)}")
    else:
        print("  No products endpoint available, will fall back to generic text")

    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "fourthwall.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written {path}")


if __name__ == "__main__":
    main()
