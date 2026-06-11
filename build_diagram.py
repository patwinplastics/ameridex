#!/usr/bin/env python3
"""Render the PVC-vs-composite cross-section diagram as a crisp SVG -> PNG."""
import subprocess, os

NAVY   = "#0A2A4E"
NAVYD  = "#071F3A"
RED    = "#D6263A"
GOLD   = "#CDB795"
CREAM  = "#EFEAE0"
OFFW   = "#F7F5F0"
INK    = "#1A1A1A"
GREY   = "#6B7785"
LINE   = "#E5E1D8"
GREEN  = "#2E7D5B"

W, H = 1600, 920

def board_pvc(x, y, w, h):
    """Solid cellular PVC board: uniform fill, ASA cap top strip, no internal layers."""
    parts = []
    # ASA cap (top thin strip) - gold
    cap_h = 16
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{cap_h}" rx="6" fill="{GOLD}"/>')
    parts.append(f'<rect x="{x}" y="{y+cap_h-6}" width="{w}" height="6" fill="{GOLD}"/>')
    # solid PVC core - one uniform material, subtle cellular dots
    parts.append(f'<rect x="{x}" y="{y+cap_h}" width="{w}" height="{h-cap_h}" rx="6" fill="#E9EEF3" stroke="{NAVY}" stroke-width="2"/>')
    # uniform "cellular" texture: faint even dots, signalling homogeneous core
    dots = []
    import random
    random.seed(7)
    for gx in range(int(x)+26, int(x+w)-18, 34):
        for gy in range(int(y+cap_h)+26, int(y+h)-18, 30):
            dots.append(f'<circle cx="{gx}" cy="{gy}" r="3.4" fill="#CBD6E0"/>')
    parts.append("".join(dots))
    return "".join(parts)

def board_composite(x, y, w, h):
    """Capped composite: polymer cap shell + visible wood-fiber core inside."""
    parts = []
    cap = 10
    # outer polymer cap (3-sided: top, left, right; bottom open)
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{GOLD}" opacity="0.55"/>')
    # wood-fiber core (inset), warm brown with streaks
    cx, cy, cw, ch = x+cap, y+cap, w-2*cap, h-cap  # bottom NOT capped -> open
    parts.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" fill="#A9743B"/>')
    # wood-fiber streaks
    streaks = []
    import random
    random.seed(11)
    for i in range(70):
        sx = random.uniform(cx+6, cx+cw-30)
        sy = random.uniform(cy+6, cy+ch-6)
        ln = random.uniform(14, 40)
        op = random.uniform(0.18, 0.5)
        col = random.choice(["#7E5326", "#C68A4C", "#6B451F"])
        streaks.append(f'<rect x="{sx:.0f}" y="{sy:.0f}" width="{ln:.0f}" height="3" rx="1.5" fill="{col}" opacity="{op:.2f}"/>')
    parts.append("".join(streaks))
    # thin cap outline so the shell reads clearly
    parts.append(f'<path d="M {x} {y+h} L {x} {y} L {x+w} {y} L {x+w} {y+h}" fill="none" stroke="#B8A270" stroke-width="3"/>')
    return "".join(parts)

