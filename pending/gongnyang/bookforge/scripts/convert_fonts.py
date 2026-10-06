#!/usr/bin/env python3
"""bookforge font converter — CFF(.otf) -> TrueType(.ttf), in-repo reproducible.

Why: Chromium print-to-PDF cannot subset CFF outlines and silently falls back
to Type3 glyph drawings (per-page vector soup: no text extraction guarantees,
8-10x file size, G2 unenforceable). TrueType(glyf) embeds as proper Type0
subsets. Measured: same text, OTF -> 19 Type3 objects / converted TTF -> 1
Type0 subset, 0 Type3.

Scope: Pretendard, Noto Serif KR (both OFL, no Reserved Font Name -> modified
versions redistributable under the same license). Gmarket Sans declares RFN,
so its TTF must come from the official distribution (fetch_fonts.py), never
from conversion here.

Conversion: fontTools cu2qu pen, max error 1.0 unit @ em 2048 (sub-pixel).
Metrics (advance widths, vertical metrics, name/license tables) are preserved,
so pagination is unaffected.

Run: python3 scripts/convert_fonts.py  (idempotent; skips existing .ttf)
"""
import sys
import time
from pathlib import Path

from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable

FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"
MAX_ERR = 1.0  # font units @ em 2048/1000 — sub-pixel at book sizes

CONVERT_FAMILIES = ("Pretendard-", "NotoSerifKR-")  # OFL, no RFN
NEVER_CONVERT = ("GmarketSans",)  # OFL with Reserved Font Name — official TTF only


def otf2ttf(src: Path, dst: Path):
    t0 = time.time()
    f = TTFont(str(src))
    if "CFF " not in f:
        print(f"skip (not CFF): {src.name}")
        return
    glyph_order = f.getGlyphOrder()
    glyph_set = f.getGlyphSet()
    glyf = newTable("glyf")
    glyf.glyphOrder = glyph_order
    glyf.glyphs = {}
    for name in glyph_order:
        pen = TTGlyphPen(glyph_set)
        glyph_set[name].draw(Cu2QuPen(pen, MAX_ERR, reverse_direction=True))
        glyf.glyphs[name] = pen.glyph()
    f["glyf"] = glyf
    f["loca"] = newTable("loca")
    maxp = f["maxp"]
    maxp.tableVersion = 0x00010000
    for k in ("maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs",
              "maxInstructionDefs", "maxStackElements", "maxSizeOfInstructions",
              "maxComponentElements", "maxComponentDepth"):
        setattr(maxp, k, 1 if k == "maxZones" else 0)
    post = f["post"]
    post.formatType = 2.0
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = glyph_order
    for tag in ("CFF ", "VORG"):
        if tag in f:
            del f[tag]
    f.sfntVersion = "\x00\x01\x00\x00"
    f.save(str(dst))
    print(f"{src.name} -> {dst.name}: {time.time() - t0:.1f}s, {len(glyph_order)} glyphs")


def main():
    targets = [p for p in sorted(FONTS.glob("*.otf"))
               if p.name.startswith(CONVERT_FAMILIES)]
    if not targets:
        print("no CFF fonts to convert")
        return
    for src in targets:
        if any(src.name.startswith(n) for n in NEVER_CONVERT):
            print(f"REFUSE (Reserved Font Name): {src.name}", file=sys.stderr)
            continue
        dst = src.with_suffix(".ttf")
        if dst.exists():
            print(f"exists: {dst.name}")
            continue
        otf2ttf(src, dst)


if __name__ == "__main__":
    main()
