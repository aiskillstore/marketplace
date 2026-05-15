#!/usr/bin/env python3
"""Best-effort screenshot helpers for operation manuals."""

from __future__ import annotations

import argparse
import json
import shutil
import re
from pathlib import Path
from urllib.parse import urljoin

from common import ensure_dir, read_json, write_json


def safe_name(path: str) -> str:
    value = path.strip("/") or "home"
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    return value[:80] or "page"


def collect_manual_screenshots(input_dir: Path, out_dir: Path) -> dict[str, object]:
    out_dir = ensure_dir(out_dir)
    screenshots = []
    errors = []
    allowed = {".png", ".jpg", ".jpeg", ".webp"}
    for index, path in enumerate(sorted(input_dir.iterdir()), start=1):
        if path.suffix.lower() not in allowed or not path.is_file():
            continue
        target = out_dir / f"{index:02d}-{safe_name(path.stem)}{path.suffix.lower()}"
        if path.resolve() != target.resolve():
            shutil.copy2(path, target)
        screenshots.append({"route": "", "url": "", "path": str(target), "source": str(path)})
    if not screenshots:
        errors.append({"error": f"no screenshot images found in {input_dir}"})
    manifest = {
        "status": "ok" if screenshots else "empty",
        "method": "user-supplied",
        "screenshots": screenshots,
        "errors": errors,
    }
    write_json(out_dir / "截图清单.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url")
    parser.add_argument("--analysis")
    parser.add_argument("--out-dir", default="软件著作权申请资料/截图")
    parser.add_argument("--max-pages", type=int, default=8)
    parser.add_argument("--manual-dir", help="Collect user-supplied screenshots from this directory")
    args = parser.parse_args()

    if args.manual_dir:
        manifest = collect_manual_screenshots(Path(args.manual_dir), Path(args.out_dir))
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        if not manifest["screenshots"]:
            raise SystemExit(3)
        return

    if not args.base_url or not args.analysis:
        raise SystemExit("Missing --base-url and --analysis unless --manual-dir is provided")

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        print(json.dumps({"status": "error", "reason": f"playwright unavailable: {exc}"}, ensure_ascii=False))
        raise SystemExit(2)

    analysis = read_json(Path(args.analysis))
    paths = analysis.get("routes") or ["/"]
    clean_paths = []
    for path in paths:
        if isinstance(path, str) and path.startswith("/") and path not in clean_paths:
            clean_paths.append(path)
    clean_paths = clean_paths[: args.max_pages] or ["/"]

    out_dir = ensure_dir(Path(args.out_dir))
    screenshots = []
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        for route in clean_paths:
            url = urljoin(args.base_url.rstrip("/") + "/", route.lstrip("/"))
            file_path = out_dir / f"{safe_name(route)}.png"
            try:
                page.goto(url, wait_until="networkidle", timeout=15_000)
                page.screenshot(path=str(file_path), full_page=True)
                screenshots.append({"route": route, "url": url, "path": str(file_path)})
            except Exception as exc:
                errors.append({"route": route, "url": url, "error": str(exc)})
        browser.close()

    manifest = {"status": "ok" if screenshots else "partial", "screenshots": screenshots, "errors": errors}
    write_json(out_dir / "截图清单.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    if not screenshots:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
