#!/usr/bin/env python3
"""Shared manifest bindings for version-sensitive compatibility operations."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any, Dict, NamedTuple, NoReturn, Optional, Sequence, Tuple, Union

sys.dont_write_bytecode = True

RUNTIME_MAJOR = 3
RUNTIME_MINOR = 9
MANIFEST_LIMIT = 128 * 1024
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
MANIFEST_PATH = SCRIPT_DIRECTORY.parent / "compat" / "agy-version-manifest.json"
VERSION_RE = re.compile(r"\A(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")
SHA256_RE = re.compile(r"\A[0-9a-f]{64}\Z")
SHA512_RE = re.compile(r"\A[0-9a-f]{128}\Z")
COMMIT_RE = re.compile(r"\A[0-9a-f]{40}\Z")
SAFE_NAME_RE = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]{0,199}\Z")
SUPPORT_POLICIES = {
    "current": (
        "activation", "capture", "classifier", "profile", "reprofile",
        "version-evidence",
    ),
    "previous": ("capture", "profile", "version-evidence"),
    "historical": (),
}


class EngineError(ValueError):
    """The manifest or a derived operation binding is invalid."""


class VersionSpec(NamedTuple):
    version: str
    support_tier: str
    allowed_operations: Tuple[str, ...]
    expected_stdout: bytes
    source_sha256: str
    source_size: int
    release_commit: str
    distribution_url: str
    distribution_sha512: str
    recovery_binding_sha256: str
    recovery_stdout: bytes
    recovery_runner_sha256: str
    recovery_runner_bytes: int
    recovery_summary_bytes: int
    output_profile_name: str
    prior_name: str
    historical_recovery_binding_sha256: Optional[str] = None
    historical_recovery_source_sha256: Optional[str] = None
    reprofile_output_name: Optional[str] = None
    failure_ruleset_version: Optional[str] = None
    capture_runner_source_sha256: Optional[str] = None
    capture_record_sha256: Optional[str] = None
    capture_stdout_sha256: Optional[str] = None
    capture_response_sha256: Optional[str] = None
    inventory_normalized_sha256: Optional[str] = None
    slug_count: Optional[int] = None
    slugs: Optional[Tuple[str, ...]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VersionSpec":
        required = {
            "version", "support_tier", "allowed_operations", "expected_stdout",
            "source_sha256", "source_size",
            "release_commit", "distribution_url", "distribution_sha512",
            "recovery_binding_sha256", "recovery_stdout", "recovery_runner_sha256",
            "recovery_runner_bytes", "recovery_summary_bytes", "output_profile_name",
            "prior_name",
        }
        optional = {
            "historical_recovery_binding_sha256", "historical_recovery_source_sha256",
            "reprofile_output_name", "failure_ruleset_version", "capture_runner_source_sha256", "capture_record_sha256",
            "capture_stdout_sha256", "capture_response_sha256",
            "inventory_normalized_sha256", "slug_count", "slugs",
        }
        if set(data) - required - optional or required - set(data):
            raise EngineError("version record keys do not match the closed schema")
        version = _text(data["version"], "version")
        if not VERSION_RE.fullmatch(version):
            raise EngineError("invalid version")
        support_tier = _text(data["support_tier"], "support_tier")
        expected_operations = SUPPORT_POLICIES.get(support_tier)
        if expected_operations is None:
            raise EngineError("invalid support tier")
        raw_operations = data["allowed_operations"]
        if not isinstance(raw_operations, list):
            raise EngineError("allowed_operations must be a list")
        allowed_operations = tuple(
            _safe_name(item, "allowed operation") for item in raw_operations
        )
        if allowed_operations != expected_operations:
            raise EngineError("allowed operations differ from support tier policy")
        slug_count = data.get("slug_count")
        if slug_count is not None:
            slug_count = _positive_int(slug_count, "slug_count")
        raw_slugs = data.get("slugs")
        slugs: Optional[Tuple[str, ...]] = None
        if raw_slugs is not None:
            if not isinstance(raw_slugs, list) or not raw_slugs or len(raw_slugs) > 1_000:
                raise EngineError("slugs must be a bounded non-empty list")
            slugs = tuple(_safe_name(item, "slug") for item in raw_slugs)
            if len(set(slugs)) != len(slugs) or tuple(sorted(slugs)) != slugs:
                raise EngineError("slugs must be unique and sorted")
            if slug_count != len(slugs):
                raise EngineError("slug_count differs from slugs")
        elif slug_count is not None:
            raise EngineError("slug_count requires slugs")
        return cls(
            version=version,
            support_tier=support_tier,
            allowed_operations=allowed_operations,
            expected_stdout=_ascii(data["expected_stdout"], "expected_stdout"),
            source_sha256=_digest(data["source_sha256"], SHA256_RE, "source_sha256"),
            source_size=_positive_int(data["source_size"], "source_size"),
            release_commit=_digest(data["release_commit"], COMMIT_RE, "release_commit"),
            distribution_url=_url(data["distribution_url"]),
            distribution_sha512=_digest(data["distribution_sha512"], SHA512_RE, "distribution_sha512"),
            recovery_binding_sha256=_digest(data["recovery_binding_sha256"], SHA256_RE, "recovery_binding_sha256"),
            recovery_stdout=_ascii(data["recovery_stdout"], "recovery_stdout"),
            recovery_runner_sha256=_digest(data["recovery_runner_sha256"], SHA256_RE, "recovery_runner_sha256"),
            recovery_runner_bytes=_positive_int(data["recovery_runner_bytes"], "recovery_runner_bytes"),
            recovery_summary_bytes=_positive_int(data["recovery_summary_bytes"], "recovery_summary_bytes"),
            output_profile_name=_safe_name(data["output_profile_name"], "output_profile_name"),
            prior_name=_safe_name(data["prior_name"], "prior_name"),
            historical_recovery_binding_sha256=_optional_digest(data.get("historical_recovery_binding_sha256"), "historical_recovery_binding_sha256"),
            historical_recovery_source_sha256=_optional_digest(data.get("historical_recovery_source_sha256"), "historical_recovery_source_sha256"),
            reprofile_output_name=_optional_name(data.get("reprofile_output_name"), "reprofile_output_name"),
            failure_ruleset_version=_optional_name(data.get("failure_ruleset_version"), "failure_ruleset_version"),
            capture_runner_source_sha256=_optional_digest(data.get("capture_runner_source_sha256"), "capture_runner_source_sha256"),
            capture_record_sha256=_optional_digest(data.get("capture_record_sha256"), "capture_record_sha256"),
            capture_stdout_sha256=_optional_digest(data.get("capture_stdout_sha256"), "capture_stdout_sha256"),
            capture_response_sha256=_optional_digest(data.get("capture_response_sha256"), "capture_response_sha256"),
            inventory_normalized_sha256=_optional_digest(data.get("inventory_normalized_sha256"), "inventory_normalized_sha256"),
            slug_count=slug_count,
            slugs=slugs,
        )

    def as_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "version": self.version,
            "support_tier": self.support_tier,
            "allowed_operations": list(self.allowed_operations),
            "expected_stdout": self.expected_stdout.decode("ascii"),
            "source_sha256": self.source_sha256,
            "source_size": self.source_size,
            "release_commit": self.release_commit,
            "distribution_url": self.distribution_url,
            "distribution_sha512": self.distribution_sha512,
            "recovery_binding_sha256": self.recovery_binding_sha256,
            "recovery_stdout": self.recovery_stdout.decode("ascii"),
            "recovery_runner_sha256": self.recovery_runner_sha256,
            "recovery_runner_bytes": self.recovery_runner_bytes,
            "recovery_summary_bytes": self.recovery_summary_bytes,
            "output_profile_name": self.output_profile_name,
            "prior_name": self.prior_name,
        }
        for key in (
            "historical_recovery_binding_sha256", "historical_recovery_source_sha256",
            "reprofile_output_name", "failure_ruleset_version", "capture_runner_source_sha256", "capture_record_sha256",
            "capture_stdout_sha256", "capture_response_sha256",
            "inventory_normalized_sha256", "slug_count", "slugs",
        ):
            value = getattr(self, key)
            if value is not None:
                result[key] = list(value) if key == "slugs" else value
        return result


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 2_000:
        raise EngineError(f"invalid {label}")
    return value


def _ascii(value: object, label: str) -> bytes:
    try:
        return _text(value, label).encode("ascii")
    except UnicodeEncodeError as exc:
        raise EngineError(f"invalid {label}") from exc


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise EngineError(f"invalid {label}")
    return value


def _digest(value: object, pattern: re.Pattern[str], label: str) -> str:
    text = _text(value, label)
    if not pattern.fullmatch(text):
        raise EngineError(f"invalid {label}")
    return text


def _optional_digest(value: object, label: str) -> Optional[str]:
    return None if value is None else _digest(value, SHA256_RE, label)


def _safe_name(value: object, label: str) -> str:
    text = _text(value, label)
    if not SAFE_NAME_RE.fullmatch(text) or text in {".", ".."}:
        raise EngineError(f"invalid {label}")
    return text


def _optional_name(value: object, label: str) -> Optional[str]:
    return None if value is None else _safe_name(value, label)


def _url(value: object) -> str:
    text = _text(value, "distribution_url")
    if not text.startswith("https://") or any(char.isspace() for char in text):
        raise EngineError("invalid distribution_url")
    return text


def _read_regular(path: Path, limit: int) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(os.fspath(path), flags)
    except OSError as exc:
        raise EngineError("manifest artifact is unavailable") from exc
    try:
        identity = os.fstat(descriptor)
        if not stat.S_ISREG(identity.st_mode) or not 0 < identity.st_size <= limit:
            raise EngineError("manifest artifact is not a bounded regular file")
        data = b""
        while len(data) <= limit:
            chunk = os.read(descriptor, min(65_536, limit + 1 - len(data)))
            if not chunk:
                break
            data += chunk
        if len(data) != identity.st_size:
            raise EngineError("manifest artifact changed during read")
        return data
    finally:
        os.close(descriptor)


def find_manifest_path(explicit: Optional[Union[Path, str]] = None) -> Path:
    return Path(explicit) if explicit is not None else MANIFEST_PATH


def _reject_duplicate_keys(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EngineError("duplicate manifest key")
        result[key] = value
    return result


def load_manifest(manifest_path: Optional[Union[Path, str]] = None) -> Dict[str, VersionSpec]:
    path = find_manifest_path(manifest_path)
    raw = _read_regular(path, MANIFEST_LIMIT)
    expected = _read_regular(path.with_suffix(".sha256"), 256).decode("ascii").strip()
    if not SHA256_RE.fullmatch(expected) or hashlib.sha256(raw).hexdigest() != expected:
        raise EngineError("manifest digest mismatch")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, EngineError) as exc:
        raise EngineError("malformed manifest JSON") from exc
    if not isinstance(data, dict) or set(data) != {"schema_version", "kind", "versions"}:
        raise EngineError("manifest top-level keys do not match the closed schema")
    if data["schema_version"] != 1 or isinstance(data["schema_version"], bool):
        raise EngineError("unsupported manifest schema")
    if data["kind"] != "agy-version-manifest":
        raise EngineError("invalid manifest kind")
    versions = data["versions"]
    if not isinstance(versions, dict) or not versions or len(versions) > 100:
        raise EngineError("versions must be a bounded non-empty object")
    result: Dict[str, VersionSpec] = {}
    for key, value in versions.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            raise EngineError("invalid version record")
        spec = VersionSpec.from_dict(value)
        if key != spec.version:
            raise EngineError("version key mismatch")
        result[key] = spec
    return result


def get_version_spec(version: str, manifest_path: Optional[Union[Path, str]] = None) -> VersionSpec:
    spec = load_manifest(manifest_path).get(version)
    if spec is None:
        raise EngineError("unsupported agy version in manifest")
    return spec


def operation_constants(spec: VersionSpec, operation: str) -> Dict[str, object]:
    """Return the version-varying constants consumed by a stable operation adapter."""
    require_operation(spec, operation)
    common = {
        "EXPECTED_SOURCE_SHA256": spec.source_sha256,
        "EXPECTED_RECOVERY_BINDING_SHA256": spec.recovery_binding_sha256,
        "EXPECTED_RECOVERY_STDOUT": spec.recovery_stdout,
        "EXPECTED_RECOVERY_RUNNER_SHA256": spec.recovery_runner_sha256,
        "EXPECTED_RECOVERY_RUNNER_BYTES": spec.recovery_runner_bytes,
        "EXPECTED_RECOVERY_SUMMARY_BYTES": spec.recovery_summary_bytes,
        "EXPECTED_RELEASE_COMMIT": spec.release_commit,
        "EXPECTED_DISTRIBUTION_URL": spec.distribution_url,
        "EXPECTED_DISTRIBUTION_SHA512": spec.distribution_sha512,
    }
    if operation == "version-evidence":
        return {
            "EXPECTED_VERSION": spec.version, "EXPECTED_STDOUT": spec.expected_stdout,
            "EXPECTED_SOURCE_SHA256": spec.source_sha256, "EXPECTED_SIZE": spec.source_size,
            "EXPECTED_RELEASE_COMMIT": spec.release_commit,
            "EXPECTED_DISTRIBUTION_URL": spec.distribution_url,
            "EXPECTED_DISTRIBUTION_SHA512": spec.distribution_sha512,
            "HISTORICAL_RECOVERY_BINDING_SHA256": spec.historical_recovery_binding_sha256,
            "HISTORICAL_RECOVERY_SOURCE_SHA256": spec.historical_recovery_source_sha256,
        }
    if operation == "profile":
        return dict(common, OUTPUT_NAME=spec.output_profile_name)
    if operation == "capture":
        return dict(common, OUTPUT_PROFILE_NAME=spec.output_profile_name)
    if operation == "classifier":
        if spec.failure_ruleset_version is None:
            raise EngineError("version does not define failure classification")
        if spec.capture_runner_source_sha256 is None:
            raise EngineError("version does not bind the shared capture runner")
        return {
            "EXPECTED_SOURCE_SHA256": spec.source_sha256,
            "EXPECTED_RECOVERY_BINDING_SHA256": spec.recovery_binding_sha256,
            "OUTPUT_PROFILE_NAME": spec.output_profile_name,
            "RULESET_VERSION": spec.failure_ruleset_version,
            "EXPECTED_RUNNER_SHA256": spec.capture_runner_source_sha256,
        }
    if operation == "reprofile":
        if spec.reprofile_output_name is None:
            raise EngineError("version does not define reprofile output")
        return {"OUTPUT_NAME": spec.reprofile_output_name}
    raise EngineError("unknown version operation")


def require_operation(spec: VersionSpec, operation: str) -> None:
    """Fail closed unless the digest-bound support policy allows an operation."""
    if operation not in SUPPORT_POLICIES[spec.support_tier]:
        raise EngineError(
            f"{operation} is not allowed for {spec.support_tier} version {spec.version}"
        )


def validate_activation_binding(binding: Dict[str, Any], spec: VersionSpec) -> None:
    require_operation(spec, "activation")
    required = {
        "agy_version": spec.version,
        "reviewed_source_revision": spec.release_commit,
        "source_sha256": spec.source_sha256,
        "version_binding_sha256": spec.recovery_binding_sha256,
        "capture_record_sha256": spec.capture_record_sha256,
        "capture_stdout_sha256": spec.capture_stdout_sha256,
        "capture_response_sha256": spec.capture_response_sha256,
        "inventory_normalized_sha256": spec.inventory_normalized_sha256,
    }
    if any(expected is None or binding.get(key) != expected for key, expected in required.items()):
        raise EngineError("activation binding differs from version manifest")
    if spec.slugs is None or binding.get("slugs") != list(spec.slugs):
        raise EngineError("activation slugs differ from version manifest")


def verify_reprofile_transition(prior: Dict[str, Any], current: os.stat_result) -> None:
    identity = prior.get("account_home_identity")
    if not isinstance(identity, dict):
        raise EngineError("prior profile lacks account identity")
    observed = {
        "dev": current.st_dev, "gid": current.st_gid, "ino": current.st_ino,
        "mode": stat.S_IMODE(current.st_mode), "uid": current.st_uid,
    }
    if any(identity.get(key) != value for key, value in observed.items()):
        raise EngineError("stable account identity changed")
    if observed["mode"] != 0o700 or observed["uid"] != os.getuid():
        raise EngineError("account home is not owner-private")


def _runtime_supported() -> bool:
    return (
        sys.implementation.name == "cpython" and sys.version_info[:2] == (RUNTIME_MAJOR, RUNTIME_MINOR)
        and sys.flags.isolated == 1 and sys.flags.no_site == 1
        and sys.flags.dont_write_bytecode == 1 and sys.flags.ignore_environment == 1
    )


def _atomic_exit(code: int, message: bytes) -> NoReturn:
    try:
        os.write(sys.stderr.buffer.fileno(), message)
    except OSError:
        pass
    os._exit(code)


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"


def main(argv: Optional[Sequence[str]] = None) -> NoReturn:
    if not _runtime_supported():
        _atomic_exit(2, b"version manifest engine: rejected runtime\n")
    args = list(argv if argv is not None else sys.argv[1:])
    try:
        if args and args[0] == "--audit-manifest" and len(args) <= 2:
            manifest = load_manifest(args[1] if len(args) == 2 else None)
            sys.stdout.write(f"manifest valid: {len(manifest)} versions loaded\n")
            raise SystemExit(0)
        if len(args) == 2 and args[0] == "--get-version-spec":
            sys.stdout.buffer.write(_canonical_json(get_version_spec(args[1]).as_dict()))
            raise SystemExit(0)
        _atomic_exit(64, b"usage: version_manifest_engine.py --audit-manifest [PATH] | --get-version-spec VERSION\n")
    except EngineError:
        _atomic_exit(2, b"version manifest engine: operation failed closed\n")


if __name__ == "__main__":
    main()
