#!/usr/bin/env python3
"""Package a JPG/MOV pair as an AirDrop-friendly Live Photo .pvt bundle.

Run with:

  UV_CACHE_DIR=/private/tmp/uv-cache \
  UV_TOOL_DIR=/private/tmp/uv-tools \
  uvx --from 'makelive==0.7.0' python scripts/package-live-photo.py IMG.JPG IMG.MOV
"""

from __future__ import annotations

import argparse
from pathlib import Path

from makelive import save_live_photo_pair_as_pvt


def main() -> None:
    parser = argparse.ArgumentParser(description="Package a JPG/MOV pair as a Live Photo .pvt bundle.")
    parser.add_argument("jpg", type=Path, help="Key photo path, usually 1080x1440 JPG.")
    parser.add_argument("mov", type=Path, help="Paired H.264 MOV path.")
    args = parser.parse_args()

    jpg = args.jpg.expanduser().resolve()
    mov = args.mov.expanduser().resolve()
    if not jpg.exists():
        raise SystemExit(f"missing JPG: {jpg}")
    if not mov.exists():
        raise SystemExit(f"missing MOV: {mov}")

    asset_id, pvt_path = save_live_photo_pair_as_pvt(str(jpg), str(mov))
    print(asset_id)
    print(pvt_path)


if __name__ == "__main__":
    main()
