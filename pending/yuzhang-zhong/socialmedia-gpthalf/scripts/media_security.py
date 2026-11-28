"""Local media validation and privacy-safe external selection helpers."""

from __future__ import annotations

import hashlib
import os
import re
import stat
from collections.abc import Iterable, Mapping
from pathlib import Path


DEFAULT_MAX_BYTES = 20 * 1024 * 1024
_CHUNK_SIZE = 1024 * 1024
_ASSET_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_SUPPORTED_MEDIA_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


class MediaSecurityError(ValueError):
    """A media input failed a local security or consent check."""


def _is_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def _reject_link_components(path: Path) -> None:
    """Reject symlinks and Windows junctions in every supplied path component."""

    current = Path(path.anchor)
    for part in path.parts[1:]:
        if part in {"", "."}:
            continue
        if part == "..":
            current = current.parent
            continue
        current = current / part
        try:
            if _is_link(current):
                raise MediaSecurityError("media paths must not contain symbolic links")
        except OSError as error:
            raise MediaSecurityError("media path metadata could not be inspected") from error


def _resolve_directory(path: str | os.PathLike[str]) -> Path:
    root = Path(path)
    if not root.is_absolute():
        raise MediaSecurityError("allowed_root must be an absolute directory")
    _reject_link_components(root)
    try:
        resolved = root.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise MediaSecurityError("allowed_root must be an existing directory") from error
    if not resolved.is_dir():
        raise MediaSecurityError("allowed_root must be an existing directory")
    return resolved


def _resolve_media_path(
    path: str | os.PathLike[str], allowed_root: str | os.PathLike[str] | None
) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        raise MediaSecurityError("media path must be an absolute local file")
    _reject_link_components(candidate)
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise MediaSecurityError("media path must be an existing local file") from error
    if allowed_root is not None:
        root = _resolve_directory(allowed_root)
        try:
            resolved.relative_to(root)
        except ValueError as error:
            raise MediaSecurityError("media file is outside allowed_root") from error
    try:
        mode = resolved.stat().st_mode
    except OSError as error:
        raise MediaSecurityError("media path metadata could not be inspected") from error
    if not stat.S_ISREG(mode):
        raise MediaSecurityError("media path must be a regular file")
    return resolved


def _media_type(header: bytes) -> str:
    if header.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if header.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "image/webp"
    raise MediaSecurityError("media file has an unsupported or invalid image signature")


def _validated_asset_id(asset_id: str | None, digest: str) -> str:
    if asset_id is None:
        return f"asset-{digest[:16]}"
    if not isinstance(asset_id, str) or not _ASSET_ID.fullmatch(asset_id):
        raise MediaSecurityError("asset_id must be a non-path logical identifier")
    return asset_id


def validate_media_file(
    path: str | os.PathLike[str],
    *,
    allowed_root: str | os.PathLike[str] | None = None,
    max_bytes: int = DEFAULT_MAX_BYTES,
    asset_id: str | None = None,
) -> dict:
    """Validate a local image and return an anonymous, path-free asset summary."""

    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes <= 0:
        raise MediaSecurityError("max_bytes must be a positive integer")
    resolved = _resolve_media_path(path, allowed_root)

    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    if no_follow:
        flags |= no_follow
    try:
        descriptor = os.open(resolved, flags)
    except OSError as error:
        raise MediaSecurityError("media file could not be opened safely") from error

    digest = hashlib.sha256()
    total = 0
    header = b""
    try:
        with os.fdopen(descriptor, "rb") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode):
                raise MediaSecurityError("media path must be a regular file")
            if opened.st_size > max_bytes:
                raise MediaSecurityError("media file exceeds max_bytes")
            while True:
                chunk = handle.read(_CHUNK_SIZE)
                if not chunk:
                    break
                if not header:
                    header = chunk[:16]
                total += len(chunk)
                if total > max_bytes:
                    raise MediaSecurityError("media file exceeds max_bytes")
                digest.update(chunk)
    except MediaSecurityError:
        raise
    except OSError as error:
        raise MediaSecurityError("media file could not be read safely") from error

    media_type = _media_type(header)
    hexadecimal = digest.hexdigest()
    return {
        "asset_id": _validated_asset_id(asset_id, hexadecimal),
        "media_type": media_type,
        "size_bytes": total,
        "sha256": hexadecimal,
    }


def _sanitize_summary(summary: Mapping) -> dict:
    asset_id = summary.get("asset_id")
    media_type = summary.get("media_type")
    size_bytes = summary.get("size_bytes")
    digest = summary.get("sha256")
    if not isinstance(asset_id, str) or not _ASSET_ID.fullmatch(asset_id):
        raise MediaSecurityError("asset summary contains an invalid asset_id")
    if media_type not in _SUPPORTED_MEDIA_TYPES:
        raise MediaSecurityError("asset summary contains an unsupported media_type")
    if isinstance(size_bytes, bool) or not isinstance(size_bytes, int) or size_bytes < 0:
        raise MediaSecurityError("asset summary contains an invalid size_bytes")
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
        raise MediaSecurityError("asset summary contains an invalid sha256")
    return {
        "asset_id": asset_id,
        "media_type": media_type,
        "size_bytes": size_bytes,
        "sha256": digest,
    }


def validate_external_selection(
    asset_summaries: Iterable[Mapping], selected_asset_ids: Iterable[str]
) -> list[dict]:
    """Return path-free summaries for the explicitly selected, known image IDs."""

    if isinstance(asset_summaries, (str, bytes, Mapping)):
        raise MediaSecurityError("asset_summaries must be an iterable of summaries")
    if isinstance(selected_asset_ids, (str, bytes, Mapping)):
        raise MediaSecurityError("selected_asset_ids must be an iterable of asset IDs")

    known: dict[str, dict] = {}
    for raw_summary in asset_summaries:
        if not isinstance(raw_summary, Mapping):
            raise MediaSecurityError("asset_summaries must contain mappings")
        summary = _sanitize_summary(raw_summary)
        key = summary["asset_id"]
        if key in known:
            raise MediaSecurityError("asset summaries contain duplicate asset IDs")
        known[key] = summary

    selected: list[dict] = []
    seen: set[str] = set()
    for asset_id in selected_asset_ids:
        if not isinstance(asset_id, str) or not _ASSET_ID.fullmatch(asset_id):
            raise MediaSecurityError("external selection contains an invalid asset ID")
        if asset_id in seen:
            raise MediaSecurityError("external selection contains duplicate asset IDs")
        seen.add(asset_id)
        if asset_id not in known:
            raise MediaSecurityError("external selection contains an unknown asset ID")
        selected.append(dict(known[asset_id]))
    return selected


# Descriptive aliases for callers that prefer inspection/selection terminology.
inspect_media_file = validate_media_file
select_assets_for_external_processing = validate_external_selection


__all__ = [
    "DEFAULT_MAX_BYTES",
    "MediaSecurityError",
    "inspect_media_file",
    "select_assets_for_external_processing",
    "validate_external_selection",
    "validate_media_file",
]
