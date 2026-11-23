"""Create, snapshot, update and verify independent local Jianying drafts."""

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path


CONTENT = "draft_content.json"
MIRROR = "template-2.tmp"
PROJECT = Path("Timelines/project.json")
META = Path("draft_meta_info.json")
PROJECT_BACKUP = Path("Timelines/project.json.bak")


class DraftError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise DraftError(message)


def load(path):
    return json.loads(path.read_bytes())


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def atomic(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".jianying-", delete=False) as stream:
        tmp = Path(stream.name)
        try:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            stream.close()
            tmp.unlink(missing_ok=True)
            raise
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def child_file(root, relative):
    path = root / relative
    require(path.resolve() == path and path.is_file(), f"Missing file or redirected path: {path}")
    return path


def safe_id(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}", value),
            f"Invalid project or timeline ID: {value!r}")
    return value


def rows(index):
    entries = load(index).get("all_draft_store")
    require(isinstance(entries, list), f"Unsupported draft index: {index}")
    return [row for row in entries if isinstance(row, dict) and row.get("draft_name")]


def describe(entry):
    name = entry["draft_name"]
    raw = Path(entry["draft_fold_path"])
    require(raw.is_absolute(), f"Draft path must be absolute: {raw}")
    root = raw.resolve(strict=True)
    require(root.is_dir(), f"Missing draft folder: {root}")
    project = load(child_file(root, PROJECT))
    timelines = project.get("timelines")
    require(isinstance(timelines, list) and timelines, f"No timeline index at {root / PROJECT}")
    ids = [safe_id(row["id"]) for row in timelines]
    require(len(set(i.casefold() for i in ids)) == len(ids), f"Repeated timeline IDs in {name}")
    main = project.get("main_timeline_id")
    require(main in ids, f"Unknown main timeline in {name}: {main!r}")
    return dict(name=name, path=str(root), draft_id=safe_id(entry["draft_id"]),
                project_id=safe_id(project["id"]), main=main,
                timelines=[dict(name=str(row["name"]), id=tid) for row, tid in zip(timelines, ids)])


def named(entries, name):
    found = [row for row in entries if row["draft_name"] == name]
    require(len(found) == 1, f"Expected one registered draft named {name!r}, found {len(found)}")
    return describe(found[0])


def identities(index, source, copy):
    require(source != copy, "Source and copy names must differ")
    entries = rows(index)
    b = named(entries, copy)
    if source is None:
        return None, b
    a = named(entries, source)
    roots = Path(a["path"]), Path(b["path"])
    require(not any(x.is_relative_to(y) for x, y in (roots, roots[::-1])),
            "Source and copy must have independent directories")
    for key in ("draft_id", "project_id"):
        require(a[key].casefold() != b[key].casefold(), f"Source and copy share {key}")
    return a, b


def same_identities(actual, expected):
    source_keys = ("name", "path", "draft_id", "project_id")
    if actual[0] is None or expected[0] is None:
        return actual[0] is expected[0] and actual[1] == expected[1]
    return (all(actual[0][key] == expected[0][key] for key in source_keys)
            and actual[1] == expected[1])


def select(info, names):
    require(len(set(names)) == len(names), "Repeated episode in selection")
    result = []
    for name in names:
        matches = [row for row in info["timelines"] if row["name"] == name]
        require(len(matches) == 1, f"Expected one timeline named {name!r} in {info['name']!r}")
        result.append(matches[0])
    return result


def selected_files(copy, names):
    episodes = select(copy, names)
    return [dict(row, filename=f"{row['id']}.json") for row in episodes]


def unlocked(root):
    require(not os.path.lexists(root / ".locked"), f"Return to Jianying home to close the copy: {root}")


