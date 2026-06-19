#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VERSION_URL = "https://raw.githubusercontent.com/yaojingang/yao-meta-skill/main/VERSION"
DEFAULT_MANIFEST_URL = "https://raw.githubusercontent.com/yaojingang/yao-meta-skill/main/manifest.json"
CACHE_DIR = ROOT / ".yao"
CACHE_PATH = CACHE_DIR / "update-check.json"
ALLOWED_UPDATE_HOST = "raw.githubusercontent.com"
ALLOWED_UPDATE_PATH_PREFIX = "/yaojingang/yao-meta-skill/"


def load_local_version(root: Path) -> str:
    version_file = root / "VERSION"
    if version_file.exists():
        value = version_file.read_text(encoding="utf-8").strip()
        if value:
            return value
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        version = str(payload.get("version", "")).strip()
        if version:
            return version
    return "0.0.0"


def normalize_version(value: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", value)
    if not parts:
        return (0,)
    return tuple(int(part) for part in parts)


def is_newer(remote: str, local: str) -> bool:
    remote_parts = normalize_version(remote)
    local_parts = normalize_version(local)
    length = max(len(remote_parts), len(local_parts))
    remote_parts = remote_parts + (0,) * (length - len(remote_parts))
    local_parts = local_parts + (0,) * (length - len(local_parts))
    return remote_parts > local_parts


def fetch_text(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": "yao-meta-skill-update-check"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8").strip()


def validate_update_url(url: str, allow_custom: bool) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"Update URL scheme is not allowed: {parsed.scheme or 'missing'}")
    is_default_source = (
        parsed.netloc == ALLOWED_UPDATE_HOST
        and parsed.path.startswith(ALLOWED_UPDATE_PATH_PREFIX)
    )
    if not is_default_source and not allow_custom:
        raise ValueError("Custom update URLs require --allow-custom-update-url.")


def validate_update_urls(version_url: str, manifest_url: str, allow_custom: bool) -> None:
    validate_update_url(version_url, allow_custom)
    validate_update_url(manifest_url, allow_custom)


def fetch_remote_version(version_url: str, manifest_url: str, timeout: float) -> tuple[str, str]:
    try:
        value = fetch_text(version_url, timeout)
        if value:
            return value.splitlines()[0].strip(), version_url
    except (HTTPError, URLError, TimeoutError, OSError):
        pass
    manifest_text = fetch_text(manifest_url, timeout)
    payload = json.loads(manifest_text)
    version = str(payload.get("version", "")).strip()
    if not version:
        raise ValueError("Remote manifest does not contain a version.")
    return version, manifest_url


def read_cache(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def write_cache(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_result(
    local_version: str,
    remote_version: str | None,
    source: str | None,
    checked: bool,
    skipped: bool = False,
    error: str | None = None,
) -> dict:
    update_available = bool(remote_version and is_newer(remote_version, local_version))
    return {
        "ok": error is None,
        "checked": checked,
        "skipped": skipped,
        "local_version": local_version,
        "remote_version": remote_version,
        "update_available": update_available,
        "source": source,
        "install_hint": "npx skills add yaojingang/yao-meta-skill" if update_available else "",
        "error": error,
    }


def check_update(
    root: Path,
    cache_path: Path,
    version_url: str,
    manifest_url: str,
    timeout: float,
    max_age_days: int,
    force: bool,
    no_cache: bool,
    allow_custom_url: bool = False,
) -> dict:
    local_version = load_local_version(root)
    today = str(date.today())
    if not force and not no_cache:
        cache = read_cache(cache_path)
        if cache.get("checked_at") == today and cache.get("local_version") == local_version:
            return {
                **build_result(
                    local_version=local_version,
                    remote_version=cache.get("remote_version"),
                    source=cache.get("source"),
                    checked=False,
                    skipped=True,
                    error=cache.get("error"),
                ),
                "cached": True,
            }
    try:
        validate_update_urls(version_url, manifest_url, allow_custom_url)
        remote_version, source = fetch_remote_version(version_url, manifest_url, timeout)
        result = build_result(local_version, remote_version, source, checked=True)
    except Exception as exc:  # noqa: BLE001 - update checks should never break authoring.
        result = build_result(local_version, None, None, checked=True, error=str(exc))
    if not no_cache:
        write_cache(
            cache_path,
            {
                "checked_at": today,
                "local_version": local_version,
                "remote_version": result.get("remote_version"),
                "source": result.get("source"),
                "error": result.get("error"),
            },
        )
    result["cached"] = False
    result["max_age_days"] = max_age_days
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Check whether yao-meta-skill has a newer GitHub version.")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--cache-path", default=str(CACHE_PATH))
    parser.add_argument("--version-url", default=os.environ.get("YAO_UPDATE_VERSION_URL", DEFAULT_VERSION_URL))
    parser.add_argument("--manifest-url", default=os.environ.get("YAO_UPDATE_MANIFEST_URL", DEFAULT_MANIFEST_URL))
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--max-age-days", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument(
        "--allow-custom-update-url",
        action="store_true",
        default=os.environ.get("YAO_ALLOW_CUSTOM_UPDATE_URL") == "1",
        help="Allow custom HTTPS update URLs. file:// and non-HTTPS schemes are always blocked.",
    )
    args = parser.parse_args()
    result = check_update(
        root=Path(args.root).resolve(),
        cache_path=Path(args.cache_path).resolve(),
        version_url=args.version_url,
        manifest_url=args.manifest_url,
        timeout=args.timeout,
        max_age_days=args.max_age_days,
        force=args.force,
        no_cache=args.no_cache,
        allow_custom_url=args.allow_custom_update_url,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
