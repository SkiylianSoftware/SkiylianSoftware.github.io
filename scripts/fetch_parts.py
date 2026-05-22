import json
import os
import re
import sys
from datetime import datetime, timezone

import requests

PCPARTPICKER_BASE = "https://uk.pcpartpicker.com"
DATA_DIR = "_data"

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def extract_between(text, start, end):
    idx = text.find(start)
    if idx == -1:
        return ""
    idx += len(start)
    end_idx = text.find(end, idx)
    if end_idx == -1:
        return text[idx:]
    return text[idx:end_idx]


def extract_tag_content(text, tag, attrs=None):
    """Extract content of first matching HTML tag."""
    tag_start = f"<{tag}"
    if attrs:
        for key, val in attrs.items():
            tag_start += f' {key}="{val}"'
    tag_start += ">"

    idx = text.find(tag_start)
    if idx == -1:
        return ""
    idx += len(tag_start)
    end_tag = f"</{tag}>"
    end_idx = text.find(end_tag, idx)
    if end_idx == -1:
        return text[idx:]
    return text[idx:end_idx]


CORE_COMPONENTS = [
    "CPU", "Video Card", "Memory", "Motherboard",
    "CPU Cooler", "Storage", "Power Supply", "Case",
    "External Storage", "UPS",
]


def shorten_name(part):
    name = part["name"]
    match part["component"]:
        case "CPU":
            return re.sub(r"\s+\d[\d.]*\s*GHz.*", "", name).strip()
        case "CPU Cooler":
            m = re.match(r"^([^0-9]+(?:\s+\d+)??(?:mm)?)", name)
            return m.group(1).strip() if m else name
        case "Motherboard":
            m = re.match(r"^([^(]+?)\s*(?:ATX|Micro ATX|Mini ITX)", name)
            return m.group(1).strip() if m else name
        case "Memory":
            cap_match = re.search(r"(\d+)\s*GB", name)
            speed_match = re.search(r"DDR4-\d+", name)
            speed = speed_match.group(0) if speed_match else "DDR4"
            return f"{cap_match.group(1)} GB {speed}" if cap_match else name
        case "Storage":
            return re.sub(r"\s*\([^)]*\)", "", name).strip()
        case "Video Card":
            return re.sub(r"\s+\d+\s*GB.*", "", name).strip()
        case "Case":
            name = re.sub(r"\s*ATX\s+(Mid|Full)\s+Tower\s*", " ", name).strip()
            return re.sub(r"\s+Case$", "", name).strip()
        case "Power Supply":
            brand = re.match(r"^([A-Za-z][A-Za-z\s-]+)", name)
            wattage = re.search(r"(\d+)\s*W", name)
            brand_name = brand.group(1).strip() if brand else ""
            watt = wattage.group(1) if wattage else "?"
            return f"{brand_name} {watt}W" if brand_name else f"{watt}W PSU"
        case "External Storage":
            return re.sub(r"\s*\([^)]*\)", "", name).strip()
        case "UPS":
            return name
    return name


def build_display(parts):
    filtered = [p for p in parts if p["component"] in CORE_COMPONENTS]

    merged = {}
    for p in filtered:
        comp = p["component"]
        if comp in ("Memory", "Storage"):
            if comp not in merged:
                merged[comp] = []
            merged[comp].append(p)
        else:
            merged[comp] = {"component": comp, "name": shorten_name(p), "url": p["url"]}

    result = []
    for comp in CORE_COMPONENTS:
        if comp not in merged:
            continue
        if comp == "Memory":
            total_gb = 0
            for mp in merged[comp]:
                cap_match = re.search(r"(\d+)\s*GB", mp["name"])
                if cap_match:
                    total_gb += int(cap_match.group(1))
            result.append({"component": "Memory", "name": f"{total_gb} GB DDR4", "url": None})
        elif comp == "Storage":
            parts_list = []
            for sp in merged[comp]:
                cap_match = re.search(r"(\d+)\s*(?:GB|TB)", sp["name"])
                type_match = re.search(r"(SATA|NVMe|SSD|HDD)", sp["name"], re.IGNORECASE)
                cap = cap_match.group(0) if cap_match else "?"
                stype = type_match.group(1).upper() if type_match else "SSD"
                parts_list.append(f"{cap} {stype}")
            result.append({"component": "Storage", "name": " + ".join(parts_list), "url": None})
        else:
            result.append(merged[comp])

    return result


