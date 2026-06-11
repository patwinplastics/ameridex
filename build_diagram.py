#!/usr/bin/env python3
"""Render the PVC-vs-composite deck-board cross-section diagram as crisp SVG -> PNG."""
import subprocess, random

NAVY   = "#0A2A4E"
NAVYD  = "#071F3A"
RED    = "#D6263A"
GOLD   = "#CDB795"
GOLDD  = "#B8A270"
CREAM  = "#EFEAE0"
OFFW   = "#F7F5F0"
INK    = "#1A1A1A"
GREY   = "#6B7785"
LINE   = "#E5E1D8"
GREEN  = "#2E7D5B"

W, H = 1600, 1040

def rounded_board_path(x, y, w, h, r_top, r_bot):
    """Deck-board cross-section: eased (rounded) top corners, slightly eased bottom."""
    return (f'M {x} {y+r_top} '
            f'Q {x} {y} {x+r_top} {y} '
            f'L {x+w-r_top} {y} '
            f'Q {x+w} {y} {x+w} {y+r_top} '
            f'L {x+w} {y+h-r_bot} '
            f'Q {x+w} {y+h} {x+w-r_bot} {y+h} '
            f'L {x+r_bot} {y+h} '
            f'Q {x} {y+h} {x} {y+h-r_bot} Z')

def board_pvc(x, y, w, h):
    """Solid cellular PVC deck board with an ASA cap that wraps the top, both full
    sides, and ~1 inch under each edge (center underside bare). Wide eased profile."""
    parts = []
    rt, rb = 22, 8
    ct = 16          # cap thickness (visual)
    under = 110      # how far the cap wraps under each edge (~1 inch, to scale)
    # full board body (solid PVC) - light cool grey
    parts.append(f'<path d="{rounded_board_path(x,y,w,h,rt,rb)}" fill="#E9EEF3" stroke="{NAVY}" stroke-width="2.5"/>')
    # ASA cap as a wrapping shell: top + both sides + ~1in under each edge.
    # Outer edge follows the board profile; inner edge is offset inward by ct,
    # leaving the center underside uncapped (a gap of bare PVC).
    cap = (
        # outer boundary, clockwise from bottom-left-under-stop
        f'M {x+under} {y+h} '
        f'L {x+rb} {y+h} Q {x} {y+h} {x} {y+h-rb} '            # outer: bottom-left corner
        f'L {x} {y+rt} Q {x} {y} {x+rt} {y} '                  # up left side to top-left ease
        f'L {x+w-rt} {y} Q {x+w} {y} {x+w} {y+rt} '            # across top to top-right ease
        f'L {x+w} {y+h-rb} Q {x+w} {y+h} {x+w-rb} {y+h} '      # down right side, bottom-right corner
        f'L {x+w-under} {y+h} '                                # under-wrap stop on right
        f'L {x+w-under} {y+h-ct} '                             # step up to inner underside
        f'L {x+w-ct} {y+h-ct} '                                # inner underside (right) toward side
        f'L {x+w-ct} {y+rt} Q {x+w-ct} {y+ct} {x+w-rt} {y+ct} '# inner: right side up to inner top ease
        f'L {x+rt} {y+ct} Q {x+ct} {y+ct} {x+ct} {y+rt} '      # inner top across to inner top-left ease
        f'L {x+ct} {y+h-ct} '                                  # inner left side down
        f'L {x+under} {y+h-ct} Z'                              # inner underside (left), close
    )
    parts.append(f'<path d="{cap}" fill="{GOLD}" stroke="{GOLDD}" stroke-width="1.5"/>')
    # top-face sheen highlight (gives 3D board read)
    parts.append(f'<rect x="{x+rt}" y="{y+3}" width="{w-2*rt}" height="5" rx="2.5" fill="#FFFFFF" opacity="0.5"/>')
    # tiny markers showing where the underside wrap stops on each side
    for ux in (x+under, x+w-under):
        parts.append(f'<line x1="{ux}" y1="{y+h-ct}" x2="{ux}" y2="{y+h+10}" stroke="{GOLDD}" stroke-width="2" stroke-dasharray="3 3"/>')
    # uniform cellular texture in the core -> homogeneous solid PVC
    dots = []
    random.seed(7)
    for gx in range(int(x)+34, int(x+w)-24, 42):
        for gy in range(int(y+ct)+24, int(y+h)-14, 30):
            dots.append(f'<circle cx="{gx}" cy="{gy}" r="3.2" fill="#CBD6E0"/>')
    parts.append("".join(dots))
    return "".join(parts)

