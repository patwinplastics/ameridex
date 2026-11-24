#!/usr/bin/env python3
"""Build per-page 1200x630 Open Graph / Twitter card images.

Usage: python3 tools/build_og_images.py [slug ...]
Writes assets/img/og/<slug>.jpg. Diagram cards reuse the page's own inline SVG
diagram; photo cards frame an existing site image. Requires playwright + Pillow.
"""
import base64, io, pathlib, re, sys
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/img/og"
IMG = ROOT / "assets/img"

# slug: (page file, kicker, Title Case headline, visual, tag)
# visual: "svg" = first inline <svg> on the page, or an image path under assets/img
PAGES = {
 "under-deck-home-gym": ("under-deck-home-gym.html", "AmeriDex Guide", "Home Gym Under a Deck: Work Out in a Dry Space", "svg", "Diagram For Illustration Only"),
 "under-deck-carport": ("under-deck-carport.html", "AmeriDex Guide", "Carport Under a Deck: Park in a Dry Space", "svg", "Diagram For Illustration Only"),
 "under-deck-ceiling": ("under-deck-ceiling.html", "AmeriDex Guide", "Under Deck Ceiling Options for a Dry Deck", "svg", "Diagram For Illustration Only"),
 "under-deck-dog-area": ("under-deck-dog-area.html", "AmeriDex Guide", "Dog Area Under a Deck: A Dry, Shaded Spot", "svg", "Diagram For Illustration Only"),
 "under-deck-hot-tub": ("under-deck-hot-tub.html", "AmeriDex Guide", "Hot Tub Under a Deck: Plan a Dry, Covered Spa Spot", "svg", "Diagram For Illustration Only"),
 "under-deck-play-area": ("under-deck-play-area.html", "AmeriDex Guide", "Under Deck Play Area: A Dry, Shaded Spot for Kids", "svg", "Diagram For Illustration Only"),
 "under-deck-screened-porch": ("under-deck-screened-porch.html", "AmeriDex Guide", "Screened Porch Under a Deck", "svg", "Diagram For Illustration Only"),
 "under-deck-storage": ("under-deck-storage.html", "AmeriDex Guide", "Under Deck Storage That Stays Dry", "svg", "Diagram For Illustration Only"),
 "outdoor-kitchen-under-deck": ("outdoor-kitchen-under-deck.html", "AmeriDex Guide", "Outdoor Kitchen Under a Deck: How to Keep It Dry", "svg", "Diagram For Illustration Only"),
 "balcony-waterproofing": ("balcony-waterproofing.html", "AmeriDex Guide", "Balcony Waterproofing With Real Deck Boards", "svg", "Diagram For Illustration Only"),
 "under-deck-drainage-systems-compared": ("under-deck-drainage-systems-compared.html", "AmeriDex Guide", "Under-Deck Drainage Systems Compared", "diagrams/ameridex-system.svg", "Diagram For Illustration Only"),
 "above-joist-deck-drainage": ("above-joist-deck-drainage.html", "AmeriDex Guide", "Above-Joist Deck Drainage: Water Stops Above the Framing", "diagrams/dexerdry-cross-section.png", "Diagram For Illustration Only"),
 "above-joist-deck-drainage-cost": ("above-joist-deck-drainage-cost.html", "AmeriDex Guide", "Above-Joist Deck Drainage Cost Guide", "diagrams/dexerdry-profile.svg", "Dexerdry Seal Profile"),
 "dry-space-under-deck": ("dry-space-under-deck.html", "AmeriDex Guide", "Dry Space Decking: Keep the Space Under Your Deck Dry", "photo:gallery/09-under-deck-lounge.jpg", "Design Inspiration"),
 "keep-under-deck-dry": ("keep-under-deck-dry.html", "AmeriDex Guide", "Decking That Keeps the Space Under Your Deck Dry", "photo:gallery/11-lakeside-under-deck-seating.jpg", "Design Inspiration"),
 "protect-under-deck-from-water": ("protect-under-deck-from-water.html", "AmeriDex Guide", "How to Protect Under Your Deck From Water and Rain", "photo:blog/storm-dryspace.jpg", "Design Inspiration"),
 "deck-rain-shield": ("deck-rain-shield.html", "AmeriDex Guide", "Deck Rain Shield and Rain Guard: Keep Rain Out From Under a Deck", "photo:hero.jpg", "Design Inspiration"),
 "what-to-look-for-deck-rain-guard": ("what-to-look-for-deck-rain-guard.html", "AmeriDex Guide", "What to Look For in a Deck Rain Guard", "photo:blog/nj-shore-dryspace.jpg", "Design Inspiration"),
 "how-to-choose-under-deck-drainage-system": ("how-to-choose-under-deck-drainage-system.html", "AmeriDex Guide", "How to Choose an Under-Deck Drainage System", "photo:gallery/08-deck-stairs-cropped.jpg", ""),
 "above-joist-vs-below-joist-deck-drainage": ("above-joist-vs-below-joist-deck-drainage.html", "AmeriDex Guide", "Above-Joist vs Below-Joist Deck Drainage", "photo:blog/above-vs-below-hero.jpg", "Design Inspiration"),
 "waterproof-decking": ("waterproof-decking.html", "AmeriDex Guide", "Waterproof Decking: Deck Boards That Are the Waterproof Layer", "photo:lifestyle/waterproof-decking-patio.webp", "Design Inspiration"),
 "pvc-decking": ("pvc-decking.html", "AmeriDex Guide", "PVC Decking Made in the USA", "swatches", "AmeriDex Colors"),
 "blog-choosing-the-right-ameridex-color": ("blog/choosing-the-right-ameridex-color.html", "AmeriDex Blog", "Choosing the Right AmeriDex Color for Your Home", "swatches-all", "AmeriDex Colors"),
 "blog-nj-shore-deck-guide": ("blog/nj-shore-deck-guide.html", "AmeriDex Blog", "Why Coastal Decks Fail Faster", "photo:blog/nj-shore-hero.jpg", "Design Inspiration"),
 "blog-planning-a-new-deck-checklist": ("blog/planning-a-new-deck-checklist.html", "AmeriDex Blog", "Planning a New Deck: A Pre-Construction Checklist", "photo:gallery/05-deck-installed.jpg", ""),
 "blog-under-deck-living-space-ideas": ("blog/under-deck-living-space-ideas.html", "AmeriDex Blog", "5 Ways to Turn the Space Under Your Deck Into a Living Space", "photo:gallery/10-under-deck-kitchen-dining.jpg", "Design Inspiration"),
 "blog-why-decks-rot-from-the-top-down": ("blog/why-decks-rot-from-the-top-down.html", "AmeriDex Blog", "Why Decks Rot From the Top Down and How to Stop It", "crop:blog/ameridex-dry-joists.jpg", "Diagram For Illustration Only"),
 "blog-above-joist-vs-below-joist-buyer-guide": ("blog/above-joist-vs-below-joist-buyer-guide.html", "AmeriDex Blog", "Above-Joist vs Below-Joist Deck Drainage: A Buyer's Guide", "diagrams/ameridex-system.svg", "Diagram For Illustration Only"),
 "blog-fall-deck-maintenance-checklist": ("blog/fall-deck-maintenance-checklist.html", "AmeriDex Blog", "Fall Deck Maintenance Checklist: 8 Steps Before Winter", "photo:og/sources/fall-deck-maintenance.jpg", "Design Inspiration"),
 "blog-how-to-clean-pvc-deck-boards": ("blog/how-to-clean-pvc-deck-boards.html", "AmeriDex Blog", "How to Clean and Maintain PVC Deck Boards", "photo:og/sources/clean-pvc-deck.jpg", "Design Inspiration"),
 "blog-installing-ameridex-pro-guide": ("blog/installing-ameridex-pro-guide.html", "AmeriDex Blog", "Installing AmeriDex: A Builder's Guide to a Watertight Deck", "blog/deck-slope-drainage.jpg", "Diagram For Illustration Only"),
 "blog-cellular-pvc-vs-composite-decking": ("blog/cellular-pvc-vs-composite-decking.html", "AmeriDex Blog", "PVC Decking vs Composite Decking: The Full Case for PVC", "cropbox:pvc-vs-composite-core.jpg:0,150,1600,785", "Diagram For Illustration Only"),
 "blog-dexerdry-automotive-grade-tpe-seal": ("blog/dexerdry-automotive-grade-tpe-seal.html", "AmeriDex Blog", "Why the Dexerdry Seal Is Built From Automotive-Grade TPE", "diagrams/dexerdry-cross-section.png", "Diagram For Illustration Only"),
 "second-story-deck-waterproofing": ("second-story-deck-waterproofing.html", "AmeriDex Guide", "Second-Story Deck Waterproofing: Keep the Patio Below Dry", "photo:gallery/05-deck-installed.jpg", ""),
 "blog": ("blog.html", "The AmeriDex Blog", "Decks, Drainage and the Space Underneath", "blog-index", "Diagrams For Illustration Only"),
}

