#!/usr/bin/env python3
"""Feature the newest blog post on the homepage.

Reads every post card in blog.html, picks the one with the most recent
date (ties go to the card listed first), and rewrites the block between
the LATEST-POST markers in index.html.

Runs automatically in .github/workflows/pages.yml before every deploy,
so publishing a new post (blog/<slug>.html plus its card in blog.html)
updates the homepage with no manual edit. Safe to run locally too:

    python3 tools/update_homepage_latest_post.py

Standard library only. Exits non-zero (and leaves index.html untouched)
if a card can't be parsed, so a broken card never ships a broken homepage.
"""
import re
import struct
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog.html"
HOME = ROOT / "index.html"
START = "<!-- LATEST-POST:START (auto-generated from blog.html by tools/update_homepage_latest_post.py; do not edit by hand) -->"
END = "<!-- LATEST-POST:END -->"


def fail(msg):
    print(f"update_homepage_latest_post: {msg}", file=sys.stderr)
    sys.exit(1)


def image_size(path):
    """Return (width, height) for a PNG or JPEG, or None."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            seg = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + seg
    return None


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).strip()


def parse_cards(html):
    cards = re.findall(r'<article class="card"[^>]*>(.*?)</article>', html, re.S)
    if not cards:
        fail("no post cards found in blog.html")
    posts = []
    for order, c in enumerate(cards):
        href = re.search(r'href="(blog/[^"]+\.html)"', c)
        pic = re.search(r"<picture\b.*?</picture>", c, re.S) or re.search(r"<img\b[^>]*>", c)
        kicker = re.search(r'<p class="kicker"[^>]*>(.*?)</p>', c, re.S)
        title = re.search(r"<h3[^>]*>(.*?)</h3>", c, re.S)
        excerpt = re.search(r'<p style="flex:1;">(.*?)</p>', c, re.S)
        date = re.search(r'color:#777;">\s*([A-Z][a-z]+ \d{1,2}, \d{4})\s*</p>', c)
        missing = [n for n, m in [("link", href), ("image", pic), ("category", kicker),
                                  ("title", title), ("summary", excerpt), ("date", date)] if not m]
        if missing:
            fail(f"card #{order + 1} in blog.html is missing: {', '.join(missing)}")
        try:
            d = datetime.strptime(date.group(1), "%B %d, %Y").date()
        except ValueError:
            fail(f"card #{order + 1} has an unreadable date: {date.group(1)!r}")
        posts.append({
            "order": order, "href": href.group(1), "picture": pic.group(0),
            "kicker": strip_tags(kicker.group(1)), "title": strip_tags(title.group(1)),
            "excerpt": excerpt.group(1).strip(), "date": d, "date_text": date.group(1),
        })
    return posts


def build_card(p):
    pic = p["picture"]
    img = re.search(r"<img\b[^>]*>", pic).group(0)
    is_diagram = bool(re.search(r'class="[^"]*\bcontain\b', img))
    src = re.search(r'src="([^"]+)"', img).group(1)
    alt = re.search(r'alt="([^"]*)"', img)
    alt = alt.group(1) if alt else p["title"]
    source = re.search(r"<source\b[^>]*>", pic)
    size = image_size(ROOT / src)
    dims = f' height="{size[1]}" width="{size[0]}"' if size else ""
    new_img = f'<img alt="{alt}"{dims} loading="lazy" src="{src}"/>'
    picture = ('<picture style="display:contents">' + (source.group(0) if source else "") + new_img + "</picture>")
    img_class = "learning-latest-image is-diagram" if is_diagram else "learning-latest-image"
    iso = p["date"].isoformat()
    return (
        f'<a class="learning-latest-card" href="{p["href"]}">\n'
        f'<div class="{img_class}">{picture}</div>\n'
        f'<div class="learning-latest-copy"><p class="eyebrow"><span class="learning-latest-badge">Newest Article</span> '
        f'{p["kicker"]} <span aria-hidden="true" class="learning-latest-sep">·</span> '
        f'<time datetime="{iso}">{p["date_text"]}</time></p>'
        f'<h3>{p["title"]}</h3><p>{p["excerpt"]}</p>'
        f'<span class="text-link">Read the article <span aria-hidden="true">↗</span></span></div>\n'
        f"</a>\n"
    )


def main():
    posts = parse_cards(BLOG.read_text(encoding="utf-8"))
    newest = sorted(posts, key=lambda p: (-p["date"].toordinal(), p["order"]))[0]
    if not (ROOT / newest["href"]).exists():
        fail(f"newest card links to {newest['href']}, which does not exist")

    home = HOME.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)
    block = START + "\n" + build_card(newest) + END + "\n"
    if not pattern.search(home):
        fail("LATEST-POST markers not found in index.html")
    updated = pattern.sub(lambda _: block, home, count=1)
    if updated != home:
        HOME.write_text(updated, encoding="utf-8")
        print(f"Homepage now features: {newest['title']} ({newest['date_text']})")
    else:
        print(f"Homepage already features: {newest['title']} ({newest['date_text']})")


def refresh_breadcrumbs():
    """Also runs in the Pages deploy: rebuild visible breadcrumbs from each
    page's JSON-LD so a post copied from a template never ships a stale trail.
    Best effort only; a failure here must never block the deploy."""
    try:
        import runpy
        runpy.run_path(str(ROOT / "tools" / "sync-breadcrumbs.py"), run_name="__main__")
    except SystemExit:
        pass
    except Exception as exc:  # pragma: no cover
        print(f"breadcrumb refresh skipped: {exc}")


if __name__ == "__main__":
    main()
    refresh_breadcrumbs()