def board_composite(x, y, w, h):
    """Capped composite deck board: wide profile, eased top, polymer cap shell, wood-fiber core, open bottom."""
    parts = []
    rt, rb = 22, 8
    cap = 12
    # outer polymer cap shell following board profile
    parts.append(f'<path d="{rounded_board_path(x,y,w,h,rt,rb)}" fill="{GOLD}" opacity="0.6"/>')
    # wood-fiber core inset on top/left/right, OPEN at the bottom (3-sided cap)
    cx, cy, cw, ch = x+cap, y+cap, w-2*cap, h-cap
    parts.append(f'<path d="{rounded_board_path(cx,cy,cw,ch,rt-6,0)}" fill="#A9743B"/>')
    # wood-fiber streaks (horizontal grain inside the core)
    streaks = []
    random.seed(11)
    for _ in range(120):
        sx = random.uniform(cx+8, cx+cw-44)
        sy = random.uniform(cy+10, cy+ch-6)
        ln = random.uniform(20, 60)
        op = random.uniform(0.18, 0.5)
        col = random.choice(["#7E5326", "#C68A4C", "#6B451F"])
        streaks.append(f'<rect x="{sx:.0f}" y="{sy:.0f}" width="{ln:.0f}" height="3" rx="1.5" fill="{col}" opacity="{op:.2f}"/>')
    parts.append("".join(streaks))
    # cap outline (drawn on 3 sides only: left, top, right) to show open underside
    parts.append(f'<path d="M {x} {y+h-rb} L {x} {y+rt} Q {x} {y} {x+rt} {y} '
                 f'L {x+w-rt} {y} Q {x+w} {y} {x+w} {y+rt} L {x+w} {y+h-rb}" '
                 f'fill="none" stroke="{GOLDD}" stroke-width="3"/>')
    # top-face sheen
    parts.append(f'<rect x="{x+rt}" y="{y+3}" width="{w-2*rt}" height="5" rx="2.5" fill="#FFFFFF" opacity="0.35"/>')
    return "".join(parts)

