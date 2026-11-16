"""Private, versioned voice evidence storage. Standard library; no model or network I/O.

All editing functions return fresh values. Evidence stays local, and an acceptance
signal is never promoted to an authored sample. Only the two persistence helpers
touch the filesystem.
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

from voice_context import DESTINATIONS, validate_context_preferences, validate_voice_traits


SCHEMA_VERSION = 1
MAX_STORE_BYTES = 10 * 1024 * 1024
MAX_HISTORY = 32
MAX_RECORDS = 10_000
MAX_TEXT_CHARS = 2_000_000
MAX_REVISION = 2**63 - 1
MAX_SYSTEM_LINKS = 8
_STORE_FIELDS = {
    "schema_version", "name", "revision", "learning_enabled", "samples", "feedback",
    "profiles", "history", "profile_version", "pending_evidence_ids",
}
_REQUIRED_FIELDS = _STORE_FIELDS - {"profile_version", "pending_evidence_ids"}
_KINDS = {"preference", "revision", "accept", "reject"}


def _string(value, label: str, limit: int, *, blank: bool = False) -> str:
    if not isinstance(value, str) or len(value) > limit or (not blank and not value.strip()):
        qualifier = "" if blank else "nonempty "
        raise ValueError(f"{label} must be a {qualifier}string of at most {limit:,} characters.")
    return value


def _integer(value, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or not minimum <= value <= MAX_REVISION:
        raise ValueError(f"{label} must be an integer between {minimum} and {MAX_REVISION}.")
    return value


def _destination(value) -> str:
    if not isinstance(value, str) or value not in DESTINATIONS:
        raise ValueError("Use a canonical destination: " + ", ".join(DESTINATIONS) + ".")
    return value


def _normal(value: str) -> str:
    return " ".join(value.split()).casefold()


def _strings(values, label: str, count: int, size: int) -> list[str]:
    if not isinstance(values, list) or len(values) > count:
        raise ValueError(f"{label} must be a list of at most {count:,} strings.")
    return [_string(value, label, size) for value in values]


def _contradictions(prefer: list[str], avoid: list[str]) -> None:
    if {_normal(value) for value in prefer} & {_normal(value) for value in avoid}:
        raise ValueError("The same item cannot be preferred and avoided in one update.")


def _preferences(values, label: str, count: int, size: int) -> list[str]:
    checked = _strings([] if values is None else values, label, count, size)
    result, seen = [], set()
    for value in checked:
        value = value.strip()
        if _normal(value) not in seen:
            result.append(value)
            seen.add(_normal(value))
    return result


def _profile(profile) -> dict:
    """Match legacy profile constraints without importing the CLI or editor."""
    allowed = {"name", "preferences", "avoid", "preserve", "samples", "traits", "contexts"}
    if not isinstance(profile, dict) or set(profile) - allowed:
        raise ValueError("Profile accepts name, preferences, avoid, preserve, samples, traits, and contexts only.")
    if "name" in profile:
        _string(profile["name"], "Profile name", 80, blank=True)
    for key, count, size in (("preferences", 8, 180), ("avoid", 8, 100),
                             ("preserve", 20, 100), ("samples", 2, 500)):
        _strings(profile.get(key, []), key, count, size)
    _contradictions(profile.get("preferences", []), profile.get("avoid", []))
    if "traits" in profile:
        validate_voice_traits(profile["traits"])
    if "contexts" in profile:
        validate_context_preferences(profile["contexts"])
    try:
        length = len(json.dumps(profile, ensure_ascii=False, allow_nan=False))
    except (TypeError, ValueError, RecursionError) as error:
        raise ValueError("A profile must contain JSON data only.") from error
    if length > 6000:
        raise ValueError("Stored profile exceeds 6,000 characters; distill it before committing.")
    return deepcopy(profile)


def _json_bytes(value) -> bytes:
    try:
        payload = (json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False,
                              separators=(",", ":")) + "\n").encode("utf-8")
    except (TypeError, ValueError, RecursionError, UnicodeError) as error:
        raise ValueError("A collection must contain finite, UTF-8 JSON data only.") from error
    if len(payload) > MAX_STORE_BYTES:
        raise ValueError(f"Collection exceeds the {MAX_STORE_BYTES:,}-byte local storage limit.")
    return payload


def _identifier(prefix: str, record: dict) -> str:
    encoded = json.dumps(record, sort_keys=True, ensure_ascii=False, allow_nan=False,
                         separators=(",", ":")).encode("utf-8")
    return prefix + "-" + hashlib.sha256(encoded).hexdigest()


def _sample(text, role, destination, label) -> dict:
    _string(text, "Sample text", MAX_TEXT_CHARS)
    if role not in ("authored", "reference"):
        raise ValueError("Sample role must be authored or reference.")
    _destination(destination)
    _string(label, "Sample label", 200, blank=True)
    try:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        body = {"sha256": digest, "text": text, "role": role,
                "destination": destination, "label": label}
        return {"id": _identifier("sample", body), **body}
    except UnicodeError as error:
        raise ValueError("Sample text must be valid UTF-8.") from error


def _feedback(*, kind, destination, reason, prefer, avoid, draft, final, occurrence=None) -> dict:
    if not isinstance(kind, str) or kind not in _KINDS:
        raise ValueError("Feedback kind must be preference, revision, accept, or reject.")
    _destination(destination)
    _string(reason, "Feedback reason", 2000, blank=True)
    preferred = _preferences(prefer, "prefer", 8, 180)
    avoided = _preferences(avoid, "avoid", 8, 100)
    _contradictions(preferred, avoided)
    _string(draft, "Feedback draft", MAX_TEXT_CHARS, blank=True)
    _string(final, "Feedback final", MAX_TEXT_CHARS, blank=True)
    if kind == "preference" and not (preferred or avoided or reason.strip()):
        raise ValueError("Preference feedback needs explicit prefer/avoid items or an author reason.")
    if kind == "revision" and (not draft.strip() or not final.strip() or draft.strip() == final.strip()):
        raise ValueError("Revision feedback needs a draft and distinct, nonempty final author text.")
    body = {"kind": kind, "destination": destination, "reason": reason.strip(),
            "prefer": preferred, "avoid": avoided}
    if draft:
        body["draft"] = draft
    if final:
        body["final"] = final
    if occurrence is not None:
        body["occurrence"] = _integer(occurrence, "Feedback occurrence", minimum=2)
    try:
        return {"id": _identifier("feedback", body), **body}
    except UnicodeError as error:
        raise ValueError("Feedback text must be valid UTF-8.") from error


def _feedback_body(record: dict) -> dict:
    return {key: value for key, value in record.items() if key not in {"id", "occurrence"}}


def _feedback_scopes(record: dict) -> set[str]:
    scopes = set()
    if (record["kind"] in {"preference", "revision"}
            or record["reason"] or record["prefer"] or record["avoid"]):
        scopes.add("author-guidance")
    if record["kind"] in {"accept", "reject"}:
        scopes.add("assessment")
    return scopes


def _ids(values, known: set[str], label: str) -> list[str]:
    checked = _strings(values, label, 2 * MAX_RECORDS, 80)
    if len(checked) != len(set(checked)) or set(checked) - known:
        raise ValueError(f"{label} must contain unique IDs of existing evidence.")
    return checked


def _entries(entries, known: set[str], maximum_version: int) -> dict:
    if not isinstance(entries, dict) or any(key not in DESTINATIONS for key in entries):
        raise ValueError("profiles must map canonical destinations to profile entries.")
    for entry in entries.values():
        required = {"profile", "evidence_ids", "version"}
        if (not isinstance(entry, dict) or required - set(entry)
                or set(entry) - (required | {"reviewed_evidence_ids"})):
            raise ValueError("Each profile entry requires profile, evidence_ids, and version; reviewed_evidence_ids is optional.")
        _profile(entry["profile"])
        provenance = _ids(entry["evidence_ids"], known, "Profile evidence_ids")
        if "reviewed_evidence_ids" in entry:
            reviewed = _ids(entry["reviewed_evidence_ids"], known, "Profile reviewed_evidence_ids")
            if set(reviewed) - set(provenance):
                raise ValueError("Profile reviewed_evidence_ids must be a subset of evidence_ids.")
        _integer(entry["version"], "Profile version", minimum=1)
        if entry["version"] > maximum_version:
            raise ValueError("Profile version exceeds the collection profile_version.")
    return entries


def _all_ids(store: dict) -> list[str]:
    return [record["id"] for key in ("samples", "feedback") for record in store[key]]


def _covered(profiles: dict) -> set[str]:
    return {value for entry in profiles.values() for value in entry["evidence_ids"]}


def _reviewed(profiles: dict) -> set[str]:
    return {value for entry in profiles.values()
            for value in entry.get("reviewed_evidence_ids", entry["evidence_ids"])}


def _pending(store: dict) -> list[str]:
    covered = _reviewed(store["profiles"])
    return [value for value in _all_ids(store) if value not in covered]


def create_collection(name, learning_enabled=False) -> dict:
    """Create an empty collection; continuing learning is disabled by default."""
    _string(name, "Collection name", 80)
    if type(learning_enabled) is not bool:
        raise ValueError("learning_enabled must be a boolean.")
    return validate_collection({"schema_version": SCHEMA_VERSION, "name": name.strip(), "revision": 0,
                                "learning_enabled": learning_enabled, "samples": [], "feedback": [],
                                "profiles": {}, "history": [], "profile_version": 0,
                                "pending_evidence_ids": []})


def validate_collection(store) -> dict:
    """Validate bounded JSON and provenance, returning a detached canonical copy."""
    if not isinstance(store, dict) or set(store) - _STORE_FIELDS or _REQUIRED_FIELDS - set(store):
        raise ValueError("Collection has missing or unsupported fields.")
    _json_bytes(store)  # Bound the entire input before copying or traversing it.
    checked = deepcopy(store)
    if type(checked["schema_version"]) is not int or checked["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Unsupported collection schema_version.")
    _string(checked["name"], "Collection name", 80)
    revision = _integer(checked["revision"], "Collection revision")
    if type(checked["learning_enabled"]) is not bool:
        raise ValueError("learning_enabled must be a boolean.")
    known = set()
    for key in ("samples", "feedback"):
        records = checked[key]
        if not isinstance(records, list) or len(records) > MAX_RECORDS:
            raise ValueError(f"{key} must be a list of at most {MAX_RECORDS:,} records.")
        for record in records:
            if not isinstance(record, dict):
                raise ValueError(f"Each {key} entry must be an object.")
            if key == "samples":
                if set(record) != {"id", "sha256", "text", "role", "destination", "label"}:
                    raise ValueError("Sample has missing or unsupported fields.")
                expected = _sample(record["text"], record["role"], record["destination"], record["label"])
            else:
                required = {"id", "kind", "destination", "reason", "prefer", "avoid"}
                if required - set(record) or set(record) - (required | {"draft", "final", "occurrence"}):
                    raise ValueError("Feedback has missing or unsupported fields.")
                expected = _feedback(**{field: record.get(field, "") for field in
                                       ("kind", "destination", "reason", "prefer", "avoid", "draft", "final")},
                                     occurrence=record.get("occurrence"))
            if record != expected or record["id"] in known:
                raise ValueError("Evidence IDs/content are inconsistent or duplicated.")
            known.add(record["id"])
    history = checked["history"]
    if not isinstance(history, list) or len(history) > MAX_HISTORY:
        raise ValueError(f"history must contain at most {MAX_HISTORY} snapshots.")
    if not isinstance(checked["profiles"], dict):
        raise ValueError("profiles must be an object.")
    # The two bookkeeping fields are optional on a schema-v1 import.
    versions = [entry.get("version", 0) for entry in checked["profiles"].values() if isinstance(entry, dict)]
    versions += [entry.get("version", 0) for entry in history if isinstance(entry, dict)]
    for version in versions:
        _integer(version, "Profile version", minimum=1)
    checked.setdefault("profile_version", max(versions, default=0))
    profile_version = _integer(checked["profile_version"], "Collection profile_version")
    if profile_version > revision:
        raise ValueError("profile_version cannot exceed collection revision.")
    _entries(checked["profiles"], known, profile_version)
    previous = 0
    for snapshot in history:
        if not isinstance(snapshot, dict) or set(snapshot) != {"version", "profiles", "evidence_ids", "action"}:
            raise ValueError("History snapshots require version, profiles, evidence_ids, and action.")
        version = _integer(snapshot["version"], "Snapshot version", minimum=1)
        if version <= previous or version > profile_version:
            raise ValueError("History versions must increase and not exceed profile_version.")
        previous = version
        if snapshot["action"] not in ("commit", "rollback"):
            raise ValueError("Unknown profile history action.")
        _entries(snapshot["profiles"], known, version)
        provenance = _ids(snapshot["evidence_ids"], known, "Snapshot evidence_ids")
        if set(provenance) != _covered(snapshot["profiles"]):
            raise ValueError("Snapshot provenance must match its profiles.")
    checked.setdefault("pending_evidence_ids", _pending(checked))
    pending = _ids(checked["pending_evidence_ids"], known, "pending_evidence_ids")
    if set(pending) != set(_pending(checked)):
        raise ValueError("pending_evidence_ids must identify evidence not reviewed by active profiles.")
    _json_bytes(checked)
    return checked


def _finish(store: dict) -> dict:
    if store["revision"] == MAX_REVISION:
        raise ValueError("Collection revision limit reached.")
    store["revision"] += 1
    store["pending_evidence_ids"] = _pending(store)
    return validate_collection(store)


def add_sample(store, text, *, role="authored", destination="general", label="") -> dict:
    checked = validate_collection(store)
    record = _sample(text, role, destination, label)
    if any(existing["id"] == record["id"] for existing in checked["samples"]):
        return checked
    checked["samples"].append(record)
    return _finish(checked)


def add_feedback(store, *, kind, destination="general", reason="", prefer=None, avoid=None,
                 draft="", final="", automatic=False) -> dict:
    """Append an author event; deduplicate only the latest relevant repeated event.

    A recurrence after intervening guidance/assessment receives a deterministic
    occurrence number and new ID, so a preference reversal is never lost merely
    because the writer previously expressed the same preference.
    """
    checked = validate_collection(store)
    if type(automatic) is not bool:
        raise ValueError("automatic must be a boolean.")
    if automatic and not checked["learning_enabled"]:
        raise ValueError("Automatic feedback requires continuing learning to be enabled explicitly.")
    record = _feedback(kind=kind, destination=destination, reason=reason, prefer=prefer,
                       avoid=avoid, draft=draft, final=final)
    body, scopes = _feedback_body(record), _feedback_scopes(record)
    latest = next((existing for existing in reversed(checked["feedback"])
                   if existing["destination"] == destination and _feedback_scopes(existing) & scopes), None)
    if latest is not None and _feedback_body(latest) == body:
        return checked
    occurrences = [existing.get("occurrence", 1) for existing in checked["feedback"]
                   if _feedback_body(existing) == body]
    if occurrences:
        record = _feedback(**{field: record.get(field, "") for field in
                              ("kind", "destination", "reason", "prefer", "avoid", "draft", "final")},
                           occurrence=max(occurrences) + 1)
    checked["feedback"].append(record)
    return _finish(checked)


def set_learning(store, enabled) -> dict:
    checked = validate_collection(store)
    if type(enabled) is not bool:
        raise ValueError("Learning consent must be a boolean.")
    if checked["learning_enabled"] == enabled:
        return checked
    checked["learning_enabled"] = enabled
    return _finish(checked)


def _snapshot(store: dict, action: str) -> None:
    if store["profile_version"] == MAX_REVISION:
        raise ValueError("Profile version limit reached.")
    store["profile_version"] += 1
    store["history"].append({"version": store["profile_version"],
                             "profiles": deepcopy(store["profiles"]),
                             "evidence_ids": sorted(_covered(store["profiles"])), "action": action})
    store["history"] = store["history"][-MAX_HISTORY:]


def commit_profile(store, destination, profile, evidence_ids, *, expected_revision,
                   reviewed_evidence_ids=None) -> dict:
    """Commit a card with transitive provenance and exact target review coverage.

    Older callers omit ``reviewed_evidence_ids`` and thereby mark their supplied
    evidence as reviewed. Inherited provenance can instead be included only in
    ``evidence_ids``, leaving uninspected evidence pending for an actual review.
    """
    checked = validate_collection(store)
    _destination(destination)
    _integer(expected_revision, "expected_revision")
    if expected_revision != checked["revision"]:
        raise ValueError("Stale collection revision; build learning from the current collection.")
    profile = _profile(profile)
    provenance = sorted(_ids(evidence_ids, set(_all_ids(checked)), "evidence_ids"))
    reviewed = provenance if reviewed_evidence_ids is None else sorted(
        _ids(reviewed_evidence_ids, set(provenance), "reviewed_evidence_ids"))
    current = checked["profiles"].get(destination)
    if (current and current["profile"] == profile and sorted(current["evidence_ids"]) == provenance
            and sorted(current.get("reviewed_evidence_ids", current["evidence_ids"])) == reviewed):
        return checked
    checked["profiles"][destination] = {"profile": profile, "evidence_ids": provenance,
                                         "reviewed_evidence_ids": list(reviewed),
                                         "version": checked["profile_version"] + 1}
    _snapshot(checked, "commit")
    return _finish(checked)


def rollback_profile(store, version) -> dict:
    """Restore a bounded profile snapshot, preserving evidence and learning consent."""
    checked = validate_collection(store)
    _integer(version, "Rollback version", minimum=1)
    snapshot = next((item for item in checked["history"] if item["version"] == version), None)
    if snapshot is None:
        raise ValueError("Profile version is unavailable or has been forgotten.")
    if checked["profiles"] == snapshot["profiles"]:
        return checked
    checked["profiles"] = deepcopy(snapshot["profiles"])
    _snapshot(checked, "rollback")
    return _finish(checked)


def forget_evidence(store, evidence_id) -> dict:
    """Purge one record and every inferred card/snapshot that could retain its text."""
    checked = validate_collection(store)
    _string(evidence_id, "Evidence ID", 80)
    if evidence_id not in set(_all_ids(checked)):
        return checked
    for key in ("samples", "feedback"):
        checked[key] = [record for record in checked[key] if record["id"] != evidence_id]
    checked["profiles"] = {}
    checked["history"] = []
    if checked["profile_version"] == MAX_REVISION:
        raise ValueError("Profile version limit reached.")
    checked["profile_version"] += 1
    return _finish(checked)


def _target(path) -> Path:
    try:
        target = Path(os.path.abspath(Path(path).expanduser()))
    except (TypeError, ValueError, OSError) as error:
        raise ValueError("Collection path must name a local file.") from error
    if not target.name:
        raise ValueError("Collection path must name a local file.")
    return target


def _parents(target: Path, *, create: bool = False) -> None:
    # Walk the physical path one component at a time. Root-owned links are system
    # layout (/var on macOS, /home on Fedora Atomic) and are followed, with every
    # component of their destination vetted the same way; any other link is refused.
    current = Path(target.anchor)
    pending = list(reversed(target.parent.parts[1:]))
    followed = 0
    while pending:
        part = pending.pop()
        if part == "..":
            current = current.parent
            continue
        component = current / part
        try:
            metadata = component.lstat()
        except FileNotFoundError:
            if not create:
                raise
            try:
                component.mkdir(mode=0o700)
            except FileExistsError:
                pass
            metadata = component.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            followed += 1
            if os.name != "posix" or metadata.st_uid != 0 or followed > MAX_SYSTEM_LINKS:
                raise ValueError("Collection paths must not contain symlinks.")
            destination = Path(os.readlink(component))
            if destination.is_absolute():
                current = Path(destination.anchor)
            pending.extend(reversed(destination.parts[1:] if destination.is_absolute() else destination.parts))
            continue
        if not stat.S_ISDIR(metadata.st_mode):
            raise ValueError("Collection parent must be a directory.")
        current = component


def _private(metadata) -> None:
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError("Use a regular collection file, not a symlink or special file.")
    if os.name == "posix":
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise ValueError("Collection permissions must be private (0600); group/other access is refused.")
        if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
            raise ValueError("Collection must belong to the current user.")


@contextmanager
def _parent_lock(target: Path):
    """Serialize this module's writers where POSIX directory locks are available."""
    descriptor = None
    locking = None
    if os.name == "posix":
        try:
            import fcntl
            locking = fcntl
        except ImportError:  # The JSON APIs remain usable on other Python platforms.
            pass
    try:
        if locking is not None:
            descriptor = os.open(target.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                                 | getattr(os, "O_NOFOLLOW", 0))
            locking.flock(descriptor, locking.LOCK_EX)
        yield
    finally:
        if descriptor is not None:
            try:
                locking.flock(descriptor, locking.LOCK_UN)
            finally:
                os.close(descriptor)


