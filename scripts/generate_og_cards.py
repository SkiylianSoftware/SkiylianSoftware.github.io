"""
Generate branded Open Graph / social share cards for each video.

Composites the video thumbnail (16:9) with the title and a "watch on
skiylia.dev" footer onto a 1280x720 card so shared post links have a
proper visual instead of a bare link card.

Requires Pillow. Fonts: uses DejaVu (available on ubuntu-latest runners).

Cards are written to assets/img/og/<video_id>.jpg, which generate_posts.py
references as the post's og:image.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

DATA_DIR = "_data"
OUT_DIR = os.path.join("assets", "img", "og")
CARD_W, CARD_H = 1280, 720
FOOTER = "watch on skiylia.dev"
TITLE_WRAP = 44  # approx chars per line at this size
TITLE_LINES = 3
TITLE_TOP = 40
TITLE_LEFT = 48
TITLE_RIGHT = 76
MAXTITLE = TITLE_RIGHT
FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
]


def _font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def _wrap_title(text, font, max_width):
    words = text.split()
    if not words:
        return [""]
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        wpx = font.getlength(trial)
        if wpx <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
            # single word longer than the box: hard-truncate
            while font.getlength(cur) > max_width and cur:
                cur = cur[:-1]
    if cur:
        lines.append(cur)
    return lines


def _draw_gradient(draw, w, h, top, bottom):
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def make_card(video):
    vid = video.get("video_id", "")
    if not vid:
        return False
    thumb = video.get("thumbnail", "")
    title = video.get("title", "")
    if not thumb:
        return False

    # Base canvas: dark brand-ish background with a subtle gradient
    img = Image.new("RGB", (CARD_W, CARD_H), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    _draw_gradient(draw, CARD_W, CARD_H, (10, 10, 28), (24, 18, 48))

    # Lay the thumbnail over the top two-thirds (like a video preview)
    try:
        th = Image.open(__fetch(thumb))
        th = th.convert("RGB")
        target_w = CARD_W
        target_h = int(CARD_H * 0.62)
        scale = max(target_w / th.width, target_h / th.height)
        nw, nh = int(th.width * scale), int(th.height * scale)
        th = th.resize((nw, nh), Image.LANCZOS)
        left = (nw - target_w) // 2
        top = (nh - target_h) // 2
        img.paste(th.crop((left, top, left + target_w, top + target_h)), (0, 0))
    except Exception:
        pass  # no thumbnail: gradient background stands in

    draw = ImageDraw.Draw(img)

    # Slight bottom scrim so the overlay text reads
    for y in range(int(CARD_H * 0.5), CARD_H):
        draw.line([(0, y), (CARD_W, y)], fill=(8, 8, 16, 240))

    # Title block lower-left
    f_title = _font(44, bold=True)
    f_footer = _font(24, bold=False)

    lines = _wrap_title(title, f_title, CARD_W - TITLE_LEFT - TITLE_RIGHT)
    lines = lines[:TITLE_LINES]
    y = CARD_H - 200
    for ln in lines:
        draw.text((TITLE_LEFT, y), ln, fill=(255, 255, 255), font=f_title)
        y += 52

    # Accent underline + footer
    draw.rectangle(
        [TITLE_LEFT, y + 4, TITLE_LEFT + 180, y + 12],
        fill=(45, 212, 191),
    )
    draw.text((TITLE_LEFT, CARD_H - 56), FOOTER, fill=(200, 216, 230), font=f_footer)

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"{vid}.jpg")
    img.save(out, "JPEG", quality=88)
    return True


def __fetch(url):
    import requests

    return requests.get(url, timeout=15).content


def main():
    data = read_json("youtube_main.json") or {}
    videos = data.get("videos") or []
    if not videos:
        print("No videos to card-ify")
        return
    made = 0
    for v in videos:
        if make_card(v):
            made += 1
    print(f"Generated {made} OG cards in {OUT_DIR}/")
    stale_old(videos)


def read_json(name):
    p = os.path.join(DATA_DIR, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def stale_old(videos):
    """Remove cards for videos that no longer exist."""
    have = {v.get("video_id") for v in videos if v.get("video_id")}
    if not os.path.isdir(OUT_DIR):
        return
    for f in os.listdir(OUT_DIR):
        if f.endswith(".jpg") and f[:-4] not in have:
            os.remove(os.path.join(OUT_DIR, f))
            print(f"  removed stale {f}")


if __name__ == "__main__":
    main()
