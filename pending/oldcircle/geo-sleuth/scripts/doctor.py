#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright"]
# ///
"""Check geo-sleuth setup without uploading photos or downloading ML models.

  uv run scripts/doctor.py                   local tools, data, browser, writable directory
  uv run scripts/doctor.py --network         also probe public service endpoints
  uv run scripts/doctor.py --json            machine-readable results on stdout

uv may install this script's Playwright dependency on first use. Network probes only
check reachability, not image uploads, API stability, coverage, or model inference.
Exit codes: 0 = no failed checks (warnings may remain); 1 = at least one failed check.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from _browser import launch_browser
from _net import PROXY_HELP, curl_args, resolve_proxy
import regions

SERVICES = {
    "Baidu image search": "https://graph.baidu.com/pcpage/index?tpl_from=pc",
    "Baidu panoramas": "https://mapsv0.bdimg.com/?qt=qsdata&x=0&y=0",
    "Yandex Images": "https://yandex.com/images/",
    "Google satellite tiles": "https://mt1.google.com/vt/lyrs=s&x=0&y=0&z=0",
    "Overpass": "https://overpass-api.de/api/status",
    "Elevation tiles": "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/0/0/0.png",
    "Hugging Face": "https://huggingface.co/",
}


# gsv.py's panorama lookup at a covered point (Shibuya). An HTTP probe isn't enough here: a turned-down endpoint still answers 200.
STREET_VIEW = ("https://maps.googleapis.com/$rpc/google.internal.maps.mapsjs.v1.MapsJsInternalService/SingleImageSearch",
               '[["apiv3",null,null,null,"US",null,null,null,null,null,[[0]]],[[null,null,35.6595,139.7005],50],'
               '[null,["en","US"],null,null,null,null,null,null,[2],null,[[[2,true,2]]]],[[1,2,3,4,8,6]]]')


def check(name: str, status: str, detail: str, fix: str = "") -> dict:
    return {"name": name, "status": status, "detail": detail, "fix": fix}


def probe(item: tuple[str, str], proxy: str | None) -> dict:
    name, url = item
    try:
        result = subprocess.run(
            ["curl", "-q", "-sSL", "--max-time", "12", *curl_args(proxy),
             "-A", "geo-sleuth-doctor/1.0", "-o", os.devnull, "-w", "%{http_code}", url],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15)
        code = result.stdout.strip()
        if result.returncode:
            return check(name, "FAIL", f"Connection failed (curl exit {result.returncode}).",
                         "Check DNS, TLS certificates and network access.")
        if code.isdigit() and 200 <= int(code) < 400:
            return check(name, "PASS", f"HTTP {code}; reachable (a live operation can still be blocked or rate-limited).")
        return check(name, "WARN", f"HTTP {code}; server reached, but service access was not confirmed.",
                     "Retry later or inspect the service in a browser. HTTP 403/429 may mean a challenge or rate limit.")
    except (OSError, subprocess.TimeoutExpired):
        return check(name, "FAIL", "Probe could not complete within its time limit.", "Check curl and network access, then retry.")


def street_view_check(proxy: str | None) -> dict:
    name = "Google Street View"
    url, query = STREET_VIEW
    try:
        result = subprocess.run(
            ["curl", "-q", "-sS", "--max-time", "12", *curl_args(proxy), "-X", "POST",
             "-H", "content-type: application/json+protobuf", "-H", "x-user-agent: grpc-web-javascript/0.1",
             "--data", query, url],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return check(name, "FAIL", "Probe could not complete within its time limit.", "Check curl and network access, then retry.")
    if result.returncode:
        return check(name, "FAIL", f"Connection failed (curl exit {result.returncode}).", "Check DNS, TLS certificates and network access.")
    try:
        pano = json.loads(result.stdout)[1][1][1]
    except (ValueError, IndexError, TypeError, KeyError):
        pano = None
    if isinstance(pano, str) and pano:
        return check(name, "PASS", "Panorama lookup returned a panorama at a covered test point.")
    return check(name, "FAIL", f"Panorama lookup failed: {' '.join(result.stdout.split())[:160] or 'empty reply'}",
                 "gsv.py near/sheet won't work. If the reply says the service changed or was turned down, gsv.py needs updating.")


async def browser_check(proxy: str | None) -> dict:
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser, name = await launch_browser(p, proxy)
            try:
                page = await browser.new_page()
                await page.goto("about:blank")
                return check("Reverse-search browser", "PASS", f"{name} launched successfully.")
            finally:
                await browser.close()
    except Exception as exc:
        return check("Reverse-search browser", "WARN", str(exc),
                     "Install Chrome or run `uvx playwright install chromium`. Until then, use intake.py --no-rev.")


def diagnose(network: bool, proxy: str | None) -> dict:
    rows = [check("Python", "PASS" if sys.version_info >= (3, 10) else "FAIL",
                  platform.python_version(), "Use Python 3.10 or later." if sys.version_info < (3, 10) else "")]
    for tool in ("uv", "curl"):
        found = (os.environ.get("UV") or shutil.which("uv")) if tool == "uv" else shutil.which(tool)
        try:
            result = subprocess.run([found or tool, "--version"], capture_output=True, timeout=5)
            ok = result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            ok = False
        rows.append(check(tool, "PASS" if ok else "FAIL", "Available." if ok else "Not runnable.",
                          "" if ok else f"Install {tool} and reopen your terminal so it is on PATH."))
    try:
        with tempfile.TemporaryFile(dir=Path.cwd()) as file:
            file.write(b"geo-sleuth")
        rows.append(check("Working directory", "PASS", "Writable; reports and .geo-cache can be created here."))
    except OSError:
        rows.append(check("Working directory", "FAIL", "Cannot write here.", "Run from a writable folder."))
    data = Path(__file__).resolve().parent.parent / "data"
    names = ("calling_codes", "driving_side", "territories", "country_names")
    bad = []
    for name in names:
        try:
            json.loads((data / f"{name}.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            bad.append(name)
    rows.append(check("Global lookup tables", "FAIL" if bad else "PASS", "Missing or invalid: " + ", ".join(bad) if bad else f"All {len(names)} tables are readable.",
                      "Reinstall the complete skill folder (including data/)." if bad else ""))
    # A broken region pack only disables that country's lookups and tips; it never fails the core
    for code, pack in sorted(regions.packs().items()):
        try:
            errs, _ = regions.lint(pack)
        except regions.PACK_ERRORS as exc:
            errs = [str(exc)]
        rows.append(check(f"Region pack {code.lower()}", "WARN" if errs else "PASS",
                          "; ".join(errs[:2]) if errs else f"{pack.get('name', code)}: lookups {', '.join(pack.get('lookups') or {}) or 'none'}.",
                          f"`regions.py lint {code.lower()}` lists every problem; reinstall regions/{code.lower()}/ or remove it." if errs else ""))
    route = "configured proxy" if resolve_proxy(proxy) else "direct"
    rows.append(check("Service connection", "PASS", f"Using {route}."))
    rows.append(asyncio.run(browser_check(proxy)))
    rows.append(check("OCR", "INFO", "Apple Vision preferred; RapidOCR fallback." if sys.platform == "darwin" else "RapidOCR backend.",
                      "uv run ocr.py <photo> tests recognition; this check does not install or run OCR."))
    rows.append(check("ML models", "INFO", "Not loaded. match.py and sat_scan.py download model weights on first use; allow time and disk space."))
    if network and shutil.which("curl"):
        with ThreadPoolExecutor(max_workers=8) as pool:
            rows.extend(pool.map(lambda item: probe(item, proxy), SERVICES.items()))
        rows.append(street_view_check(proxy))
    else:
        rows.append(check("Network probes", "SKIP", "Run with --network to check service reachability."))
    return {"ok": not any(row["status"] == "FAIL" for row in rows), "connection": route, "checks": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--network", action="store_true", help="probe public endpoints without uploading photos")
    parser.add_argument("--proxy", help=PROXY_HELP)
    parser.add_argument("--json", action="store_true", help="print JSON for issue reports or automation")
    args = parser.parse_args()
    report = diagnose(args.network, args.proxy)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for row in report["checks"]:
            print(f"[{row['status']}] {row['name']}: {row['detail']}")
            if row["fix"]:
                print(f"  Next: {row['fix']}")
        print("\nNo failed checks. Review warnings before using optional features." if report["ok"] else "\nSome checks failed. Follow the suggested fixes and rerun doctor.py.")
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