def label(x, y, text, color=NAVY, size=30, weight=700, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="Archivo, Arial, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{text}</text>')

def tag(x, y, text, color):
    return (f'<text x="{x}" y="{y}" font-family="Archivo, Arial, sans-serif" font-size="20" '
            f'font-weight="800" letter-spacing="2" fill="{color}" text-anchor="middle">{text}</text>')

def chip(cx, cy, text, ok):
    col = GREEN if ok else RED
    icon = ('<path d="M -7 0 L -2 5 L 8 -6" fill="none" stroke="white" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
            if ok else
            '<path d="M -6 -6 L 6 6 M 6 -6 L -6 6" fill="none" stroke="white" stroke-width="3.2" stroke-linecap="round"/>')
    return (f'<g transform="translate({cx},{cy})">'
            f'<circle cx="0" cy="0" r="15" fill="{col}"/>'
            f'<g>{icon}</g>'
            f'<text x="26" y="7" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="500" fill="{INK}">{text}</text>'
            f'</g>')

def breach_dot(cx, cy):
    return (f'<g><circle cx="{cx}" cy="{cy}" r="13" fill="{RED}"/>'
            f'<text x="{cx}" y="{cy+7}" font-family="Archivo, Arial, sans-serif" font-size="22" font-weight="800" fill="white" text-anchor="middle">!</text></g>')

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append(f'<rect width="{W}" height="{H}" fill="{OFFW}"/>')

# header band
svg.append(f'<rect x="0" y="0" width="{W}" height="118" fill="{NAVY}"/>')
svg.append(tag(W/2, 46, "AMERIDEX MATERIALS", GOLD))
svg.append(f'<text x="{W/2}" y="90" font-family="Archivo, Arial, sans-serif" font-size="40" font-weight="800" fill="#FFFFFF" text-anchor="middle">What is inside the board: cellular PVC vs composite</text>')

# board geometry (wide deck-board cross-sections, stacked)
BX, BW, BH = 130, 760, 150
TOP_Y = 215
BOT_Y = 560

# ===== TOP: CELLULAR PVC =====
svg.append(label(BX, TOP_Y-22, "CELLULAR PVC  (AMERIDEX)", NAVY, 27, 800))
svg.append(label(BX+BW+10, TOP_Y-22, "wins", GREEN, 24, 800))
svg.append(board_pvc(BX, TOP_Y, BW, BH))
# ASA cap callout
svg.append(f'<line x1="{BX+BW}" y1="{TOP_Y+11}" x2="{BX+BW+40}" y2="{TOP_Y+11}" stroke="{GREY}" stroke-width="2"/>')
svg.append(label(BX+BW+50, TOP_Y+6, "Proprietary ASA cap", GREY, 21, 700))
svg.append(label(BX+BW+50, TOP_Y+33, "wraps top, sides, and", GREY, 19, 400))
svg.append(label(BX+BW+50, TOP_Y+56, "~1 in. under each edge", GREY, 19, 400))
# solid-core callout
svg.append(f'<line x1="{BX+BW}" y1="{TOP_Y+BH-30}" x2="{BX+BW+40}" y2="{TOP_Y+BH-30}" stroke="{GREY}" stroke-width="2"/>')
svg.append(label(BX+BW+50, TOP_Y+BH-35, "Solid PVC core,", GREY, 21, 700))
svg.append(label(BX+BW+50, TOP_Y+BH-9, "all the way through", GREY, 19, 400))
# green cut-edge note under board
svg.append(f'<line x1="{BX}" y1="{TOP_Y+BH+16}" x2="{BX+BW}" y2="{TOP_Y+BH+16}" stroke="{GREEN}" stroke-width="3"/>')
svg.append(label(BX, TOP_Y+BH+46, "A cut edge is just more PVC", GREEN, 22, 700))

# ===== BOTTOM: CAPPED COMPOSITE =====
svg.append(label(BX, BOT_Y-22, "CAPPED COMPOSITE", NAVY, 27, 800))
svg.append(board_composite(BX, BOT_Y, BW, BH))
# scratch breach on top cap
svg.append(breach_dot(BX+230, BOT_Y-2))
svg.append(label(BX+230+22, BOT_Y+5, "scratch breaks the cap", RED, 20, 700))
# wood-fiber core callout
svg.append(f'<line x1="{BX+BW}" y1="{BOT_Y+BH/2}" x2="{BX+BW+40}" y2="{BOT_Y+BH/2}" stroke="{GREY}" stroke-width="2"/>')
svg.append(label(BX+BW+50, BOT_Y+BH/2-4, "Wood-fiber core", "#7E5326", 21, 800))
svg.append(label(BX+BW+50, BOT_Y+BH/2+22, "under the cap", "#7E5326", 19, 500))
# open-bottom breach
svg.append(f'<line x1="{BX+10}" y1="{BOT_Y+BH}" x2="{BX+BW-10}" y2="{BOT_Y+BH}" stroke="{RED}" stroke-width="5" stroke-dasharray="9 7"/>')
svg.append(breach_dot(BX+30, BOT_Y+BH))
svg.append(label(BX, BOT_Y+BH+46, "Open underside on 3-sided caps  ·  cut ends expose the wood", RED, 22, 700))

# ===== chips row =====
CYL = 820
svg.append(chip(BX+10, CYL,      "No wood, no organic filler", True))
svg.append(chip(BX+10, CYL+46,   "Will not rot or feed mold", True))
svg.append(chip(BX+10, CYL+92,   "Lighter, easier to handle", True))
RCX = 850
svg.append(chip(RCX, CYL,      "Organic wood fiber inside", False))
svg.append(chip(RCX, CYL+46,   "Absorbs moisture where breached", False))
svg.append(chip(RCX, CYL+92,   "Heavier, holds heat longer", False))
# subtle divider between chip columns
svg.append(f'<line x1="{RCX-40}" y1="{CYL-26}" x2="{RCX-40}" y2="{CYL+108}" stroke="{LINE}" stroke-width="2"/>')

# footer caption
svg.append(f'<text x="40" y="{H-20}" font-family="Inter, Arial, sans-serif" font-size="20" fill="{GREY}" text-anchor="start">Cellular PVC has no wood to protect, which is why it wins on moisture, weight, cut edges, and lifespan.</text>')
svg.append(f'<text x="{W-40}" y="{H-20}" font-family="Archivo, Arial, sans-serif" font-size="20" font-weight="700" fill="{NAVY}" text-anchor="end">ameridex.com</text>')

svg.append('</svg>')

svg_str = "".join(svg)
with open("assets/img/pvc-vs-composite-core.svg", "w") as f:
    f.write(svg_str)

import cairosvg
cairosvg.svg2png(url="assets/img/pvc-vs-composite-core.svg",
                 write_to="assets/img/_tmp.png",
                 output_width=1600, output_height=1040)
print("rendered_png")
