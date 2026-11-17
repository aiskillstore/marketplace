#!/usr/bin/env python3
"""Generate assets/demo.gif from the anyviz banner animation.

This script reproduces the banner's SMIL timeline deterministically: it emits
one SVG per frame with interpolated values, rasterizes each with cairosvg, and
assembles a looping GIF with Pillow. It reuses the outlined wordmark geometry
from make_wordmark.build() so the GIF matches the static banner exactly.
"""
import io
import math
import cairosvg
from PIL import Image
import make_wordmark as wm

W, H = 1280, 420
FPS = 25
DURATION = 4.0
HOLD = 1.2
FRAMES = int(DURATION * FPS)
HOLD_FRAMES = int(HOLD * FPS)

# Pre-build the light-on-dark wordmark geometry once.
G = wm.build("#F8FAFC", light=True, x0=0)
WM_EDGE = G["right_edge"]
WM_X = (W - WM_EDGE) / 2
WM_Y = 60
TAIL_PTS = G["tail_pts"]
TAIL_TOTAL = sum(math.hypot(x2 - x1, y2 - y1)
                 for (x1, y1), (x2, y2) in zip(TAIL_PTS, TAIL_PTS[1:]))


def ease_out(t):
    return 1 - (1 - t) ** 3


def clamp01(x):
    return max(0.0, min(1.0, x))


def seg(t, begin, dur):
    return ease_out(clamp01((t - begin) / dur))


def bar(x, color, target_h, prog, base_y=270):
    h = target_h * prog
    return f'<rect x="{x}" y="{base_y - h:.1f}" width="34" height="{h:.1f}" rx="4" fill="{color}"/>'


def frame_svg(t):
    b1, b2, b3 = seg(t, 0.2, 0.7), seg(t, 0.32, 0.7), seg(t, 0.44, 0.7)
    bars = (f'<g transform="translate(96,0)">'
            + bar(0, "#4269d0", 70, b1) + bar(46, "#6cc5b0", 120, b2)
            + bar(92, "#3ca951", 92, b3) + "</g>")

    line_prog = seg(t, 0.9, 1.1)
    area_op = clamp01((t - 1.1) / 0.8)
    line_off = 320 * (1 - line_prog)
    right = (f'<g transform="translate(940,150)">'
             f'<path d="M0 120 L40 95 L40 120 Z M40 95 L88 105 L88 120 L40 120 Z '
             f'M88 105 L140 60 L140 120 L88 120 Z M140 60 L196 26 L196 120 L140 120 Z" '
             f'fill="url(#b-area)" opacity="{area_op:.2f}"/>'
             f'<polyline points="0,120 40,95 88,105 140,60 196,26" fill="none" stroke="url(#b-grad)" '
             f'stroke-width="5" stroke-linecap="round" stroke-linejoin="round" '
             f'stroke-dasharray="320" stroke-dashoffset="{line_off:.1f}"/>')
    for cx, cy, col, r, begin in [(40, 95, "#4269d0", 6, 1.4), (88, 105, "#6cc5b0", 6, 1.55),
                                   (140, 60, "#6cc5b0", 6, 1.7), (196, 26, "#3ca951", 7, 1.85)]:
        rp = clamp01((t - begin) / 0.3) * r
        stroke = "#FFFFFF" if col == "#3ca951" else col
        fill = "#3ca951" if col == "#3ca951" else "#03050C"
        right += f'<circle cx="{cx}" cy="{cy}" r="{rp:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
    right += "</g>"

    wm_op = clamp01((t - 0.5) / 0.6)
    rise = (1 - seg(t, 0.5, 0.7)) * 18
    tail_prog = seg(t, 1.0, 0.7)
    tail_off = TAIL_TOTAL * (1 - tail_prog)
    z_dot_op = clamp01((t - 1.6) / 0.3)
    pulse = 11.5
    if t > 2.2:
        pulse = 11.5 + 2.0 * (0.5 - 0.5 * math.cos((t - 2.2) / 1.6 * 2 * math.pi))
    wmg = (f'<g transform="translate({WM_X:.1f},{WM_Y + rise:.1f})" opacity="{wm_op:.2f}">'
           + G["axis"] + G["anyv"] + G["stem"]
           + f'<circle cx="{G["i_cx"]:.1f}" cy="33" r="{pulse:.1f}" fill="#4269d0" stroke="#03050C" stroke-width="3"/>'
           + G["z"]
           + f'<g stroke-dasharray="{TAIL_TOTAL:.1f}" stroke-dashoffset="{tail_off:.1f}">{G["tail_poly"]}</g>'
           + f'<circle cx="{TAIL_PTS[-1][0]:.1f}" cy="46" r="6.5" fill="#3ca951" stroke="#03050C" stroke-width="2.5" opacity="{z_dot_op:.2f}"/>'
           + "</g>")

    tag_op = clamp01((t - 1.8) / 0.8)
    tagline = (f'<text x="640" y="362" text-anchor="middle" fill="#9696a0" '
               f'font-family="Helvetica,Arial,sans-serif" font-size="22" font-weight="400" '
               f'letter-spacing="3" opacity="{tag_op:.2f}">AI-NATIVE DATA VISUALIZATION</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <linearGradient id="av-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#4269d0"/><stop offset="55%" stop-color="#6cc5b0"/><stop offset="100%" stop-color="#3ca951"/></linearGradient>
    <linearGradient id="b-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#4269d0"/><stop offset="55%" stop-color="#6cc5b0"/><stop offset="100%" stop-color="#3ca951"/></linearGradient>
    <radialGradient id="b-glow" cx="50%" cy="42%" r="60%"><stop offset="0%" stop-color="#4269d0" stop-opacity="0.16"/><stop offset="70%" stop-color="#03050C" stop-opacity="0"/></radialGradient>
    <linearGradient id="b-area" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4269d0" stop-opacity="0.30"/><stop offset="100%" stop-color="#4269d0" stop-opacity="0"/></linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="#03050C"/>
  <rect width="{W}" height="{H}" fill="url(#b-glow)"/>
  <g stroke="#FFFFFF" stroke-opacity="0.04" stroke-width="1"><line x1="0" y1="105" x2="{W}" y2="105"/><line x1="0" y1="210" x2="{W}" y2="210"/><line x1="0" y1="315" x2="{W}" y2="315"/></g>
  {bars}{right}{wmg}{tagline}
</svg>'''


def main():
    scale = 0.5
    images = []
    for i in range(FRAMES):
        t = i / FPS
        png = cairosvg.svg2png(bytestring=frame_svg(t).encode(),
                               output_width=int(W * scale), output_height=int(H * scale))
        images.append(Image.open(io.BytesIO(png)).convert("RGB"))
    images.extend([images[-1]] * HOLD_FRAMES)

    pal = images[-1].quantize(colors=128, method=Image.MEDIANCUT)
    frames = [im.quantize(palette=pal, dither=Image.NONE) for im in images]
    frames[0].save("assets/demo.gif", save_all=True, append_images=frames[1:],
                   duration=int(1000 / FPS), loop=0, optimize=True, disposal=2)
    print("wrote assets/demo.gif")


if __name__ == "__main__":
    main()
