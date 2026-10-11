#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "pillow-heif"]
# ///
"""Read photo metadata: GPS, capture time, camera model, focal length. The first thing to do before geolocating.

  exif.py <photo> [<photo> ...]

- With GPS: gives WGS84 coordinates and the GCJ-02 conversion (for Amap/Tencent Maps) directly, but you still must check against the image (metadata can be edited).
- With capture time: can be fed to sun.py (note EXIF time is usually local time at the capture location, without a time zone; see the OffsetTime field).
- With 35mm equivalent focal length: can be fed to geo.py range / geometry.md to compute the field of view, no need to guess the zoom factor.
- WeChat, QQ and most social platforms strip metadata when forwarding; screenshots and rephotographed images have no metadata. Empty output is normal and means nothing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import ExifTags, Image

sys.path.insert(0, str(Path(__file__).parent))
import geo  # noqa: E402

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:  # without pillow-heif, HEIC can't be read; other formats work as usual
    pass


def _deg(v, ref) -> float:
    d, m, s = (float(x) for x in v)
    val = d + m / 60 + s / 3600
    return -val if ref in ("S", "W") else val


def read(path: Path) -> dict:
    im = Image.open(path)
    ex = im.getexif()
    out: dict = {"file": str(path), "size": list(im.size)}
    base = {ExifTags.TAGS.get(k, k): v for k, v in ex.items()}
    sub = {ExifTags.TAGS.get(k, k): v for k, v in ex.get_ifd(0x8769).items()}
    for k in ("Make", "Model", "Software"):
        if base.get(k):
            out[k.lower()] = str(base[k]).strip("\x00 ")
    for k in ("DateTimeOriginal", "OffsetTimeOriginal"):
        if sub.get(k):
            out[k] = str(sub[k])
    if not out.get("DateTimeOriginal") and base.get("DateTime"):
        out["DateTime"] = str(base["DateTime"])
    if sub.get("FocalLengthIn35mmFilm"):
        out["focal_35mm"] = int(sub["FocalLengthIn35mmFilm"])
        lf, sf = geo.fov_from_equiv_focal(out["focal_35mm"])
        out["fov_4x3_long_short"] = [round(lf, 1), round(sf, 1)]
    elif sub.get("FocalLength"):
        out["focal_mm_actual"] = float(sub["FocalLength"])
    g = ex.get_ifd(0x8825)
    if g and 2 in g and 4 in g:
        lat, lon = _deg(g[2], g.get(1, "N")), _deg(g[4], g.get(3, "E"))
        out["gps_wgs84"] = [round(lat, 7), round(lon, 7)]
        out["gps_gcj02"] = [round(x, 7) for x in geo.convert(lat, lon, "wgs", "gcj")]
        if 6 in g:
            out["altitude_m"] = round(float(g[6]), 1)
        if 17 in g:
            out["image_direction_deg"] = round(float(g[17]), 1)   # some phones write the lens heading
    return out


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        try:
            print(json.dumps(read(Path(p)), ensure_ascii=False))
        except Exception as e:  # noqa: BLE001
            print(json.dumps({"file": p, "error": str(e)}, ensure_ascii=False))


if __name__ == "__main__":
    # Chinese Windows outputs GBK by default: it crashes on m², ñ, and Chinese text the agent reads comes out garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