class Codec:
    def __init__(self, args):
        self.exe = Path(args.codec).resolve(strict=True)
        self.runtime = Path(args.runtime).resolve(strict=True)
        require(self.exe.is_file() and self.runtime.is_dir(), "Expected a codec executable and runtime directory")

    def run(self, flag, src, dest):
        require(not os.path.lexists(dest), f"Codec output already exists: {dest}")
        output = subprocess.run([str(self.exe), flag, str(src), "-o", str(dest),
                                 "--jy-dir", str(self.runtime), "-q"],
                                capture_output=True, timeout=60, cwd=dest.parent,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if output.returncode or not dest.is_file():
            details = (output.stdout + output.stderr).decode("utf-8", errors="replace")[-1200:]
            raise DraftError(f"Codec failed for {src.name} ({output.returncode}): {details}")

    def read(self, src, dest, tid):
        doc = self.document(src, dest)
        require(isinstance(doc, dict) and doc.get("id") == tid and isinstance(doc.get("tracks"), list),
                f"Timeline identity or tracks do not match: {src}")
        return doc

    def document(self, src, dest):
        self.run("-dc", src, dest)
        value = load(dest)
        require(isinstance(value, dict), f"Expected an object in {src}")
        return value


def list_drafts(args):
    entries = rows(Path(args.index).resolve(strict=True))
    if args.draft:
        return named(entries, args.draft)
    result = []
    for entry in entries:
        try:
            result.append(describe(entry))
        except (DraftError, OSError, ValueError, KeyError, TypeError) as exc:
            result.append(dict(name=entry["draft_name"], path=entry.get("draft_fold_path"), error=str(exc)))
    return result


def files(episodes):
    """Legacy snapshot file list, retained for already-created workspaces."""
    for row in episodes:
        folder = Path("Timelines") / safe_id(row["id"])
        for name in (CONTENT, MIRROR):
            yield folder / name, row["id"]
    yield PROJECT, None


def records(manifest):
    if "files" in manifest:
        return manifest["files"]
    return [dict(path=path.as_posix(), kind="timeline" if tid else "project", id=tid,
                 prepared=f"{tid}.enc" if tid else "project.json")
            for path, tid in files(manifest["episodes"])]


def layout_files(root, info, episodes):
    result = []

    def add(relative, kind, tid=None):
        child_file(root, relative)
        name = {"metadata": "meta.enc", "project": "project.json",
                "project_backup": "project.previous.json"}.get(kind)
        if kind.startswith("timeline"):
            name = f"{tid}.previous.enc" if kind == "timeline_backup" else f"{tid}.enc"
        result.append(dict(path=relative.as_posix(), kind=kind, id=tid, prepared=name))

    for row in episodes:
        folder = Path("Timelines") / row["id"]
        unknown = [p.name for p in (root / folder).glob("template-*.tmp") if p.name != MIRROR]
        require(not unknown, f"Unknown timeline mirror layout in {folder}: {unknown}")
        add(folder / CONTENT, "timeline", row["id"])
        add(folder / MIRROR, "timeline", row["id"])
        if (root / folder / (CONTENT + ".bak")).exists():
            add(folder / (CONTENT + ".bak"), "timeline_backup", row["id"])
    if any(row["id"] == info["main"] for row in episodes):
        unknown = [p.name for p in root.glob("template-*.tmp") if p.name != MIRROR]
        require(not unknown, f"Unknown main root mirror layout: {unknown}")
        require((root / CONTENT).is_file() and (root / MIRROR).is_file(),
                "Unsupported main root layout: expected draft_content.json and template-2.tmp")
        add(Path(CONTENT), "timeline", info["main"])
        add(Path(MIRROR), "timeline", info["main"])
        if (root / (CONTENT + ".bak")).exists():
            add(Path(CONTENT + ".bak"), "timeline_backup", info["main"])
    if (root / META).exists():
        add(META, "metadata")
    add(PROJECT, "project")
    if (root / PROJECT_BACKUP).exists():
        add(PROJECT_BACKUP, "project_backup")
    return result


def project_identity(doc):
    return doc.get("id"), doc.get("main_timeline_id"), [
        (row.get("id"), str(row.get("name"))) for row in doc.get("timelines", [])]


def metadata_identity(doc, info):
    require(doc.get("draft_id") == info["draft_id"] and doc.get("draft_name") == info["name"],
            f"Metadata identity differs from the registered draft: {info['name']}")
    require(Path(doc.get("draft_fold_path", "")).resolve() == Path(info["path"]),
            f"Metadata folder differs from the registered draft: {info['name']}")


def decode_snapshot(codec, root, baseline, info, episodes, bindings):
    docs = {}
    primary_hashes = {}
    for row in episodes:
        tid = row["id"]
        docs[tid] = codec.read(root / "Timelines" / tid / CONTENT, baseline / row["filename"], tid)
        primary_hashes[tid] = digest(root / "Timelines" / tid / CONTENT)
    project = load(root / PROJECT)
    with tempfile.TemporaryDirectory(prefix="layout-", dir=baseline) as temp:
        scratch = Path(temp)
        for number, item in enumerate(bindings):
            relative = Path(item["path"])
            source = root / relative
            if item["kind"].startswith("timeline"):
                tid = item["id"]
                if relative == Path("Timelines") / tid / CONTENT:
                    continue
                if digest(source) == primary_hashes[tid]:
                    continue
                doc = codec.read(source, scratch / f"{number}.json", tid)
                if item["kind"] == "timeline":
                    require(doc == docs[tid], f"Active mirror differs from its timeline: {relative}")
            elif item["kind"] == "metadata":
                meta = codec.document(source, baseline / "meta.json")
                metadata_identity(meta, info)
            elif item["kind"] == "project_backup":
                require(project_identity(load(source)) == project_identity(project),
                        f"Unknown project backup layout or identity: {relative}")
    return docs


def snapshot_closed(args):
    index = Path(args.index).resolve(strict=True)
    source, copy = identities(index, args.source, args.copy)
    root = Path(copy["path"])
    unlocked(root)
    if source is not None:
        select(source, args.episodes)
    episodes = selected_files(copy, args.episodes)
    bindings = layout_files(root, copy, episodes)
    work = Path(args.workspace).resolve()
    for base in [root, *([Path(source["path"])] if source is not None else [])]:
        require(not work.is_relative_to(base), f"Workspace cannot be inside a draft: {work}")
    codec = Codec(args)
    work.mkdir(parents=True, exist_ok=False)
    baseline = work / "baseline"
    baseline.mkdir()
    checks = {}
    for item in bindings:
        relative = Path(item["path"])
        current = child_file(root, relative)
        saved = work / "backup" / relative
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(current, saved)
        checks[relative.as_posix()] = digest(saved)
    decode_snapshot(codec, work / "backup", baseline, copy, episodes, bindings)
    unlocked(root)
    require(same_identities(identities(index, args.source, args.copy), (source, copy)),
            "Draft registration changed during capture")
    for item in bindings:
        relative = Path(item["path"])
        require(digest(child_file(root, relative)) == checks[relative.as_posix()], f"Live file changed: {relative}")
    manifest = dict(version=2, index=str(index), source=source, copy=copy,
                    episodes=episodes, files=bindings, hashes=checks)
    atomic(work / "snapshot.json", encoded(manifest))
    return dict(workspace=str(work), baseline=str(baseline), episodes=episodes)


def draft_lock_path(info):
    return Path(info["path"]).parent / f".codex-draft-{safe_id(info['draft_id'])}.lock"


def snapshot(args):
    info = named(rows(Path(args.index).resolve(strict=True)), args.copy)
    with file_lock(draft_lock_path(info)):
        return snapshot_closed(args)


def context(args, need_codec=True):
    work = Path(args.workspace).resolve(strict=True)
    manifest = load(child_file(work, Path("snapshot.json")))
    index = Path(manifest["index"])
    recorded_source = manifest["source"]
    source, copy = identities(index, recorded_source["name"] if recorded_source is not None else None,
                              manifest["copy"]["name"])
    require(same_identities((source, copy), (manifest["source"], manifest["copy"])),
            "Draft identity or the copy timeline map changed")
    requested = [row["name"] for row in manifest["episodes"]]
    require(requested and selected_files(copy, requested) == manifest["episodes"], "Snapshot episode selection changed")
    root = Path(copy["path"])
    unlocked(root)
    for item in records(manifest):
        relative = Path(item["path"])
        saved = child_file(work, Path("backup") / relative)
        require(digest(saved) == manifest["hashes"][relative.as_posix()], f"Backup hash changed: {relative}")
    return work, manifest, root, Codec(args) if need_codec else None


def transaction_paths(work, manifest, prepared):
    require(re.fullmatch(r"prepared-[a-f0-9]+", prepared), "Invalid staged transaction name")
    for item in records(manifest):
        relative = Path(item["path"])
        incoming = Path(prepared) / item["prepared"]
        yield relative, child_file(work, Path("backup") / relative), work / incoming


@contextmanager
def transaction_lock(work):
    """Serialize writers using this workspace; the OS releases a dead process's lock."""
    with file_lock(work / "commit.lock"):
        yield


@contextmanager
def file_lock(path):
    require(path.resolve() == path, f"Redirected transaction lock: {path}")
    with path.open("a+b") as stream:
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise DraftError(f"Another local operation holds {path}") from exc
        yield


def restore(work, root, manifest, tx):
    entries = list(transaction_paths(work, manifest, tx["prepared"]))
    for relative, old, new in entries:
        current = digest(child_file(root, relative))
        require(current in (digest(old), tx["hashes"][relative.as_posix()]),
                f"Cannot roll back an external save: {relative}")
    for relative, old, new in reversed(entries):
        unlocked(root)
        current = child_file(root, relative)
        value = digest(current)
        if value == tx["hashes"][relative.as_posix()]:
            atomic(current, old.read_bytes())
        else:
            require(value == digest(old), f"Draft changed during rollback: {relative}")
    tx["status"] = "rolled_back"
    atomic(work / "transaction.json", encoded(tx))


def commit_locked(args, work, manifest, root, codec):
    journal = work / "transaction.json"
    if journal.exists():
        previous = load(child_file(work, journal.name))
        if previous["status"] == "index_pending":
            return finish_commit(work, manifest, root, previous)
        if previous["status"] == "committed":
            raise DraftError("This snapshot already has a committed transaction. Use verify or take a new snapshot.")
        if previous["status"] == "writing":
            restore(work, root, manifest, previous)
        else:
            require(previous["status"] == "rolled_back", "Unknown transaction journal state")
    for item in records(manifest):
        relative = Path(item["path"])
        require(digest(child_file(root, relative)) == manifest["hashes"][relative.as_posix()],
                f"Live file differs from snapshot: {relative}")
    edited = Path(args.edited).resolve(strict=True)
    protected_paths = [root, work / "backup", work / "baseline"]
    if manifest["source"] is not None:
        protected_paths.append(Path(manifest["source"]["path"]))
    require(edited.is_dir() and all(not edited.is_relative_to(p) for p in protected_paths),
            "Use a separate directory for edited JSON files")
    tag = f"prepared-{uuid.uuid4().hex}"
    prepared = work / tag
    prepared.mkdir()
    expected_plain = {}
    edited_docs = {}
    for row in manifest["episodes"]:
        tid = row["id"]
        plain = prepared / f"{tid}.json"
        require(row["filename"] == plain.name, "Unexpected manifest filename")
        shutil.copyfile(child_file(edited, plain.name), plain)
        doc = load(plain)
        require(isinstance(doc, dict) and doc.get("id") == tid and isinstance(doc.get("tracks"), list),
                f"Edited JSON belongs to a different timeline: {plain.name}")
        cipher = prepared / f"{tid}.enc"
        codec.run("-ec", plain, cipher)
        roundtrip = prepared / f"{tid}.roundtrip.json"
        codec.read(cipher, roundtrip, tid)
        require(plain.read_bytes() == roundtrip.read_bytes(), f"Encoding round trip changed {plain.name}")
        expected_plain[tid] = digest(roundtrip)
        edited_docs[tid] = doc
        if any(item["kind"] == "timeline_backup" and item["id"] == tid for item in records(manifest)):
            previous = child_file(work, Path("backup/Timelines") / tid / CONTENT)
            shutil.copyfile(previous, prepared / f"{tid}.previous.enc")
            previous_plain = prepared / f"{tid}.previous.json"
            codec.read(previous, previous_plain, tid)
            expected_plain[f"previous:{tid}"] = digest(previous_plain)
    project = load(child_file(work, Path("backup") / PROJECT))
    require(project["id"] == manifest["copy"]["project_id"], "Backup project identity changed")
    changed_ids = {row["id"] for row in manifest["episodes"]}
    project["update_time"] = time.time_ns() // 1000
    for row in project["timelines"]:
        if row["id"] in changed_ids:
            row["update_time"] = project["update_time"]
    (prepared / "project.json").write_bytes(encoded(project))
    if any(item["kind"] == "project_backup" for item in records(manifest)):
        shutil.copyfile(child_file(work, Path("backup") / PROJECT), prepared / "project.previous.json")
    registered_media = 0
    if any(item["kind"] == "metadata" for item in records(manifest)):
        meta = load(child_file(work, Path("baseline/meta.json")))
        metadata_identity(meta, manifest["copy"])
        meta["tm_draft_modified"] = project["update_time"]
        main = edited_docs.get(manifest["copy"]["main"])
        if main is not None:
            meta["tm_duration"] = main.get("duration", meta.get("tm_duration", 0))
        if getattr(args, "register_media", False):
            baselines = (load(child_file(work, Path("baseline") / f"{tid}.json")) for tid in edited_docs)
            registered_media = register_media(meta, edited_docs.values(), root, baselines)
            # register_media may rewrite newly imported material paths. Re-encode
            # timeline documents after that mutation so the portable paths reach the draft.
            for tid, doc in edited_docs.items():
                plain = prepared / f"{tid}.json"
                plain.write_bytes(encoded(doc))
                cipher = prepared / f"{tid}.enc"
                cipher.unlink(missing_ok=True)
                codec.run("-ec", plain, cipher)
                roundtrip = prepared / f"{tid}.roundtrip.json"
                roundtrip.unlink(missing_ok=True)
                codec.read(cipher, roundtrip, tid)
                require(plain.read_bytes() == roundtrip.read_bytes(),
                        f"Encoding round trip changed {plain.name} after media registration")
                expected_plain[tid] = digest(roundtrip)
        (prepared / "meta.json").write_bytes(encoded(meta))
        codec.run("-ec", prepared / "meta.json", prepared / "meta.enc")
        actual_meta = codec.document(prepared / "meta.enc", prepared / "meta.roundtrip.json")
        require(actual_meta == meta, "Encoding round trip changed draft metadata")
        expected_plain["metadata"] = digest(prepared / "meta.roundtrip.json")
    elif getattr(args, "register_media", False):
        raise DraftError("Cannot register imported media: this snapshot has no draft_meta_info.json")
    audit_media_paths(edited_docs.values(), root)
    entries = list(transaction_paths(work, manifest, tag))
    tx = dict(status="writing", prepared=tag,
              hashes={relative.as_posix(): digest(new) for relative, _, new in entries},
              plaintext_hashes=expected_plain, registered_media=registered_media)
    expected = manifest["source"], manifest["copy"]
    require(same_identities(identities(Path(manifest["index"]), *(d["name"] if d is not None else None for d in expected)), expected),
            "Draft registration changed during staging")
    unlocked(root)
    for relative, old, _ in entries:
        require(digest(child_file(root, relative)) == digest(old), f"Live file changed during staging: {relative}")
    atomic(journal, encoded(tx))
    try:
        for relative, old, new in entries:
            unlocked(root)
            current = child_file(root, relative)
            require(digest(current) == digest(old), f"Live file changed before write: {relative}")
            atomic(current, new.read_bytes())
            require(digest(current) == tx["hashes"][relative.as_posix()], f"Write checksum failed: {relative}")
        tx["status"] = "index_pending"
        atomic(journal, encoded(tx))
    except BaseException:
        try:
            restore(work, root, manifest, tx)
        except (DraftError, OSError) as rollback_error:
            raise DraftError(f"Automatic rollback stopped. The recovery journal remains: {rollback_error}") from rollback_error
        raise
    return finish_commit(work, manifest, root, tx)


def finish_commit(work, manifest, root, tx):
    unlocked(root)
    for relative, _, _ in transaction_paths(work, manifest, tx["prepared"]):
        require(digest(child_file(root, relative)) == tx["hashes"][relative.as_posix()],
                f"Copy changed before index refresh: {relative}")
    index = Path(manifest["index"])
    with file_lock(index.with_name(".codex-draft-index.lock")):
        before = index.read_bytes()
        data = json.loads(before)
        found = [row for row in data["all_draft_store"] if row.get("draft_id") == manifest["copy"]["draft_id"]]
        require(len(found) == 1 and found[0].get("draft_name") == manifest["copy"]["name"]
                and Path(found[0].get("draft_fold_path", "")).resolve() == root,
                "Copy registration changed before index refresh")
        project = load(child_file(work, Path(tx["prepared"]) / "project.json"))
        found[0]["tm_draft_modified"] = project["update_time"]
        if "metadata" in tx["plaintext_hashes"]:
            meta = load(child_file(work, Path(tx["prepared"]) / "meta.roundtrip.json"))
            found[0]["tm_duration"] = meta.get("tm_duration", found[0].get("tm_duration", 0))
        unlocked(root)
        atomic_cas(index, before, encoded(data))
    tx["status"] = "committed"
    atomic(work / "transaction.json", encoded(tx))
    return dict(copy=manifest["copy"]["name"], episodes=[row["name"] for row in manifest["episodes"]],
                status="committed", journal=str(work / "transaction.json"),
                registered_media=tx.get("registered_media", 0))


def commit(args):
    work = Path(args.workspace).resolve(strict=True)
    child_file(work, Path("snapshot.json"))
    manifest = load(work / "snapshot.json")
    with transaction_lock(work), file_lock(draft_lock_path(manifest["copy"])):
        return commit_locked(args, *context(args))


def timerange(value):
    return (value or {}).get("start", 0), (value or {}).get("duration", 0)


def clip_state(segment):
    clip = segment.get("clip") or {}
    scale, position, flip = (clip.get(key) or {} for key in ("scale", "transform", "flip"))
    return (scale.get("x", 1), scale.get("y", 1), position.get("x", 0), position.get("y", 0),
            clip.get("rotation", 0), flip.get("horizontal", False), flip.get("vertical", False))


def project_playback(doc):
    materials = {m["id"]: m for group in doc.get("materials", {}).values() if isinstance(group, list)
                 for m in group if isinstance(m, dict) and "id" in m}
    tracks = []
    times = [doc.get("duration", 0)]
    for track in doc["tracks"]:
        segments = []
        for seg in track["segments"]:
            mat = materials[seg["material_id"]]
            refs = [materials[ref] for ref in seg.get("extra_material_refs", [])]
            effects = [ref for ref in refs if ref.get("type") in {"audio_fade", "transition", "speed"}]
            times.extend(timerange(seg.get("target_timerange")) + timerange(seg.get("source_timerange")))
            segments.append((seg["id"], seg["material_id"], seg.get("visible", True), seg.get("volume", 1),
                             seg.get("speed", 1), seg.get("track_attribute", 0), clip_state(seg),
                             seg.get("common_keyframes", []), (mat.get("path") or "").replace("\\", "/"),
                             mat.get("content", mat.get("text", "")), effects))
        tracks.append((track["type"], track.get("name") or "", track.get("flag", 0),
                       track.get("attribute", 0), segments))
    state = doc["id"], doc.get("fps"), doc.get("canvas_config"), tracks
    return state, times


def verify(args):
    work, manifest, root, codec = context(args)
    tx = load(child_file(work, Path("transaction.json")))
    require(tx["status"] == "committed", "No completed transaction. Rerun commit to recover an interrupted write.")
    entries = list(transaction_paths(work, manifest, tx["prepared"]))
    live_snapshot = {relative: digest(child_file(root, relative)) for relative, _, _ in entries}
    for relative, _, new in entries:
        planned = tx["hashes"][relative.as_posix()]
        require(digest(new) == planned, f"Staged checksum changed: {relative}")
        if not args.native_saved:
            require(live_snapshot[relative] == planned, f"Live checksum differs: {relative}")
    verified = []
    with tempfile.TemporaryDirectory(prefix="readback-", dir=work) as directory:
        scratch = Path(directory)
        decoded = {}
        for number, item in enumerate(records(manifest)):
            relative = Path(item["path"])
            path = child_file(root, relative)
            kind, tid = item["kind"], item["id"]
            if kind.startswith("timeline"):
                key = digest(path)
                if key not in decoded:
                    decoded[key] = codec.read(path, scratch / f"{number}.json", tid)
                actual = decoded[key]
                previous = kind == "timeline_backup"
                expected_key = f"previous:{tid}" if previous else tid
                expected_name = f"{tid}.previous.json" if previous else f"{tid}.roundtrip.json"
                expected = child_file(work, Path(tx["prepared"]) / expected_name)
                require(digest(expected) == tx["plaintext_hashes"][expected_key],
                        f"Staged plaintext changed: {relative}")
                if args.native_saved:
                    options = [load(expected)]
                    if previous:
                        options.append(load(child_file(work, Path(tx["prepared"]) / f"{tid}.roundtrip.json")))
                    require(any(same_playback(actual, value, args.tolerance_us) for value in options),
                            f"Playback state changed after native save: {relative}")
                else:
                    require(actual == load(expected), f"Live codec readback differs: {relative}")
            elif kind == "metadata":
                actual = codec.document(path, scratch / f"{number}.json")
                expected = child_file(work, Path(tx["prepared"]) / "meta.roundtrip.json")
                require(digest(expected) == tx["plaintext_hashes"]["metadata"], "Staged metadata changed")
                metadata_identity(actual, manifest["copy"])
                if args.native_saved:
                    planned = load(expected)
                    require(abs(actual.get("tm_duration", 0) - planned.get("tm_duration", 0)) <= args.tolerance_us,
                            "Native-save metadata duration differs")
                    require(imported_paths(actual) == imported_paths(planned),
                            "Native-save imported media catalogue differs")
                else:
                    require(actual == load(expected), "Live metadata differs from staged metadata")
            else:
                expected = load(child_file(work, Path(tx["prepared"]) / item["prepared"]))
                require(project_identity(load(path)) == project_identity(expected),
                        f"Live project identity or timeline map differs: {relative}")
        for row in manifest["episodes"]:
            actual = decoded[digest(root / "Timelines" / row["id"] / CONTENT)]
            verified.append(dict(name=row["name"], id=row["id"], duration_us=actual.get("duration"),
                                 tracks=[dict(type=t["type"], segments=len(t["segments"])) for t in actual["tracks"]],
                                 active_mirror=True))
    unlocked(root)
    require(all(digest(child_file(root, relative)) == value for relative, value in live_snapshot.items()),
            "Live files changed during verification")
    return dict(copy=manifest["copy"]["name"], mode="native-saved" if args.native_saved else "exact",
                episodes=verified, files=[item["path"] for item in records(manifest)])


def same_playback(actual, expected, tolerance):
    state, times = project_playback(actual)
    expected_state, expected_times = project_playback(expected)
    return state == expected_state and len(times) == len(expected_times) and all(
        abs(a-b) <= tolerance for a, b in zip(times, expected_times))


def imported_paths(meta):
    return sorted(str(item.get("file_Path", "")).replace("\\", "/").casefold()
                  for group in meta.get("draft_materials", []) for item in group.get("value", [])
                  if item.get("file_Path"))


def active_media(doc):
    lookup = {m["id"]: m for group in doc.get("materials", {}).values() if isinstance(group, list)
              for m in group if isinstance(m, dict) and "id" in m}
    for track in doc.get("tracks", []):
        if track.get("type") not in ("video", "audio"):
            continue
        for segment in track.get("segments", []):
            material = lookup[segment["material_id"]]
            if material.get("path"):
                yield track["type"], material


def media_path(raw, root):
    match = re.match(r"^##_draftpath_placeholder_[^#]+_##[/\\\\]", raw)
    if match:
        path = (root / raw[match.end():].replace("\\", "/")).resolve()
        require(path.is_relative_to(root), f"Draft-relative media escapes its root: {raw}")
        return path
    path = Path(raw)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


TEMP_MEDIA_MARKERS = ('/work/', '/analyze/', '/timeline_audio/', '/effects_audio/', '/preset_audio/')


def draft_placeholder(docs):
    pattern = re.compile(r"^##_draftpath_placeholder_[^#]+_##")
    for doc in docs:
        for _, material in active_media(doc):
            raw = material.get("path") or ""
            match = pattern.match(raw.replace("\\", "/"))
            if match:
                return match.group(0)
    return None


def audit_media_paths(docs, root):
    for doc in docs:
        for _, material in active_media(doc):
            raw = material.get("path") or ""
            path = media_path(raw, root)
            normal = str(raw).replace("\\", "/").casefold()
            if not path.is_relative_to(root):
                require(not any(marker in normal for marker in TEMP_MEDIA_MARKERS),
                        f"Temporary media path must not be committed: {raw}")
            require(path.is_file(), f"Active media is missing: {path}")


def register_media(meta, docs, root, baseline_docs):
    baseline_docs = list(baseline_docs)
    baseline_paths = {str(media_path(material["path"], root)).casefold()
                      for doc in baseline_docs for _, material in active_media(doc)}
    candidates = []
    for doc in docs:
        for track_type, material in active_media(doc):
            if material.get("sound_separate_type") in ("human", "background") or material.get("type") == "photo":
                continue
            path = media_path(material["path"], root)
            # Existing playable references need not have catalogue entries. Only
            # this edit's newly active paths are the import transaction's scope.
            if str(path).casefold() in baseline_paths:
                continue
            require(path.is_file(), f"Imported media is missing: {path}")
            candidates.append((track_type, material, path))
    groups = meta.get("draft_materials", [])
    category = next((group.get("value") for group in groups if group.get("type") == 0), None)
    require(isinstance(category, list), "Cannot register imported media: no compatible type-0 metadata catalogue")
    registered = {str(media_path(item["file_Path"], root)).casefold()
                  for item in category if item.get("file_Path")}
    placeholder = draft_placeholder(baseline_docs) or draft_placeholder(docs)
    added = 0
    for track_type, material, path in candidates:
        checksum = digest(path)
        imported_name = f"{checksum[:16]}_{path.name}"
        imported = root / "Resources" / "Imported" / imported_name
        imported.parent.mkdir(parents=True, exist_ok=True)
        if not imported.exists():
            shutil.copy2(path, imported)
        require(digest(imported) == checksum, f"Imported media copy checksum failed: {imported}")
        final_path = (f"{placeholder}/Resources/Imported/{imported_name}"
                      if placeholder else str(imported.resolve()))
        material["path"] = final_path
        key = str(media_path(final_path, root)).casefold()
        if key in registered:
            continue
        kind = "music" if track_type == "audio" else "video"
        template = next((item for item in category if item.get("metetype") == kind), None)
        require(template is not None, f"Cannot register {path.name}: no existing {kind} metadata template")
        item = json.loads(json.dumps(template))
        now = time.time_ns() // 1000
        duration = material.get("duration", 0)
        item.update(id=str(uuid.uuid4()).upper(), metetype=kind,
                    extra_info=material.get("name") or path.name, file_Path=final_path,
                    duration=duration, import_time=now // 1_000_000, import_time_ms=now,
                    roughcut_time_range=dict(start=0, duration=duration))
        category.append(item)
        registered.add(key)
        added += 1
    audit_media_paths(docs, root)
    return added

def without_active_media_paths(doc):
    value = json.loads(json.dumps(doc))
    materials = {m["id"]: m for group in value.get("materials", {}).values() if isinstance(group, list)
                 for m in group if isinstance(m, dict) and "id" in m}
    active = {segment["material_id"] for track in value.get("tracks", [])
              if track.get("type") in ("video", "audio") for segment in track.get("segments", [])}
    for identifier in active:
        material = materials[identifier]
        if "path" in material:
            material["path"] = "<active-media-path>"
    return value


def rebind_report(report, original_doc, final_doc, root, final_path):
    require(report.get("timeline_id") == final_doc.get("id") == original_doc.get("id"),
            "Edit report timeline identity differs from the final readback")
    require(without_active_media_paths(original_doc) == without_active_media_paths(final_doc),
            "Final readback differs from the edited JSON beyond active media paths")
    materials = {m["id"]: m for group in final_doc.get("materials", {}).values() if isinstance(group, list)
                 for m in group if isinstance(m, dict) and "id" in m}
    segments = {segment["id"]: segment for track in final_doc["tracks"]
                if track.get("type") in ("video", "audio") for segment in track["segments"]}

    def rebind(row):
        segment = segments.get(row.get("segment_id"))
        require(segment is not None, f"Report segment is absent from final readback: {row.get('segment_id')}")
        raw = materials[segment["material_id"]].get("path")
        require(bool(raw), f"Final media has no path: {row.get('segment_id')}")
        resolved = media_path(raw, root)
        require(resolved.is_file(), f"Final media is missing: {resolved}")
        checksum = digest(resolved)
        expected = row.get("sha256")
        require(expected is None or expected == checksum,
                f"Final media checksum differs from the edit report: {row.get('segment_id')}")
        row.update(path=raw, resolved_path=str(resolved), sha256=checksum)

    for row in [*report.get("sfx", []), *report.get("bgm_zones", [])]:
        rebind(row)
    report.update(output=str(final_path), output_sha256=digest(final_path),
                  media_rebind="Verified that only active media paths changed")
    return report


def export_readback(args, work, manifest, root, codec):
    episodes = [row for row in manifest["episodes"] if row["name"] == args.episode]
    require(len(episodes) == 1, f"Expected one snapshot episode named {args.episode!r}")
    episode = episodes[0]
    output = Path(args.output).resolve()
    require(not output.exists(), "Readback output directory must be new")
    protected = [root, work]
    if manifest["source"] is not None:
        protected.append(Path(manifest["source"]["path"]))
    require(all(not output.is_relative_to(base) for base in protected),
            "Readback output must be outside drafts and the transaction workspace")
    report = load(Path(args.report).resolve(strict=True)) if args.report else None
    original_doc = None
    if report is not None:
        original_output = Path(report["output"]).resolve(strict=True)
        require(digest(original_output) == report.get("output_sha256"),
                "Original edited JSON changed; cannot rebind its report")
        original_doc = load(original_output)
    output.mkdir(parents=True)
    final_path = output / f"{episode['id']}.json"
    final_doc = codec.read(child_file(root, Path("Timelines") / episode["id"] / CONTENT), final_path, episode["id"])
    audit_media_paths([final_doc], root)
    result = dict(status="readback", copy=manifest["copy"]["name"], episode=episode["name"],
                  timeline_id=episode["id"], json=str(final_path), sha256=digest(final_path),
                  verification="committed_exact", report=None)
    if report is not None:
        rebind_report(report, original_doc, final_doc, root, final_path)
        report["final_readback"] = dict(copy=result["copy"], episode=result["episode"],
                                       json=result["json"], sha256=result["sha256"],
                                       verification=result["verification"])
        atomic(output / "report.json", encoded(report))
        result["report"] = str(output / "report.json")
    atomic(output / "readback.json", encoded(result))
    return result


def readback(args):
    work = Path(args.workspace).resolve(strict=True)
    child_file(work, Path("snapshot.json"))
    manifest = load(work / "snapshot.json")
    with transaction_lock(work), file_lock(draft_lock_path(manifest["copy"])):
        args.native_saved = False
        args.tolerance_us = 2
        verify(args)
        work, manifest, root, codec = context(args)
        return export_readback(args, work, manifest, root, codec)


def recover(args):
    work = Path(args.workspace).resolve(strict=True)
    manifest = load(child_file(work, Path("snapshot.json")))
    with transaction_lock(work), file_lock(draft_lock_path(manifest["copy"])):
        work, manifest, root, _ = context(args, need_codec=False)
        tx = load(child_file(work, Path("transaction.json")))
        require(tx["status"] in ("writing", "rolled_back"),
                "Recovery is for an interrupted write; committed edits need a new snapshot")
        if tx["status"] == "writing":
            restore(work, root, manifest, tx)
        return dict(copy=manifest["copy"]["name"], status="rolled_back", workspace=str(work))


def rebase(value, source, destination, identities=None, media=None):
    if isinstance(value, dict):
        return {key: rebase(item, source, destination, identities, media) for key, item in value.items()}
    if isinstance(value, list):
        return [rebase(item, source, destination, identities, media) for item in value]
    if isinstance(value, str):
        if identities and value in identities:
            return identities[value]
        normal = value.replace("\\", "/")
        if media and normal.casefold() in media:
            return media[normal.casefold()]
        prefix = source.as_posix()
        if normal.casefold() == prefix.casefold() or normal.casefold().startswith(prefix.casefold() + "/"):
            return destination.as_posix() + normal[len(prefix):]
    return value


def tree_hashes(root):
    result = {}
    for folder, directories, filenames in os.walk(root, followlinks=False):
        parent = Path(folder)
        for name in directories + filenames:
            path = parent / name
            require(path.resolve() == path and not path.is_symlink(), f"Redirected draft resource: {path}")
        for name in filenames:
            path = parent / name
            result[path.relative_to(root).as_posix()] = digest(path)
    return result


def atomic_cas(path, expected, data):
    require(path.read_bytes() == expected, f"Concurrent save changed {path}")
    atomic(path, data)
    require(path.read_bytes() == data, f"Concurrent save followed the write to {path}")


def valid_copy_name(value):
    require(isinstance(value, str) and value and value not in (".", "..")
            and not re.search(r'[<>:"/\\|?*\x00-\x1f]', value) and value == value.rstrip(" ."),
            "Copy name must be one valid local folder name")
    return value


def clone_media(documents, stage, destination, collect):
    external = {}
    replacements = {}
    for doc in documents:
        for _, material in active_media(doc):
            path = media_path(material["path"], destination)
            if path.is_relative_to(destination):
                actual = stage / path.relative_to(destination)
                require(actual.is_file(), f"Copied active media is missing: {path}")
                continue
            require(path.is_file(), f"External active media is missing: {path}")
            key = path.as_posix().casefold()
            if key in external:
                continue
            external[key] = dict(path=path.as_posix(), size=path.stat().st_size)
            if collect:
                checksum = digest(path)
                relative = Path("Resources/Imported") / f"{checksum[:16]}_{path.name}"
                target = stage / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                require(digest(target) == checksum and digest(path) == checksum,
                        f"External media changed while collecting: {path}")
                replacements[key] = (destination / relative).as_posix()
    return list(external.values()), replacements


def encode_document(codec, doc, temp, name, target, tid=None):
    plain, cipher = temp / f"{name}.json", temp / f"{name}.enc"
    plain.write_bytes(encoded(doc))
    codec.run("-ec", plain, cipher)
    roundtrip = temp / f"{name}.readback.json"
    actual = codec.read(cipher, roundtrip, tid) if tid else codec.document(cipher, roundtrip)
    require(actual == doc, f"Clone codec round trip differs: {name}")
    atomic(target, cipher.read_bytes())


def embedded_documents(root, known, codec, temp):
    """Rebase supported compound subdrafts as well as indexed timelines."""
    bindings, docs = [], {}
    for primary in root.rglob(CONTENT):
        relative = primary.relative_to(root).as_posix()
        if relative in known:
            continue
        folder = primary.parent
        unknown = [p.name for p in folder.glob("template-*.tmp") if p.name != MIRROR]
        require(not unknown, f"Unknown embedded mirror layout in {folder.relative_to(root)}: {unknown}")
        number = len(docs)
        doc = codec.document(primary, temp / f"embedded-{number}.json")
        tid = safe_id(doc.get("id"))
        require(isinstance(doc.get("tracks"), list), f"Unsupported embedded timeline: {relative}")
        for name in (CONTENT, MIRROR, CONTENT + ".bak"):
            path = folder / name
            if not path.exists():
                continue
            rel = path.relative_to(root).as_posix()
            value = doc if name == CONTENT else codec.read(path, temp / f"embedded-{len(docs)}-alias.json", tid)
            if name == MIRROR:
                require(value == doc, f"Embedded active mirror differs: {rel}")
            kind = "embedded_backup" if name.endswith(".bak") else "embedded"
            bindings.append(dict(path=rel, kind=kind, id=tid, prepared=None))
            docs[rel] = value
    return bindings, docs


def build_clone(args, work, journal, codec):
    source = Path(journal["source"]["path"])
    destination = Path(journal["destination"])
    stage = Path(journal["stage"])
    unlocked(source)
    require(not destination.exists(), f"Clone destination already exists: {destination}")
    require(stage.parent == destination.parent and stage.name == journal["stage_name"],
            "Unexpected clone staging path")
    if stage.exists():
        require(stage.resolve() == stage and stage.name.startswith(".codex-clone-"), "Unsafe clone staging recovery path")
        shutil.rmtree(stage)
    original_hashes = tree_hashes(source)
    shutil.copytree(source, stage)
    require(tree_hashes(stage) == original_hashes, "Draft resources did not copy completely")
    require(tree_hashes(source) == original_hashes, "Source changed while cloning")
    unlocked(source)
    source_info = journal["source"]
    episodes = selected_files(source_info, [row["name"] for row in source_info["timelines"]])
    bindings = layout_files(stage, source_info, episodes)
    require(any(item["kind"] == "metadata" for item in bindings),
            "Clone needs a supported draft_meta_info.json identity")
    baseline = work / ("baseline-" + uuid.uuid4().hex)
    baseline.mkdir()
    docs = decode_snapshot(codec, stage, baseline, source_info, episodes, bindings)
    old_meta = load(baseline / "meta.json")
    project = load(stage / PROJECT)
    identity_map = {source_info["draft_id"]: journal["draft_id"],
                    source_info["project_id"]: journal["project_id"]}
    documents = {}
    with tempfile.TemporaryDirectory(prefix="clone-codec-", dir=work) as directory:
        temp = Path(directory)
        extra_bindings, extra_docs = embedded_documents(stage, {item["path"] for item in bindings}, codec, temp)
        bindings.extend(extra_bindings)
        for number, item in enumerate(bindings):
            if item["kind"] == "timeline":
                documents[item["path"]] = docs[item["id"]]
            elif item["kind"] == "timeline_backup":
                documents[item["path"]] = codec.read(stage / item["path"], temp / f"history-{number}.json", item["id"])
            elif item["kind"] == "metadata":
                documents[item["path"]] = old_meta
            elif item["kind"].startswith("embedded"):
                documents[item["path"]] = extra_docs[item["path"]]
        documents = {key: rebase(value, source, destination, identity_map) for key, value in documents.items()}
        for doc in documents.values():
            for _, material in active_media(doc):
                raw = material["path"]
                if not raw.startswith("##_draftpath_placeholder_") and not Path(raw).is_absolute():
                    material["path"] = rebase(media_path(raw, source).as_posix(), source, destination)
        active_documents = [documents[item["path"]] for item in bindings if item["kind"] in ("timeline", "embedded")]
        external, replacements = clone_media(active_documents, stage, destination,
                                              getattr(args, "collect_external_media", False))
        if replacements:
            documents = {key: rebase(value, source, destination, media=replacements)
                         for key, value in documents.items()}
        now = journal["created"]
        meta = documents[META.as_posix()]
        main = docs[source_info["main"]]
        meta.update(draft_id=journal["draft_id"], draft_name=journal["copy_name"],
                    draft_fold_path=destination.as_posix(), draft_root_path=destination.parent.as_posix(),
                    tm_draft_create=now, tm_draft_modified=now, tm_duration=main.get("duration", 0),
                    cloud_draft_sync=False, draft_deeplink_url="")
        project = rebase(project, source, destination, identity_map)
        project.update(id=journal["project_id"], create_time=now, update_time=now)
        for timeline in project["timelines"]:
            timeline["update_time"] = now
        known = {item["path"] for item in bindings}
        for relative in original_hashes:
            if relative in known or not relative.endswith((".json", ".json.bak")):
                continue
            path = stage / relative
            try:
                original = load(path)
            except (ValueError, UnicodeError):
                continue
            changed = rebase(original, source, destination, identity_map, replacements)
            if changed != original:
                atomic(path, encoded(changed))
        encoded_documents = {}
        for number, item in enumerate(bindings):
            relative = item["path"]
            original = work / "backup" / relative
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, original)
            if item["kind"] in ("project", "project_backup"):
                atomic(stage / relative, encoded(project))
            else:
                document_key = hashlib.sha256(encoded(documents[relative])).hexdigest()
                if document_key in encoded_documents:
                    atomic(stage / relative, encoded_documents[document_key])
                else:
                    encode_document(codec, documents[relative], temp, f"document-{number}",
                                    stage / relative, item.get("id"))
                    encoded_documents[document_key] = (stage / relative).read_bytes()
    require(tree_hashes(source) == original_hashes, "Source changed before clone publication")
    unlocked(source)
    journal.update(status="staged", source_hashes=original_hashes, baseline=str(baseline),
                   identity_files=[item["path"] for item in bindings if item["kind"] != "metadata"],
                   expected_files=tree_hashes(stage), external_media=external)
    atomic(work / "clone.json", encoded(journal))
    require(not destination.exists(), f"Clone destination appeared during preparation: {destination}")
    os.rename(stage, destination)
    journal["status"] = "published"
    atomic(work / "clone.json", encoded(journal))


