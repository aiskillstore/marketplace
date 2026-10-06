#!/usr/bin/env python3
"""bookforge contact sheet — raster pages for agent visual QC (G6).

Usage: python3 contact_sheet.py <pdf> <out_dir> [--dpi 90] [--pages 1,2,3,8-12]
Without --pages: renders every page. Also writes grid sheets sheet-N.png
(4x4 thumbnails) for fast full-book scans.
"""
import argparse, sys
from pathlib import Path

try:  # PyMuPDF 1.24+ 신 모듈명, 구버전은 fitz만 제공
    import pymupdf as fitz
except ImportError:
    import fitz

def parse_pages(spec, n):
    if not spec:
        return list(range(n))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a) - 1, min(int(b), n)))
        else:
            out.append(int(part) - 1)
    return [p for p in out if 0 <= p < n]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf"); ap.add_argument("out_dir")
    ap.add_argument("--dpi", type=int, default=90)
    ap.add_argument("--pages", default=None)
    ap.add_argument("--grid", action="store_true", help="also write 4x4 grid sheets")
    a = ap.parse_args()

    doc = fitz.open(a.pdf)
    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    pages = parse_pages(a.pages, doc.page_count)
    for p in pages:
        pix = doc[p].get_pixmap(dpi=a.dpi)
        pix.save(out / f"p{p+1:03d}.png")
    if a.grid:
        thumb_dpi = 40
        cell_w = cell_h = None
        import math
        per = 16
        for si in range(math.ceil(len(pages) / per)):
            chunk = pages[si * per:(si + 1) * per]
            pixes = [doc[p].get_pixmap(dpi=thumb_dpi) for p in chunk]
            cw = max(px.width for px in pixes); chh = max(px.height for px in pixes)
            sheet = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, cw * 4, chh * 4), False)
            sheet.clear_with(255)
            for i, px in enumerate(pixes):
                x, y = (i % 4) * cw, (i // 4) * chh
                # Pixmap.copy는 '대응 좌표'로 복사한다 — 원점을 타일 위치로 옮겨야 격자에 들어간다
                px.set_origin(x, y)
                sheet.copy(px, fitz.IRect(x, y, x + px.width, y + px.height))
            sheet.save(out / f"sheet-{si+1}.png")
    print(f"OK {len(pages)} pages -> {out}")

if __name__ == "__main__":
    main()
