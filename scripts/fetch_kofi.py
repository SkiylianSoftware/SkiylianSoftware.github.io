import json
import os
import sys
from datetime import datetime, timezone

KOFI_USERNAME = "skiylia"
DATA_DIR = "_data"


def main():
    print("Ko-fi doesn't provide a REST API -- data is only available via webhooks.")
    print("  Using embeddable widgets on the support page instead of API data.")
    data = {
        "username": KOFI_USERNAME,
        "note": "Ko-fi uses webhooks only. Embed widgets are used on the support page.",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "kofi.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written {path}")


if __name__ == "__main__":
    main()
