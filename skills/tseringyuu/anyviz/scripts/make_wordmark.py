#!/usr/bin/env python3
"""Generate a font-independent anyviz wordmark as outlined SVG paths.

Rendering text via <text> depends on the viewer having the named font; when it
falls back, glyph widths shift and the hand-placed custom 'i'/'z' no longer line
up (producing an "anyv iz" gap). Outlining the letters to paths removes the font
dependency entirely and lets us measure exact advances so the custom glyphs sit
flush against the text.

Outputs the <g> fragment for the wordmark; the caller embeds it in wordmark.svg
and banner.svg so both share identical geometry.
"""
import freetype

FONT = "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"  # metric-compatible with Arial
SIZE = 104           # em px
TRACK = -3           # letter-spacing px
BASELINE = 105       # y of baseline in the 130-tall viewbox


def glyph_path(face, ch, pen_x, baseline, scale):
    """Return (svg_path_d, advance_px) for a single character outlined at scale."""
    face.load_char(ch, freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_BITMAP)
    outline = face.glyph.outline
    pts = outline.points
    tags = outline.tags
    contours = outline.contours

    def X(v): return pen_x + v * scale
    def Y(v): return baseline - v * scale  # flip y (font up is +, svg down is +)

    d = []
    start = 0
    for end in contours:
        seg = list(range(start, end + 1))
        cpts = [pts[i] for i in seg]
        ctags = [tags[i] for i in seg]
        # rotate so we begin on an on-curve point
        on = [i for i, t in enumerate(ctags) if t & 1]
        if not on:
            start = end + 1
            continue
        o = on[0]
        cpts = cpts[o:] + cpts[:o]
        ctags = ctags[o:] + ctags[:o]
        cpts.append(cpts[0]); ctags.append(ctags[0])

        d.append(f"M{X(cpts[0][0]):.2f} {Y(cpts[0][1]):.2f}")
        i = 1
        while i < len(cpts):
            if ctags[i] & 1:  # on-curve -> line
                d.append(f"L{X(cpts[i][0]):.2f} {Y(cpts[i][1]):.2f}")
                i += 1
            else:  # quadratic control point
                cx, cy = cpts[i]
                if i + 1 < len(cpts) and (ctags[i + 1] & 1):
                    nx, ny = cpts[i + 1]
                    d.append(f"Q{X(cx):.2f} {Y(cy):.2f} {X(nx):.2f} {Y(ny):.2f}")
                    i += 2
                else:  # implied on-curve midpoint between two off-curve pts
                    nx, ny = cpts[i + 1]
                    mx, my = (cx + nx) / 2, (cy + ny) / 2
                    d.append(f"Q{X(cx):.2f} {Y(cy):.2f} {X(mx):.2f} {Y(my):.2f}")
                    i += 1
        d.append("Z")
        start = end + 1

    advance = face.glyph.advance.x  # font units (FT_LOAD_NO_SCALE)
    return " ".join(d), advance * scale


def outline_text(text, x0, baseline, fill):
    face = freetype.Face(FONT)
    units = face.units_per_EM
    scale = SIZE / units  # font units -> px
    pen = x0
    paths = []
    for ch in text:
        d, adv = glyph_path(face, ch, pen, baseline, scale)
        if d:
            paths.append(d)
        pen += adv + TRACK
    body = f'<path d="{" ".join(paths)}" fill="{fill}"/>'
    return body, pen


def build(dark_fill, light=False, x0=20):
    """Build the wordmark fragments + geometry.

    Returns a dict so the static wordmark, the animated banner, and the GIF
    frame generator can all share identical outlined geometry.
    """
    anyv, after_anyv = outline_text("anyv", x0, BASELINE, dark_fill)

    # custom "i": a stem matched to lowercase x-height, plus a data-point dot
    i_x = after_anyv + 3
    stem = f'<rect x="{i_x:.1f}" y="52" width="15" height="53" rx="3.5" fill="{dark_fill}"/>'
    dot_stroke = "#03050C" if light else "#FFFFFF"
    dot = f'<circle cx="{i_x + 7.5:.1f}" cy="33" r="11.5" fill="#4269d0" stroke="{dot_stroke}" stroke-width="3"/>'

    # "z" outlined, placed after the i stem
    z_x = i_x + 15 + 4
    z, after_z = outline_text("z", z_x, BASELINE, dark_fill)

    # trend tail rising off the z
    t0 = after_z + 8
    tail_pts = [(t0, 97), (t0 + 13, 78), (t0 + 26, 85), (t0 + 40, 46)]
    tail_poly = ((f'<polyline points="{" ".join(f"{x:.1f},{y}" for x, y in tail_pts)}" '
                  f'fill="none" stroke="url(#av-grad)" stroke-width="5.5" '
                  f'stroke-linecap="round" stroke-linejoin="round"/>'))
    tail_dot_stroke = "#03050C" if light else "#FFFFFF"
    tail_dot = (f'<circle cx="{t0+40:.1f}" cy="46" r="6.5" fill="#3ca951" '
                f'stroke="{tail_dot_stroke}" stroke-width="2.5"/>')

    right_edge = t0 + 46
    axis = (f'<line x1="22" y1="{BASELINE}" x2="{right_edge:.1f}" y2="{BASELINE}" '
            f'stroke="{"#FFFFFF" if light else "#9696a0"}" stroke-width="1.4" '
            f'stroke-opacity="{0.18 if light else 0.35}"/>')

    return {
        "axis": axis, "anyv": anyv, "stem": stem, "dot": dot, "z": z,
        "tail_poly": tail_poly, "tail_dot": tail_dot, "tail_pts": tail_pts,
        "i_cx": i_x + 7.5, "right_edge": right_edge,
        "static": axis + anyv + stem + dot + z + tail_poly + tail_dot,
    }


if __name__ == "__main__":
    g = build("#1A1A1A")
    edge = g["right_edge"]
    vb_w = int(edge + 24)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} 130" width="{vb_w}" height="130" role="img" aria-label="anyviz">
  <title>anyviz</title>
  <desc>anyviz wordmark — the "i" dot is a data point and the "z" leads into a rising trend line. Letters are outlined paths for font-independent rendering.</desc>
  <defs>
    <linearGradient id="av-grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#4269d0"/><stop offset="55%" stop-color="#6cc5b0"/><stop offset="100%" stop-color="#3ca951"/>
    </linearGradient>
  </defs>
  {g["static"]}
</svg>
'''
    open("assets/wordmark.svg", "w").write(svg)
    print(f"wrote assets/wordmark.svg (viewBox width {vb_w}, right edge {edge:.1f})")
