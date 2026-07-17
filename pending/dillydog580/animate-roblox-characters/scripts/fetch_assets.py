#!/usr/bin/env python3
"""Fetch pinned external Roblox authoring assets from their original sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import ssl
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


SKILL_DIRECTORY = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SKILL_DIRECTORY / "assets" / "toolchain-manifest.json"
DEFAULT_DESTINATION = SKILL_DIRECTORY / "assets" / "external"
ALLOWED_HOSTS = {
    "devforum.roblox.com",
    "devforum-uploads.s3.dualstack.us-east-2.amazonaws.com",
    "github.com",
    "objects.githubusercontent.com",
    "prod.docsiteassets.roblox.com",
}


def _validate_download_url(url: str) -> urllib.parse.ParseResult:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"Download URL is not allowlisted: {url}")
    return parsed


class _AllowlistedRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        _validate_download_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def component(manifest: dict[str, Any], component_id: str) -> dict[str, Any]:
    for item in manifest.get("components", []):
        if item.get("id") == component_id:
            return item
    raise ValueError(f"Unknown component: {component_id}")


def _safe_target(root: Path, relative: str) -> Path:
    target = (root / relative).resolve()
    if root.resolve() not in target.parents:
        raise ValueError(f"Unsafe destination path: {relative}")
    return target


def _download(url: str, target: Path, expected_sha256: str, expected_size: int) -> dict[str, Any]:
    _validate_download_url(url)
    if target.is_file():
        digest = sha256_file(target)
        if digest == expected_sha256 and target.stat().st_size == expected_size:
            return {"path": str(target), "sha256": digest, "status": "already-verified"}
        raise RuntimeError(f"Refusing to overwrite an unverified file: {target}")

    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "animate-roblox-characters/1.0"})
    context = ssl.create_default_context()
    opener = urllib.request.build_opener(
        _AllowlistedRedirectHandler(),
        urllib.request.HTTPSHandler(context=context),
    )
    fd, temporary_name = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=target.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        with opener.open(request, timeout=60) as response, temporary.open("wb") as output:
            _validate_download_url(response.geturl())
            content_length = response.headers.get("Content-Length")
            if content_length is not None and int(content_length) > expected_size:
                raise RuntimeError(
                    f"Download is larger than expected for {target.name}: {content_length} bytes"
                )
            written = 0
            while True:
                chunk = response.read(min(1024 * 1024, expected_size + 1 - written))
                if not chunk:
                    break
                output.write(chunk)
                written += len(chunk)
                if written > expected_size:
                    raise RuntimeError(f"Download exceeded expected size for {target.name}")
        size = temporary.stat().st_size
        digest = sha256_file(temporary)
        if size != expected_size:
            raise RuntimeError(f"Size mismatch for {target.name}: expected {expected_size}, received {size}")
        if digest != expected_sha256:
            raise RuntimeError(f"SHA-256 mismatch for {target.name}: expected {expected_sha256}, received {digest}")
        temporary.replace(target)
        return {"path": str(target), "sha256": digest, "status": "downloaded-and-verified"}
    finally:
        temporary.unlink(missing_ok=True)


def fetch_component(component_id: str, destination_root: Path = DEFAULT_DESTINATION) -> dict[str, Any]:
    manifest = load_manifest()
    item = component(manifest, component_id)
    downloads = item.get("downloads", [])
    if not downloads:
        raise ValueError(f"Component has no pinned downloads: {component_id}")
    artifacts = []
    for download in downloads:
        target = _safe_target(destination_root, download["destination"])
        artifacts.append(
            _download(
                download["url"],
                target,
                download["sha256"],
                int(download["size"]),
            )
        )
    return {
        "ok": True,
        "component": component_id,
        "source": item.get("source"),
        "license": item.get("license", "unknown"),
        "artifacts": artifacts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", default="r6-ik-fk-v222")
    parser.add_argument("--destination-root", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--list", action="store_true", help="List components with pinned downloads without networking")
    args = parser.parse_args(sys.argv[1:])
    if args.list:
        manifest = load_manifest()
        payload = [item["id"] for item in manifest.get("components", []) if item.get("downloads")]
        print(json.dumps(payload, indent=2))
        return 0
    try:
        result = fetch_component(args.component, args.destination_root.expanduser().resolve())
    except Exception as exc:
        result = {"ok": False, "component": args.component, "errors": [str(exc)]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