def _read_private(target: Path) -> tuple[bytes, os.stat_result]:
    _parents(target)
    if target.is_symlink():
        raise ValueError("Use a regular collection file, not a symlink.")
    _private(target.lstat())
    flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
             | getattr(os, "O_BINARY", 0))
    descriptor = os.open(target, flags)
    with os.fdopen(descriptor, "rb") as source:
        metadata = os.fstat(source.fileno())
        _private(metadata)
        if metadata.st_size > MAX_STORE_BYTES:
            raise ValueError(f"Collection exceeds the {MAX_STORE_BYTES:,}-byte local storage limit.")
        payload = source.read(MAX_STORE_BYTES + 1)
    if len(payload) > MAX_STORE_BYTES:
        raise ValueError(f"Collection exceeds the {MAX_STORE_BYTES:,}-byte local storage limit.")
    return payload, metadata


def _unique_object(pairs) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Collection JSON contains duplicate object keys.")
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError("Nonfinite JSON value: " + value)


def _decode(payload: bytes) -> dict:
    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique_object,
                           parse_constant=_nonfinite)
    except (UnicodeError, ValueError, RecursionError) as error:
        raise ValueError("Collection must contain valid, bounded UTF-8 JSON.") from error
    return validate_collection(value)


def load_collection(path) -> dict:
    """Read a bounded, owner-private regular file without following symlinks."""
    payload, _ = _read_private(_target(path))
    return _decode(payload)