def clone_index_entry(source_entry, journal):
    source = Path(journal["source"]["path"])
    destination = Path(journal["destination"])
    entry = rebase(source_entry, source, destination,
                   {journal["source"]["draft_id"]: journal["draft_id"],
                    journal["source"]["project_id"]: journal["project_id"]})
    entry.update(draft_name=journal["copy_name"], draft_id=journal["draft_id"],
                 draft_fold_path=destination.as_posix(), draft_root_path=destination.parent.as_posix(),
                 draft_json_file=str(destination / CONTENT),
                 cloud_draft_sync=False, tm_draft_create=journal["created"],
                 tm_draft_modified=time.time_ns() // 1000)
    return entry


def register_clone(index, work, journal, codec):
    root = Path(journal["destination"])
    unlocked(root)
    for relative in journal["identity_files"]:
        require(digest(child_file(root, Path(relative))) == journal["expected_files"][relative],
                f"Clone files changed before registration: {relative}")
    with transaction_lock(work), file_lock(index.with_name(".codex-draft-index.lock")):
        before = index.read_bytes()
        data = json.loads(before)
        entries = data["all_draft_store"]
        source_rows = [row for row in entries if row.get("draft_name") == journal["source"]["name"]]
        require(len(source_rows) == 1, "Source registration is no longer unique")
        source_info = describe(source_rows[0])
        require(all(source_info[key] == journal["source"][key]
                    for key in ("name", "path", "draft_id", "project_id")), "Source registration identity changed")
        by_name = [row for row in entries if row.get("draft_name") == journal["copy_name"]]
        by_path = [row for row in entries if row.get("draft_fold_path")
                   and Path(row["draft_fold_path"]).resolve() == root]
        require(len(by_path) <= 1 and all(row in by_path for row in by_name),
                "Concurrent index conflict: copy name belongs to another folder or has duplicate entries")
        existing = by_path[0] if by_path else None
        if existing:
            require(existing.get("draft_name") == journal["copy_name"],
                    "Concurrent index conflict: destination was registered under a different name")
            native_id = safe_id(existing.get("draft_id"))
            owners = [row for row in entries if row.get("draft_id") == native_id]
            require(len(owners) == 1 and native_id.casefold() != source_info["draft_id"].casefold(),
                    "Concurrent index conflict: native copy identity is reused")
            if native_id != journal["draft_id"]:
                current = (root / META).read_bytes()
                with tempfile.TemporaryDirectory(prefix="native-identity-", dir=work) as directory:
                    temp = Path(directory)
                    meta = codec.document(root / META, temp / "native.json")
                    require(meta.get("draft_id") in (journal["draft_id"], native_id)
                            and meta.get("draft_name") == journal["copy_name"]
                            and Path(meta.get("draft_fold_path", "")).resolve() == root,
                            "Concurrent index conflict: native metadata has an unrelated identity")
                    meta["draft_id"] = native_id
                    encode_document(codec, meta, temp, "coordinated", temp / "coordinated-meta.enc")
                    unlocked(root)
                    atomic_cas(root / META, current, (temp / "coordinated-meta.enc").read_bytes())
                journal["draft_id"] = native_id
                journal["expected_files"][META.as_posix()] = digest(root / META)
                atomic(work / "clone.json", encoded(journal))
        else:
            require(not any(row.get("draft_id") == journal["draft_id"] for row in entries),
                    "Concurrent index conflict: generated copy identity is already registered")
        entry = clone_index_entry(existing or source_rows[0], journal)
        with tempfile.TemporaryDirectory(prefix="registered-meta-", dir=work) as directory:
            meta = codec.document(root / META, Path(directory) / "meta.json")
        require(meta["draft_id"] == journal["draft_id"], "Clone metadata registration identity differs")
        entry["tm_duration"] = meta.get("tm_duration", 0)
        if existing:
            entries[entries.index(existing)] = entry
        else:
            entries.insert(0, entry)
        unlocked(root)
        atomic_cas(index, before, encoded(data))
        actual = named(rows(index), journal["copy_name"])
        require(actual["draft_id"] == journal["draft_id"] and Path(actual["path"]) == root
                and actual["project_id"] == journal["project_id"], "Registered clone identity differs")
        journal["status"] = "registered"
        atomic(work / "clone.json", encoded(journal))
    return dict(status="registered", copy=journal["copy_name"], path=str(root),
                draft_id=journal["draft_id"], project_id=journal["project_id"],
                workspace=str(work), external_media=journal.get("external_media", []))


def clone(args):
    index = Path(args.index).resolve(strict=True)
    valid_copy_name(args.copy)
    require(args.source != args.copy, "Source and copy names must differ")
    source = named(rows(index), args.source)
    destination = Path(args.destination) if args.destination else Path(source["path"]).parent / args.copy
    require(destination.is_absolute(), "Clone destination must be absolute")
    destination = destination.resolve()
    require(destination.parent.is_dir() and not destination.is_relative_to(Path(source["path"]))
            and not Path(source["path"]).is_relative_to(destination), "Clone needs an independent existing parent directory")
    work = Path(args.workspace).resolve()
    require(not any(work.is_relative_to(base) or base.is_relative_to(work)
                    for base in (Path(source["path"]), destination)), "Clone workspace must be separate from both drafts")
    codec = Codec(args)
    if (work / "clone.json").is_file():
        journal = load(work / "clone.json")
        require(journal["source"]["name"] == args.source and journal["copy_name"] == args.copy
                and Path(journal["destination"]) == destination and Path(journal["index"]) == index,
                "Clone workspace belongs to a different operation")
        if journal["status"] == "registered":
            actual = named(rows(index), args.copy)
            require(actual["draft_id"] == journal["draft_id"] and actual["project_id"] == journal["project_id"]
                    and Path(actual["path"]) == destination, "Completed clone registration changed")
            return dict(status="already-created", copy=args.copy, path=str(destination), workspace=str(work))
    else:
        require(not any(row.get("draft_name") == args.copy for row in rows(index)), "Copy name is already registered")
        require(not destination.exists(), f"Clone destination already exists: {destination}")
        work.mkdir(parents=True, exist_ok=False)
        identity = uuid.uuid4().hex
        stage_name = f".codex-clone-{identity}"
        journal = dict(version=1, status="cloning", index=str(index), source=source,
                       copy_name=args.copy, destination=str(destination), stage_name=stage_name,
                       stage=str(destination.parent / stage_name), draft_id=str(uuid.uuid4()).upper(),
                       project_id=str(uuid.uuid4()).upper(), created=time.time_ns() // 1000)
        atomic(work / "clone.json", encoded(journal))
    if journal["status"] == "staged":
        stage = Path(journal["stage"])
        if not destination.exists():
            require(stage.is_dir() and tree_hashes(stage) == journal["expected_files"],
                    "Completed clone staging is missing or changed")
            os.rename(stage, destination)
        else:
            require(not stage.exists(), "Both clone staging and destination exist")
        journal["status"] = "published"
        atomic(work / "clone.json", encoded(journal))
    if journal["status"] in ("cloning", "staged"):
        build_clone(args, work, journal, codec)
    require(journal["status"] == "published", "Unknown clone recovery state")
    return register_clone(index, work, journal, codec)


def add_codec(parser, required=True):
    parser.add_argument("--codec", required=required, help="Absolute path to the installed, compatible jy-draftc executable.")
    parser.add_argument("--runtime", required=required, help="Directory passed to the codec as --jy-dir.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list", help="List registered local drafts and their actual timeline IDs.")
    listing.add_argument("--index", required=True, help="Path to the local root_meta_info.json.")
    listing.add_argument("--draft", help="One exact registered draft name.")
    copying = sub.add_parser("clone", aliases=["create-copy"], help="Create and register an independent complete draft copy.")
    copying.add_argument("--index", required=True)
    copying.add_argument("--source", required=True, help="Exact registered source name.")
    copying.add_argument("--copy", required=True, help="Unique new copy name.")
    copying.add_argument("--workspace", required=True, help="New workspace, or the same clone workspace to resume.")
    copying.add_argument("--destination", "--copy-root", dest="destination", help="Absolute final copy folder; defaults to the source library.")
    copying.add_argument("--collect-external-media", action="store_true", help="Also copy active media outside the draft into Resources/Imported.")
    add_codec(copying)
    saving = sub.add_parser("snapshot", help="Back up a closed copy, active mirrors, metadata and selected timelines.")
    saving.add_argument("--index", required=True, help="Path to the local root_meta_info.json.")
    saving.add_argument("--source", help="Exact registered source name. Omit only for a user-designated existing editing copy when the source is unavailable.")
    saving.add_argument("--copy", required=True, help="Exact registered name of the independent copy.")
    saving.add_argument("--episodes", nargs="+", required=True, help="Exact timeline names from list, separated by spaces.")
    saving.add_argument("--workspace", required=True, help="New directory for the baseline and encrypted backup.")
    add_codec(saving)
    writing = sub.add_parser("commit", help="Encode, round-trip and install edits into the closed copy only.")
    writing.add_argument("--workspace", required=True, help="Existing directory created by snapshot.")
    writing.add_argument("--edited", required=True, help="Directory of edited <timeline-id>.json files. Read only.")
    writing.add_argument("--register-media", action="store_true", help="Register newly active audio/video paths relative to this snapshot, using existing metadata templates.")
    add_codec(writing)
    checking = sub.add_parser("verify", help="Decode the actual copy and verify it against the committed transaction.")
    checking.add_argument("--workspace", required=True, help="Existing snapshot directory with a completed commit.")
    checking.add_argument("--native-saved", action="store_true", help="Compare playback fields after Jianying rewrites the files.")
    checking.add_argument("--tolerance-us", type=int, default=2, help="Maximum timestamp deviation in native-saved mode (default: 2).")
    add_codec(checking)
    reading = sub.add_parser("readback", help="Verify a committed copy, export its final JSON and safely rebind an edit report.")
    reading.add_argument("--workspace", required=True, help="Existing snapshot directory with a completed commit.")
    reading.add_argument("--episode", required=True, help="Exact episode name from this snapshot.")
    reading.add_argument("--report", help="Original apply report.json to rebind only if only media paths changed.")
    reading.add_argument("--output", required=True, help="New directory outside the draft and transaction workspace.")
    add_codec(reading)
    recovering = sub.add_parser("recover", help="Roll back a journaled interrupted write using its verified backups.")
    recovering.add_argument("--workspace", required=True)
    add_codec(recovering, required=False)
    args = parser.parse_args()
    operations = dict(list=list_drafts, clone=clone, snapshot=snapshot, commit=commit, verify=verify,
                      readback=readback, recover=recover)
    operations["create-copy"] = clone
    try:
        if args.command == "verify":
            require(args.tolerance_us >= 0, "Timestamp tolerance must be nonnegative")
        print(json.dumps(operations[args.command](args), ensure_ascii=False, indent=2))
    except (DraftError, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"{args.command}: {exc}\n")


if __name__ == "__main__":
    main()