def label(x, y, text, color=NAVY, size=30, weight=700, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="Archivo, Arial, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{text}</text>')

def tag(x, y, text, color):
    """small uppercase kicker"""
    return (f'<text x="{x}" y="{y}" font-family="Archivo, Arial, sans-serif" font-size="20" '
            f'font-weight="800" letter-spacing="2" fill="{color}" text-anchor="middle">{text}</text>')

def chip(cx, cy, text, ok):
    col = GREEN if ok else RED
    icon = ('<path d="M -7 0 L -2 5 L 8 -6" fill="none" stroke="white" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
            if ok else
            '<path d="M -6 -6 L 6 6 M 6 -6 L -6 6" fill="none" stroke="white" stroke-width="3.2" stroke-linecap="round"/>')
    return (f'<g transform="translate({cx},{cy})">'
            f'<circle cx="0" cy="0" r="15" fill="{col}"/>'
            f'<g transform="translate(0,0)">{icon}</g>'
            f'<text x="26" y="7" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="500" fill="{INK}">{text}</text>'
            f'</g>')

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append(f'<rect width="{W}" height="{H}" fill="{OFFW}"/>')

# header band
svg.append(f'<rect x="0" y="0" width="{W}" height="118" fill="{NAVY}"/>')
svg.append(tag(W/2, 46, "AMERIDEX MATERIALS", GOLD))
svg.append(f'<text x="{W/2}" y="90" font-family="Archivo, Arial, sans-serif" font-size="40" font-weight="800" fill="#FFFFFF" text-anchor="middle">What is inside the board: cellular PVC vs composite</text>')

# --- LEFT: cellular PVC ---
lx, by, bw, bh = 200, 250, 380, 360
svg.append(board_pvc(lx, by, bw, bh))
svg.append(label(lx+bw/2, 215, "CELLULAR PVC (AMERIDEX)", NAVY, 27, 800, "middle"))
# ASA cap callout
svg.append(f'<line x1="{lx+bw+10}" y1="{by+8}" x2="{lx+bw+70}" y2="{by+8}" stroke="{GREY}" stroke-width="2"/>')
svg.append(label(lx+bw+80, by+15, "Proprietary ASA cap", GREY, 22, 600))
svg.append(label(lx+bw+80, by+45, "Solid PVC core, all the", GREY, 22, 400))
svg.append(label(lx+bw+80, by+72, "way through", GREY, 22, 400))
# cut edge note
svg.append(f'<line x1="{lx}" y1="{by+bh+18}" x2="{lx+bw}" y2="{by+bh+18}" stroke="{GREEN}" stroke-width="3"/>')
svg.append(label(lx+bw/2, by+bh+52, "A cut edge is just more PVC", GREEN, 22, 700, "middle"))
# chips
cyl = by+bh+105
svg.append(chip(lx+10, cyl,      "No wood, no organic filler", True))
svg.append(chip(lx+10, cyl+44,   "Will not rot or feed mold", True))
svg.append(chip(lx+10, cyl+88,   "Lighter, easier to handle", True))

# --- RIGHT: composite ---
rx = 1020
svg.append(board_composite(rx, by, bw, bh))
svg.append(label(rx+bw/2, 215, "CAPPED COMPOSITE", NAVY, 27, 800, "middle"))
# core callout (placed inside the board to avoid the center 'vs' badge)
svg.append(f'<rect x="{rx+bw-250}" y="{by+bh-94}" width="232" height="74" rx="8" fill="#FFFFFF" opacity="0.92"/>')
svg.append(label(rx+bw-234, by+bh-62, "Wood-fiber core", "#7E5326", 22, 800))
svg.append(label(rx+bw-234, by+bh-34, "under the cap", "#7E5326", 22, 500))
# breach markers (red) on the cap
def breach(cx, cy, txt):
    return (f'<g><circle cx="{cx}" cy="{cy}" r="13" fill="{RED}"/>'
            f'<text x="{cx}" y="{cy+7}" font-family="Archivo, Arial, sans-serif" font-size="22" font-weight="800" fill="white" text-anchor="middle">!</text></g>'
            + label(cx+22, cy+7, txt, RED, 20, 700))
# top scratch breach
svg.append(breach(rx+90, by+6, "scratch"))
# bottom open (3-sided) breach
svg.append(f'<line x1="{rx+10}" y1="{by+bh}" x2="{rx+bw-10}" y2="{by+bh}" stroke="{RED}" stroke-width="4" stroke-dasharray="8 6"/>')
svg.append(label(rx+bw/2, by+bh+34, "Open underside on 3-sided caps", RED, 21, 700, "middle"))
svg.append(label(rx+bw/2, by+bh+60, "Cut ends expose the wood", RED, 21, 700, "middle"))
# chips
svg.append(chip(rx+10, cyl,      "Organic wood fiber inside", False))
svg.append(chip(rx+10, cyl+44,   "Absorbs moisture where breached", False))
svg.append(chip(rx+10, cyl+88,   "Heavier, holds heat longer", False))

# center divider
svg.append(f'<line x1="{W/2}" y1="170" x2="{W/2}" y2="{H-40}" stroke="{LINE}" stroke-width="2"/>')
svg.append(f'<circle cx="{W/2}" cy="{by+bh/2}" r="34" fill="{NAVY}"/>')
svg.append(f'<text x="{W/2}" y="{by+bh/2+9}" font-family="Archivo, Arial, sans-serif" font-size="26" font-weight="800" fill="white" text-anchor="middle">vs</text>')

# footer caption
svg.append(f'<text x="40" y="{H-18}" font-family="Inter, Arial, sans-serif" font-size="20" fill="{GREY}" text-anchor="start">Cellular PVC has no wood to protect, which is why it wins on moisture, weight, cut edges, and lifespan.</text>')
svg.append(f'<text x="{W-40}" y="{H-18}" font-family="Archivo, Arial, sans-serif" font-size="20" font-weight="700" fill="{NAVY}" text-anchor="end">ameridex.com</text>')
svg.append('</svg>')

svg_str = "".join(svg)
with open("assets/img/pvc-vs-composite-core.svg", "w") as f:
    f.write(svg_str)

# convert to PNG at 2x for crispness
out = "assets/img/pvc-vs-composite-core.jpg"
# try rsvg-convert, then inkscape, then cairosvg
ok = False
for cmd in (["rsvg-convert","-w","1600","-h","920","assets/img/pvc-vs-composite-core.svg","-o","assets/img/_tmp.png"],):
    try:
        subprocess.run(cmd, check=True)
        ok = True
    except Exception as e:
        print("rsvg failed:", e)
if not ok:
    try:
        import cairosvg
        cairosvg.svg2png(url="assets/img/pvc-vs-composite-core.svg", write_to="assets/img/_tmp.png", output_width=1600, output_height=920)
        ok = True
    except Exception as e:
        print("cairosvg failed:", e)
print("rendered_png" if ok else "NO_RENDERER")