def save_collection(path, store, create=False, *, expected_revision=None) -> Path:
    """Atomically persist a collection with private permissions and stale-write checks.

    ``create=True`` never overwrites an existing path. Updates require an existing
    valid private collection and its loaded ``expected_revision``. That revision
    must still match disk, even when the proposed value has a higher revision.
    Lower revisions and conflicting equal revisions are also refused. This does
    not mutate ``store`` or silently enable continuing learning.
    """
    if type(create) is not bool:
        raise ValueError("create must be a boolean.")
    checked = validate_collection(store)
    payload = _json_bytes(checked)
    target = _target(path)
    _parents(target, create=create)
    temporary = None
    with _parent_lock(target):
        if target.is_symlink():
            raise ValueError("Use a regular collection file, not a symlink.")
        original = None
        if create:
            if target.exists():
                raise FileExistsError(f"Collection already exists: {target}")
        else:
            original, metadata = _read_private(target)
            previous = _decode(original)
            if expected_revision is None:
                raise ValueError("Saving an existing collection requires expected_revision from the loaded collection.")
            _integer(expected_revision, "expected_revision")
            if previous["revision"] != expected_revision:
                raise ValueError("Stale collection ancestry; expected_revision no longer matches disk. Reload before saving.")
            if previous["revision"] > checked["revision"] or (
                    previous["revision"] == checked["revision"] and previous != checked):
                raise ValueError("Stale or conflicting collection revision; reload before saving.")
            if previous == checked:
                return target
        try:
            descriptor, name = tempfile.mkstemp(prefix=".voice-store-", dir=target.parent)
            temporary = Path(name)
            with os.fdopen(descriptor, "wb") as output:
                if os.name == "posix" and hasattr(os, "fchmod"):
                    os.fchmod(output.fileno(), 0o600)
                output.write(payload)
                output.flush()
                os.fsync(output.fileno())
            _parents(target)
            if target.is_symlink():
                raise ValueError("Use a regular collection file, not a symlink.")
            if create:
                # A hard link publishes a complete file atomically with O_EXCL-like
                # collision handling; both paths are on the same filesystem.
                os.link(temporary, target)
            else:
                current, current_metadata = _read_private(target)
                if current != original or (current_metadata.st_dev, current_metadata.st_ino) != (
                        metadata.st_dev, metadata.st_ino):
                    raise ValueError("Collection changed while saving; reload before saving.")
                os.replace(temporary, target)
            if os.name == "posix":
                directory = os.open(target.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                                    | getattr(os, "O_NOFOLLOW", 0))
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
        finally:
            if temporary is not None:
                try:
                    temporary.unlink()
                except FileNotFoundError:
                    pass
    return target