def data_uri(path, max_w=1400):
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

def png_uri(path):
    return "data:image/png;base64," + base64.b64encode(pathlib.Path(path).read_bytes()).decode()

LOGO = png_uri(IMG / "logo.png")
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:630px;overflow:hidden;font-family:Inter,'Open Sans',sans-serif}
.kick{font-family:Montserrat,sans-serif;font-weight:800;letter-spacing:3px;text-transform:uppercase;font-size:20px;color:#D6263A}
h1{font-family:Montserrat,sans-serif;font-weight:800;line-height:1.12;letter-spacing:-0.5px}
.tag{position:absolute;font-size:15px;font-weight:600;padding:6px 12px;border-radius:6px;background:rgba(7,31,58,.82);color:#fff}
.url{font-family:Montserrat,sans-serif;font-weight:700;font-size:22px}
"""

def diagram_html(kicker, title, visual_html, tag):
    size = 46 if len(title) <= 48 else 40
    return f"""<html><head><style>{CSS}
body{{background:#F7F5F0}}
.top{{position:absolute;left:0;top:0;width:1200px;height:200px;background:#0A2A4E;padding:30px 56px}}
.top img{{position:absolute;right:56px;top:22px;height:36px;background:#fff;padding:6px 10px;border-radius:6px}}
.top h1{{color:#fff;font-size:{size}px;margin-top:24px;max-width:1080px}}
.bar{{position:absolute;left:0;top:200px;width:1200px;height:8px;background:#D6263A}}
.card{{position:absolute;left:56px;top:230px;width:1088px;height:350px;background:#fff;border-radius:14px;box-shadow:0 4px 18px rgba(0,0,0,.08);display:flex;align-items:center;justify-content:center;overflow:hidden;padding:14px}}
.card svg,.card img{{max-width:100%;max-height:100%;width:auto;height:100%}}
.foot{{position:absolute;left:56px;bottom:12px;color:#0A2A4E}}
.tag{{right:56px;bottom:10px;background:#EFEAE0;color:#0A2A4E}}
</style></head><body>
<div class="top"><div class="kick">{kicker}</div><h1>{title}</h1><img src="{LOGO}"></div><div class="bar"></div>
<div class="card">{visual_html}</div>
<div class="foot url">ameridex.com</div>{f'<div class="tag">{tag}</div>' if tag else ''}
</body></html>"""

def photo_html(kicker, title, photo_uri, tag, pos="center"):
    size = 46 if len(title) <= 40 else (40 if len(title) <= 56 else 36)
    return f"""<html><head><style>{CSS}
body{{background:#0A2A4E}}
.ph{{position:absolute;left:470px;top:0;width:730px;height:630px;background:url({photo_uri}) {pos}/cover}}
.fade{{position:absolute;left:470px;top:0;width:120px;height:630px;background:linear-gradient(90deg,#0A2A4E,rgba(10,42,78,0))}}
.panel{{position:absolute;left:0;top:0;width:520px;height:630px;padding:52px 40px 44px 56px}}
.panel img{{height:44px;background:#fff;padding:7px 11px;border-radius:6px}}
.kick{{margin-top:56px}}
.rule{{width:72px;height:6px;background:#D6263A;margin:18px 0 22px}}
h1{{color:#fff;font-size:{size}px}}
.url{{position:absolute;left:56px;bottom:44px;color:#EFEAE0}}
.tag{{right:18px;bottom:18px}}
</style></head><body>
<div class="ph"></div><div class="fade"></div>
<div class="panel"><img src="{LOGO}"><div class="kick">{kicker}</div><div class="rule"></div><h1>{title}</h1><div class="url">ameridex.com</div></div>
{f'<div class="tag">{tag}</div>' if tag else ''}
</body></html>"""

def swatch_html(names):
    cells = "".join(
        f'<div style="flex:1;background:url({data_uri(IMG/"swatches-flat"/(n+".jpg"),600)}) center/cover;position:relative">'
        f'<span style="position:absolute;left:0;right:0;bottom:0;background:rgba(7,31,58,.78);color:#fff;font:600 14px Inter;padding:6px 4px;text-align:center">{n.replace("-"," ").title()}</span></div>'
        for n in names)
    return f'<div style="display:flex;gap:6px;width:100%;height:100%;border-radius:8px;overflow:hidden">{cells}</div>'

def build(slug, page):
    page_file, kicker, title, visual, tag = PAGES[slug]
    if visual == "blog-index":
        imgs = ["blog/deck-slope-drainage.jpg", "diagrams/dexerdry-cross-section.png", "blog/patio-under-a-deck.jpg"]
        cards = "".join(f'<div style="flex:1;min-width:0;text-align:center"><img style="width:100%;height:255px;object-fit:contain" src="{data_uri(IMG/f)}"><div style="font:700 19px Montserrat;color:#0A2A4E;margin-top:8px">{label}</div></div>' for f,label in zip(imgs,["Plan Your Deck", "Know Your Materials", "Use the Space Below"]))
        return diagram_html(kicker,title, f'<div style="display:flex;gap:16px;width:100%;align-items:center">{cards}</div>',tag)
    if visual == "svg":
        src = (ROOT / page_file).read_text()
        svg = re.search(r"<svg.*?</svg>", src, re.S).group(0)
        return diagram_html(kicker, title, svg, tag)
    if visual.endswith(".svg"):
        return diagram_html(kicker, title, (IMG / visual).read_text(), tag)
    if visual.startswith("photo:"):
        return photo_html(kicker, title, data_uri(IMG / visual[6:]), tag)
    if visual.startswith("cropbox:"):
        _, f, box = visual.split(":")
        im = Image.open(IMG / f).convert("RGB").crop(tuple(int(v) for v in box.split(",")))
        b = io.BytesIO(); im.save(b, "JPEG", quality=92)
        return diagram_html(kicker, title, f'<img src="data:image/jpeg;base64,{base64.b64encode(b.getvalue()).decode()}">', tag)
    if visual.startswith("crop:"):
        im = Image.open(IMG / visual[5:]).convert("RGB")
        im = im.crop((0, 130, im.width, im.height))
        b = io.BytesIO(); im.save(b, "JPEG", quality=92)
        uri = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
        return diagram_html(kicker, title, f'<img src="{uri}">', tag)
    if visual == "swatches":
        return diagram_html(kicker, title, swatch_html(["royal-ipe","tropical-walnut","chestnut","coastal-driftwood","slate","khaki"]), tag)
    if visual == "swatches-all":
        names = sorted(p.stem for p in (IMG/"swatches-flat").glob("*.jpg"))
        return diagram_html(kicker, title, swatch_html(names[:7]) .replace('height:100%','height:49%') + swatch_html(names[7:]).replace('height:100%','height:49%'), tag)
    if pathlib.Path(IMG / visual).suffix in (".png", ".jpg"):
        return diagram_html(kicker, title, f'<img src="{data_uri(IMG/visual,1600)}">', tag)
    raise ValueError(visual)

def main():
    slugs = sys.argv[1:] or list(PAGES)
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        for s in slugs:
            html = build(s, None)
            if s == "blog-choosing-the-right-ameridex-color":
                html = html.replace('<div class="card">', '<div class="card" style="flex-direction:column;gap:8px">')
            pg.set_content(html, wait_until="load")
            pg.wait_for_timeout(400)
            png = pg.screenshot(type="png")
            im = Image.open(io.BytesIO(png)).convert("RGB")
            dest = OUT / f"{s}.jpg"
            q = 86
            while True:
                im.save(dest, "JPEG", quality=q, optimize=True, progressive=True)
                if dest.stat().st_size < 290_000 or q <= 60: break
                q -= 6
            print(s, im.size, dest.stat().st_size // 1024, "KB q", q)
        b.close()

if __name__ == "__main__":
    main()