def save(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written {path}")


def read_list_id():
    env_id = os.environ.get("PCPARTPICKER_LIST_ID")
    if env_id:
        return env_id
    try:
        with open("_config.yml") as f:
            for line in f:
                if line.startswith("pcpartpicker_list_id:"):
                    return line.split(":", 1)[1].strip()
    except FileNotFoundError:
        pass
    return "phfd9K"


def main():
    list_id = read_list_id()
    print(f"Fetching PCPartPicker list {list_id}...")

    url = f"{PCPARTPICKER_BASE}/list/{list_id}"
    resp = requests.get(url, headers=BROWSER_HEADERS, timeout=30)
    if resp.status_code != 200:
        print(f"Failed to fetch list: HTTP {resp.status_code}", file=sys.stderr)
        sys.exit(1)

    html = resp.text

    parts = []

    # Split the page into product rows
    product_rows = []
    search_from = 0
    while True:
        row_start = html.find('<tr class="tr__product">', search_from)
        if row_start == -1:
            break
        row_end = html.find("</tr>", row_start)
        if row_end == -1:
            break
        row_html = html[row_start : row_end + 6]
        product_rows.append(row_html)
        search_from = row_end + 6

    for row in product_rows:
        # Component category
        comp = ""
        comp_match_start = row.find('<td class="td__component')
        if comp_match_start != -1:
            comp_cell_end = row.find("</td>", comp_match_start)
            comp_cell = row[comp_match_start : comp_cell_end + 5]
            a_start = comp_cell.find('">', comp_cell.find("<a "))
            if a_start != -1:
                a_start += 2
                a_end = comp_cell.find("</a>", a_start)
                if a_end != -1:
                    comp = comp_cell[a_start:a_end].strip()

        # Part name and URL
        name = ""
        part_url = ""
        name_td = extract_between(row, '<td class="td__name td__name-2025">', "</td>")
        if name_td:
            a_tag_start = name_td.find('<a href="')
            if a_tag_start != -1:
                href_start = a_tag_start + 9
                href_end = name_td.find('"', href_start)
                href = name_td[href_start:href_end] if href_end != -1 else ""

                content_start = name_td.find(">", href_end) + 1 if href_end != -1 else -1
                content_end = name_td.find("</a>") if content_start != -1 else -1

                if content_start != -1 and content_end != -1:
                    name = name_td[content_start:content_end].strip()
                if href:
                    part_url = PCPARTPICKER_BASE + href

        # Price
        price = None
        price = None
        if 'td__price--none"' not in row[: row.find("</tr>")]:
            price_cell = extract_between(
                row, '<td class="td__price td__price-2025">', "</td>"
            )
            if price_cell:
                price_match = re.search(r"£[\d,]+\.?\d*", price_cell)
                if price_match:
                    price = price_match.group(0)

        if comp or name:
            parts.append({
                "component": comp,
                "name": name,
                "url": part_url,
                "price": price,
            })

    # Extract totals from tr.tr__total rows
    total_base = None
    total_shipping = None
    total_grand = None

    total_rows = []
    search_from = 0
    while True:
        row_start = html.find('<tr class="tr__total ', search_from)
        if row_start == -1:
            break
        row_end = html.find("</tr>", row_start)
        if row_end == -1:
            break
        total_rows.append(html[row_start : row_end + 6])
        search_from = row_end + 6

    for row in total_rows:
        label = extract_between(row, '<td class="td__label"', "</td>")
        label = extract_between(label, ">", "<").strip().rstrip(":")

        price_td = extract_between(row, '<td class="td__price td__price-2025">', "</td>")
        price_val = price_td.strip() if price_td else None

        if label == "Base Total":
            total_base = price_val
        elif label == "Shipping":
            total_shipping = price_val
        elif label == "Total":
            total_grand = price_val

    display = build_display(parts)

    data = {
        "list_id": list_id,
        "list_url": url,
        "parts": parts,
        "display": display,
        "total_base": total_base,
        "total_shipping": total_shipping,
        "total_grand": total_grand,
        "part_count": len(parts),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    save("pc_parts.json", data)

    for part in parts:
        price_str = part["price"] if part["price"] else "N/A"
        print(f"  {part['component']}: {part['name']} ({price_str})")
    print(f"  Base: {total_base} | Shipping: {total_shipping} | Grand: {total_grand}")
    print(f"  ({len(parts)} parts total)")
    print(f"  Display: {len(display)} items")


if __name__ == "__main__":
    main()
