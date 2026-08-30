#!/usr/bin/env python3
"""Path-pinned worktree and Git snapshot implementation for agy_dispatch.

This module deliberately does not import agy_dispatch.  Its caller passes the
current dispatcher globals for each invocation, preserving the dispatcher's
exception identity and its mutable test seams when two copied runtimes coexist.
"""
from __future__ import annotations

from typing import Any, Mapping


def call(name: str, dependencies: Mapping[str, Any], *args: Any, **kwargs: Any) -> Any:
    """Run one façade target with its caller's current dependency bindings."""
    for key, value in dependencies.items():
        # Keep the invoked implementation local so a façade cannot recurse
        # into itself. Other implementation names are dependencies: callers
        # intentionally monkeypatch them in controller and regression tests.
        if not key.startswith("__") and key != name:
            globals()[key] = value
    return _IMPLEMENTATION_DEFAULTS[name](*args, **kwargs)


class _MarkerPreflightLimit(Exception):
    """The marker-only scan hit its documented bounded entry cap."""


class _UnsupportedWorktreeError(ValueError):
    """A known repository form cannot produce an accepted snapshot."""


class _ResolveUndoPresentError(_UnsupportedWorktreeError):
    """A valid, non-empty REUC observation is present in the worktree index."""


def _marker_only_preflight(root_fd: int, *, deadline: float | None = None) -> bool:
    """Reject root aliases and nested Git markers without opening their contents.

    Filesystems such as the usual macOS volume can resolve ``.GIT`` through a
    lookup for ``.git``.  Authority checks must use the directory entry's
    actual bytes, rather than a later pathname lookup.  This intentionally
    walks only no-follow directory descriptors and returns before reading,
    opening, or resolving a marker itself.  The later complete boundary or
    manifest scan remains the timing-consistency observation.
    """
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory = getattr(os, "O_DIRECTORY", 0)
    entries_seen = 0

    def binding(info: os.stat_result) -> tuple[int, ...]:
        return (
            info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns, info.st_ctime_ns,
        )

    def walk(parent_fd: int, *, is_root: bool = False) -> bool:
        nonlocal entries_seen
        if deadline is not None and time.monotonic() >= deadline:
            return False
        try:
            before_directory = os.fstat(parent_fd)
            if not stat.S_ISDIR(before_directory.st_mode):
                return False
        except OSError:
            return False
        scan_fd = -1
        try:
            # Keep ownership of a duplicate: the traversal must not depend on
            # a pathname after its parent was bound.
            scan_fd = os.dup(parent_fd)
            with os.scandir(scan_fd) as scanned:
                for entry in scanned:
                    if deadline is not None and time.monotonic() >= deadline:
                        return False
                    raw_name = os.fsencode(entry.name)
                    if not raw_name or b"\0" in raw_name:
                        return False
                    if raw_name.lower() == b".git":
                        # An exact root spelling is the only marker permitted;
                        # its normal directory or linked-worktree file binding
                        # is performed by the caller after this preflight.
                        if is_root and raw_name == b".git":
                            continue
                        return False
                    entries_seen += 1
                    if entries_seen > MAX_BOUNDARY_ENTRIES:
                        raise _MarkerPreflightLimit
                    try:
                        info = os.stat(entry.name, dir_fd=parent_fd, follow_symlinks=False)
                    except OSError:
                        return False
                    if not stat.S_ISDIR(info.st_mode):
                        continue
                    try:
                        child_fd = os.open(
                            entry.name, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd,
                        )
                    except OSError:
                        return False
                    try:
                        if binding(os.fstat(child_fd)) != binding(info) or not walk(child_fd):
                            return False
                        if binding(os.fstat(child_fd)) != binding(info):
                            return False
                    except OSError:
                        return False
                    finally:
                        os.close(child_fd)
        except OSError:
            return False
        finally:
            if scan_fd >= 0:
                os.close(scan_fd)
        try:
            return binding(os.fstat(parent_fd)) == binding(before_directory)
        except OSError:
            return False

    return walk(root_fd, is_root=True)


def _resolved_path_is_git_administration(root: str, resolved: str) -> bool:
    """Return whether a contained resolved path enters a Git admin boundary."""
    try:
        if os.path.commonpath([root, resolved]) != root:
            return False
    except ValueError:
        return False
    relative = os.path.relpath(resolved, root)
    return any(part.lower() == ".git" for part in relative.split(os.sep))


def _worktree_symlink_boundary(workdir: str) -> bool:
    """Boundedly reject a link whose resolved target leaves ``workdir``.

    This is intentionally a no-follow directory walk, not a worktree snapshot:
    link targets are resolved only to check containment and link directories are
    never traversed.  The controller invokes it for every provider workflow.
    """
    root = os.path.realpath(workdir)
    pending = [root]
    count = 0
    try:
        while pending:
            current = pending.pop()
            with os.scandir(current) as entries:
                for entry in entries:
                    raw_name = os.fsencode(entry.name)
                    if raw_name.lower() == b".git":
                        # The root marker is controller metadata, not worktree
                        # content.  Nested Git administration is handled by
                        # the existing marker preflight.
                        if current == root and raw_name == b".git":
                            continue
                        return False
                    count += 1
                    if count > MAX_BOUNDARY_ENTRIES:
                        return False
                    if entry.is_symlink():
                        # `mktemp` commonly returns /var/... on macOS while
                        # realpath canonicalizes the worktree to /private/var.
                        # Resolve before containment so an internal link is not
                        # falsely treated as an escape; chained escapes remain
                        # outside the canonical root.
                        resolved = os.path.realpath(entry.path)
                        try:
                            contained = os.path.commonpath([root, resolved]) == root
                        except ValueError:
                            contained = False
                        if not contained or not os.path.exists(resolved):
                            return False
                        if _resolved_path_is_git_administration(root, resolved):
                            # A contained alias into the root marker or a
                            # nested Git administration area still changes
                            # repository authority; containment alone is not
                            # sufficient for lifecycle/provider safety.
                            return False
                    elif entry.is_dir(follow_symlinks=False):
                        pending.append(entry.path)
    except OSError:
        return False
    return True


def _worktree_git_admin_alias_boundary(workdir: str) -> bool:
    """Reject only contained symlink aliases into a Git admin boundary.

    Snapshotting intentionally hashes outward symlink target bytes rather than
    following them, so it cannot reuse the provider/lifecycle scope boundary.
    This narrower scan preserves that evidence behavior while refusing a link
    that aliases the worktree's own Git administration.
    """
    root = os.path.realpath(workdir)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory = getattr(os, "O_DIRECTORY", 0)
    entries_seen = 0

    def binding(info: os.stat_result) -> tuple[int, ...]:
        return (
            info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns, info.st_ctime_ns,
        )

    def walk(parent_fd: int, parent_path: str, *, is_root: bool = False) -> bool:
        nonlocal entries_seen
        try:
            before_directory = os.fstat(parent_fd)
            if not stat.S_ISDIR(before_directory.st_mode):
                return False
        except OSError:
            return False
        scan_fd = -1
        try:
            # Retain the directory descriptor across enumeration so fixture and
            # runtime behavior cannot depend on a mutable pathname.
            scan_fd = os.dup(parent_fd)
            with os.scandir(scan_fd) as entries:
                for entry in entries:
                    raw_name = os.fsencode(entry.name)
                    if not raw_name or b"\0" in raw_name:
                        return False
                    if raw_name.lower() == b".git":
                        if is_root and raw_name == b".git":
                            continue
                        return False
                    entries_seen += 1
                    if entries_seen > MAX_BOUNDARY_ENTRIES:
                        return False
                    try:
                        info = os.stat(
                            entry.name, dir_fd=parent_fd, follow_symlinks=False,
                        )
                    except OSError:
                        return False
                    if stat.S_ISLNK(info.st_mode):
                        try:
                            resolved = os.path.realpath(
                                os.path.join(parent_path, entry.name),
                            )
                            after_link = os.stat(
                                entry.name, dir_fd=parent_fd, follow_symlinks=False,
                            )
                        except OSError:
                            return False
                        if binding(info) != binding(after_link):
                            return False
                        if _resolved_path_is_git_administration(root, resolved):
                            return False
                        continue
                    if not stat.S_ISDIR(info.st_mode):
                        continue
                    try:
                        child_fd = os.open(
                            entry.name, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd,
                        )
                    except OSError:
                        return False
                    try:
                        if (
                            binding(os.fstat(child_fd)) != binding(info)
                            or not walk(child_fd, os.path.join(parent_path, entry.name))
                            or binding(os.fstat(child_fd)) != binding(info)
                        ):
                            return False
                    except OSError:
                        return False
                    finally:
                        os.close(child_fd)
        except OSError:
            return False
        finally:
            if scan_fd >= 0:
                os.close(scan_fd)
        try:
            return binding(os.fstat(parent_fd)) == binding(before_directory)
        except OSError:
            return False

    root_fd = -1
    try:
        root_fd = os.open(root, os.O_RDONLY | directory | nofollow)
        root_info = os.fstat(root_fd)
        if (
            not stat.S_ISDIR(root_info.st_mode)
            or binding(os.lstat(root)) != binding(root_info)
        ):
            return False
        return walk(root_fd, root, is_root=True)
    except OSError:
        return False
    finally:
        if root_fd >= 0:
            os.close(root_fd)


def _project_boundary(workdir: str) -> dict[str, Any]:
    root = os.path.realpath(workdir)
    if root != workdir:
        raise DispatchError("project worktree is no longer canonical")
    root_fd = -1
    try:
        root_fd = os.open(
            root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        root_info = os.fstat(root_fd)
        if (
            not stat.S_ISDIR(root_info.st_mode)
            or _identity(os.lstat(root)) != _identity(root_info)
        ):
            raise DispatchError("project worktree cannot be inspected")
        try:
            marker_preflight = _marker_only_preflight(root_fd)
        except _MarkerPreflightLimit as exc:
            raise DispatchError("project worktree boundary scan is too large") from exc
        if not marker_preflight:
            raise DispatchError("project worktree has nested Git administration")
    except DispatchError:
        raise
    except OSError as exc:
        raise DispatchError("project worktree cannot be inspected") from exc
    finally:
        if root_fd >= 0:
            os.close(root_fd)
    marker = Path(root) / ".git"
    descriptor = -1
    try:
        descriptor = os.open(marker, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as exc:
        raise DispatchError("project worktree has no Git marker") from exc
    try:
        marker_info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(marker_info.st_mode)
            or marker_info.st_uid != os.getuid()
            or marker_info.st_nlink != 1
        ):
            raise DispatchError("project Git marker must be one owner-owned linked-worktree file")
        if marker_info.st_size > 4096:
            raise DispatchError("project Git marker is oversized")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, 4097 - total)
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > 4096:
                raise DispatchError("project Git marker is oversized")
        after = os.fstat(descriptor)
        if after.st_size > 4096:
            raise DispatchError("project Git marker is oversized")
    except DispatchError:
        raise
    except OSError as exc:
        raise DispatchError("project Git marker is unavailable") from exc
    finally:
        os.close(descriptor)
    try:
        named = marker.lstat()
    except OSError as exc:
        raise DispatchError("project Git marker identity changed") from exc
    raw = b"".join(chunks)
    if (
        not stat.S_ISREG(after.st_mode)
        or after.st_uid != os.getuid()
        or after.st_nlink != 1
        or not stat.S_ISREG(named.st_mode)
        or named.st_uid != os.getuid()
        or named.st_nlink != 1
        or _identity(marker_info) != _identity(after)
        or _identity(after) != _identity(named)
        or marker_info.st_size != after.st_size
        or after.st_size != named.st_size
        or len(raw) != after.st_size
        or marker_info.st_mtime_ns != after.st_mtime_ns
        or marker_info.st_ctime_ns != after.st_ctime_ns
        or after.st_mtime_ns != named.st_mtime_ns
        or after.st_ctime_ns != named.st_ctime_ns
    ):
        raise DispatchError("project Git marker identity changed")
    marker_record: dict[str, Any] = {
        "kind": "file", "identity": list(_identity(after)), "sha256": digest(raw),
    }
    if not _worktree_symlink_boundary(root):
        raise DispatchError("project worktree has an outward symlink")
    return marker_record


def _safe_git_owner_mode(metadata: os.stat_result, *, directory: bool) -> bool:
    """Keep snapshot plumbing inside the documented local-owner/root TCB."""
    mode = stat.S_IMODE(metadata.st_mode)
    if metadata.st_uid not in {os.geteuid(), 0}:
        return False
    if not directory and metadata.st_mode & (stat.S_ISUID | stat.S_ISGID):
        return False
    if not (mode & 0o022):
        return True
    return bool(
        directory and metadata.st_uid == 0 and (mode & stat.S_ISVTX)
        and (mode & 0o022) == 0o022
    )


def _safe_git_executable() -> tuple[str, dict[str, Any]] | None:
    """Resolve Git through a bounded safe ownership and symlink-chain check."""
    candidate = shutil.which("git")
    if not candidate:
        return None

    def authority(info: os.stat_result) -> tuple[int, int, int, int, int]:
        return info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid

    def target_binding(info: os.stat_result) -> tuple[int, ...]:
        return (
            info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns, info.st_ctime_ns,
        )

    def bind(selected: str) -> tuple[str, dict[str, Any]] | None:
        """Bind one exact executable spelling without relaxing path authority."""
        selected = os.path.abspath(selected)
        parts = list(Path(selected).parts[1:])
        current = Path(os.sep)
        chain: list[tuple[tuple[int, int, int, int, int], str]] = []
        components: list[tuple[int, int, int, int, int]] = []
        seen: set[tuple[int, int]] = set()
        try:
            for _ in range(128):
                if not parts:
                    break
                part = parts.pop(0)
                if part in {"", ".", ".."}:
                    return None
                current /= part
                metadata = os.lstat(current)
                if stat.S_ISLNK(metadata.st_mode):
                    if metadata.st_uid not in {os.geteuid(), 0}:
                        return None
                    identity = (metadata.st_dev, metadata.st_ino)
                    if identity in seen or len(chain) >= 16:
                        return None
                    seen.add(identity)
                    target = os.readlink(current)
                    chain.append((authority(metadata), digest(os.fsencode(target))))
                    target_path = Path(target if os.path.isabs(target) else current.parent / target)
                    target_path = Path(os.path.normpath(str(target_path)))
                    if not target_path.is_absolute():
                        return None
                    parts = list(target_path.parts[1:]) + parts
                    current = Path(os.sep)
                    continue
                if parts:
                    if not stat.S_ISDIR(metadata.st_mode) or not _safe_git_owner_mode(metadata, directory=True):
                        return None
                    components.append(authority(metadata))
                    if len(components) > 128:
                        return None
                    continue
                if (
                    not stat.S_ISREG(metadata.st_mode)
                    or not _safe_git_owner_mode(metadata, directory=False)
                    or not (stat.S_IMODE(metadata.st_mode) & 0o111)
                ):
                    return None
                return str(current), {
                    "candidate": selected,
                    "target": target_binding(metadata),
                    "chain": tuple(chain),
                    "components": tuple(components),
                }
        except OSError:
            return None
        return None

    selected = os.path.abspath(candidate)
    bound = bind(selected)
    if bound is not None:
        return bound
    # GitHub's Apple-Silicon image can expose a group-writable Homebrew
    # launcher before the root-owned system Git.  Do not widen Homebrew's
    # authority: when that exact launcher fails the existing no-follow bind,
    # use only the fixed platform Git path and bind it by the same rules.
    if sys.platform == "darwin" and selected == "/opt/homebrew/bin/git":
        return bind("/usr/bin/git")
    return None


def _confirm_safe_git_executable(
    executable: str, expected: dict[str, Any],
) -> bool:
    current = _safe_git_executable()
    return current is not None and current[0] == executable and current[1] == expected


def _safe_git_is_outside_worktree(executable: str, worktree_root: str) -> bool:
    """Keep Git probes outside a repository-controlled executable boundary."""
    try:
        root = os.path.realpath(worktree_root)
        target = os.path.realpath(executable)
        if not os.path.isabs(root) or not os.path.isabs(target):
            return False
        return os.path.commonpath((root, target)) != root
    except (OSError, ValueError):
        # Containment is an authority decision; an unavailable or incomparable
        # path must not surface its spelling or authorize a Git subprocess.
        return False


def _stable_git_authority(info: os.stat_result) -> dict[str, int]:
    """Serialize only durable no-follow authority facts for V9 state.

    Callers may use fuller observations while holding descriptors to catch a
    race.  Persisting timestamps, sizes, or link counts would make ordinary
    Git maintenance and worktree activity look like a boundary replacement.
    """
    return {
        "dev": info.st_dev,
        "ino": info.st_ino,
        "type": stat.S_IFMT(info.st_mode),
        "mode": stat.S_IMODE(info.st_mode),
        "uid": info.st_uid,
        "gid": info.st_gid,
    }


def _full_stat_binding(info: os.stat_result) -> tuple[int, ...]:
    """Keep transient scan consistency separate from persisted authority."""
    return (
        info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
        info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _bound_git_worktree_root(
    raw: bytes, canonical_root: str, root_binding: tuple[int, ...],
) -> bool:
    """Accept only Git's exact bound-root spelling or macOS's /var alias.

    Git may report the documented ``/var`` spelling while Python canonicalizes
    the same macOS directory as ``/private/var``.  The alias is accepted only
    after strict UTF-8 framing and a no-follow full-stat binding prove that the
    final named directory is the held root.  This is deliberately narrower
    than ``realpath``: arbitrary symlink aliases and lexical path variations
    remain a failed boundary.
    """
    if (
        type(raw) is not bytes
        or type(canonical_root) is not str
        or type(root_binding) is not tuple
        or len(root_binding) != 9
        or any(type(value) is not int for value in root_binding)
        or not raw.endswith(b"\n")
        or raw.count(b"\n") != 1
        or b"\0" in raw
    ):
        return False
    try:
        path_text = raw[:-1].decode("utf-8", "strict")
    except UnicodeDecodeError:
        return False
    if not path_text or not os.path.isabs(path_text) or "\0" in path_text:
        return False
    try:
        if MODEL_SELECTION._canonical_executable_path(path_text) != (
            MODEL_SELECTION._canonical_executable_path(canonical_root)
        ):
            return False
        named = os.lstat(os.fsencode(path_text))
        if not stat.S_ISDIR(named.st_mode) or stat.S_ISLNK(named.st_mode):
            return False
        descriptor = os.open(
            os.fsencode(path_text), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            opened = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        after = os.lstat(os.fsencode(path_text))
    except OSError:
        return False
    return (
        _full_stat_binding(named) == root_binding
        and _full_stat_binding(opened) == root_binding
        and _full_stat_binding(after) == root_binding
    )


_FIXED_GIT_READ_ARGV = {
    ("rev-parse", "--is-inside-work-tree"),
    ("rev-parse", "--show-toplevel"),
    ("rev-parse", "--show-object-format"),
    ("rev-parse", "--absolute-git-dir"),
    ("rev-parse", "--git-common-dir"),
    ("rev-parse", "--git-path", "index"),
    ("rev-parse", "--verify", "-q", "HEAD^{tree}"),
    (
        "config", "--local", "--no-includes", "--get-regexp",
        "^(extensions\\.partialclone|remote\\..*\\.promisor)$",
    ),
    ("config", "--bool", "--get", "core.sparseCheckout"),
    ("ls-files", "-v", "-z"),
    ("ls-files", "--stage", "-z"),
    ("ls-files", "--debug", "-z"),
    ("ls-files", "--resolve-undo", "-z"),
    ("ls-files", "-z", "--others", "--exclude-standard"),
    ("ls-files", "-z", "--others", "--ignored", "--exclude-standard"),
    ("cat-file", "--batch"),
}


def _fixed_git_read_argv(arguments: list[str]) -> bool:
    """Accept only the read-only plumbing shapes owned by this module."""
    value = tuple(arguments)
    if value in _FIXED_GIT_READ_ARGV:
        return True
    return bool(
        len(value) == 4 and value[:3] == ("ls-tree", "-r", "-z")
        and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value[3]) is not None
    )


def _bound_git_directory(path: str, expected_binding: tuple[int, ...]) -> bool:
    """Revalidate one no-follow Git-directory authority before a pinned read."""
    if (
        type(path) is not str
        or not path
        or not os.path.isabs(path)
        or "\0" in path
        or type(expected_binding) is not tuple
        or len(expected_binding) != 9
        or any(type(value) is not int for value in expected_binding)
    ):
        return False
    named_path = os.path.abspath(path)
    try:
        named = os.lstat(os.fsencode(named_path))
        if not stat.S_ISDIR(named.st_mode) or stat.S_ISLNK(named.st_mode):
            return False
        canonical_path = os.path.realpath(named_path)
        if MODEL_SELECTION._canonical_executable_path(canonical_path) != (
            MODEL_SELECTION._canonical_executable_path(named_path)
        ):
            return False
        descriptor = os.open(
            os.fsencode(named_path), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            opened = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        after = os.lstat(os.fsencode(named_path))
    except OSError:
        return False
    return (
        _full_stat_binding(named) == expected_binding
        and _full_stat_binding(opened) == expected_binding
        and _full_stat_binding(after) == expected_binding
    )


class _BoundGitReadArguments(list[str]):
    """Fixed Git arguments paired with the snapshot's private directory proof."""

    def __init__(self, arguments: list[str], git_directory: tuple[str, tuple[int, ...]]) -> None:
        super().__init__(arguments)
        self.git_directory = git_directory


def _bounded_git_read(
    executable: str, executable_authority: dict[str, Any], root: str,
    arguments: list[str], *, deadline: float, payload: bytes = b"",
    allowed: tuple[int, ...] = (0,), stdout_limit: int | None = None,
) -> tuple[int, bytes] | None:
    """Run one allowlisted Git read under a bounded, owned process group.

    A private supervisor remains the session leader after Git exits, so the
    group identity is still signalable while a Git descendant holds stdout or
    stderr open.  Both streams are consumed incrementally with hard caps; all
    exits kill the group before a bounded reap and close every parent pipe.
    """
    if (
        not _fixed_git_read_argv(arguments)
        or not isinstance(payload, bytes)
        or len(payload) > MAX_STREAM_BYTES
        or not allowed
        or any(type(code) is not int or not (0 <= code <= 255) for code in allowed)
    ):
        return None
    output_limit = MAX_STREAM_BYTES if stdout_limit is None else stdout_limit
    if type(output_limit) is not int or not (0 <= output_limit <= MAX_STREAM_BYTES):
        return None
    git_directory = None
    if type(arguments) is _BoundGitReadArguments:
        git_directory = arguments.git_directory
        if (
            type(git_directory) is not tuple
            or len(git_directory) != 2
        ):
            return None
    git_options = () if git_directory is None else (
        f"--git-dir={git_directory[0]}", f"--work-tree={root}",
    )
    target_binding = tuple(executable_authority.get("target", ()))
    if len(target_binding) != 9:
        return None

    def executable_is_bound() -> bool:
        try:
            return bool(
                _confirm_safe_git_executable(executable, executable_authority)
                and _full_stat_binding(os.lstat(executable)) == target_binding
            )
        except OSError:
            return False

    def git_directory_is_bound() -> bool:
        return git_directory is None or _bound_git_directory(*git_directory)

    if not executable_is_bound() or time.monotonic() >= deadline:
        return None
    environment = os.environ.copy()
    for key in tuple(environment):
        if key.startswith("GIT_"):
            environment.pop(key)
    environment.update({
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_PAGER": "cat",
        "GIT_EXTERNAL_DIFF": "",
    })

    status_read = status_write = control_read = control_write = -1
    payload_read = payload_write = -1
    process: subprocess.Popen[bytes] | None = None
    launched = False
    try:
        status_read, status_write = os.pipe()
        control_read, control_write = os.pipe()
        payload_read, payload_write = os.pipe()
        # The supervisor owns the process group and deliberately outlives its
        # Git child.  Closing its copies of both output streams means any open
        # pipe after Git exits belongs to a descendant that the group kill must
        # close, rather than to the supervisor itself.
        supervisor = (
            'status_fd=$1; control_fd=$2; payload_fd=$3; shift 3; '
            '"$@" <&"$payload_fd" & child=$!; exec 1>&- 2>&-; '
            'wait "$child"; code=$?; printf "%s\\n" "$code" >&"$status_fd"; '
            'IFS= read -r _ <&"$control_fd"; exit "$code"'
        )
        if not executable_is_bound() or not git_directory_is_bound() or time.monotonic() >= deadline:
            return None
        process = subprocess.Popen(
            [
                "/bin/sh", "-c", supervisor, "bounded-git-supervisor",
                str(status_write), str(control_read), str(payload_read),
                executable, "-C", root, "-c", "core.fsmonitor=false",
                "-c", "core.hooksPath=/dev/null", *git_options, *arguments,
            ],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=environment,
            pass_fds=(status_write, control_read, payload_read),
            start_new_session=True,
        )
        launched = True
    except OSError:
        return None
    finally:
        for descriptor in (status_write, control_read, payload_read):
            if descriptor >= 0:
                os.close(descriptor)
        if not launched:
            for descriptor in (status_read, control_write, payload_write):
                if descriptor >= 0:
                    os.close(descriptor)
            status_read = control_write = payload_write = -1

    selector = selectors.DefaultSelector()
    output = bytearray()
    diagnostic_bytes = 0
    status = bytearray()
    sent = 0
    group_terminated = False
    reaped = False
    status_code: int | None = None
    try:
        assert process is not None
        assert process.stdout is not None and process.stderr is not None
        for stream in (process.stdout, process.stderr):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ)
        os.set_blocking(status_read, False)
        selector.register(status_read, selectors.EVENT_READ)
        if payload:
            os.set_blocking(payload_write, False)
            selector.register(payload_write, selectors.EVENT_WRITE)
        else:
            os.close(payload_write)
            payload_write = -1
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            ready = selector.select(remaining)
            if not ready:
                return None
            for key, events in ready:
                if events & selectors.EVENT_READ:
                    if key.fileobj == status_read:
                        piece = os.read(status_read, 33 - len(status))
                        if not piece:
                            return None
                        status.extend(piece)
                        if len(status) > 32 or b"\n" not in status:
                            continue
                        if (
                            status.count(b"\n") != 1 or not status.endswith(b"\n")
                            or not status[:-1].isdigit()
                        ):
                            return None
                        status_code = int(status[:-1])
                        selector.unregister(status_read)
                        os.close(status_read)
                        status_read = -1
                    elif key.fileobj is process.stdout:
                        amount = min(65536, output_limit + 1 - len(output))
                        piece = os.read(process.stdout.fileno(), amount)
                        if not piece:
                            selector.unregister(process.stdout)
                        else:
                            output.extend(piece)
                            if len(output) > output_limit:
                                return None
                    else:
                        amount = min(65536, MAX_STREAM_BYTES + 1 - diagnostic_bytes)
                        piece = os.read(process.stderr.fileno(), amount)
                        if not piece:
                            selector.unregister(process.stderr)
                        else:
                            diagnostic_bytes += len(piece)
                            if diagnostic_bytes > MAX_STREAM_BYTES:
                                return None
                if events & selectors.EVENT_WRITE:
                    if sent == len(payload):
                        selector.unregister(key.fileobj)
                        os.close(payload_write)
                        payload_write = -1
                    else:
                        sent += os.write(payload_write, payload[sent:])
        if status_code is None or not executable_is_bound():
            return None
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            return None
        group_terminated = True
        process.wait(timeout=TERM_GRACE)
        reaped = True
        if status_code not in allowed or not executable_is_bound():
            return None
        return status_code, bytes(output)
    except (OSError, subprocess.SubprocessError):
        return None
    finally:
        selector.close()
        if control_write >= 0:
            # Unblock an intact supervisor before the final group/reap guard.
            os.close(control_write)
            control_write = -1
        if payload_write >= 0:
            os.close(payload_write)
            payload_write = -1
        if process is not None and not group_terminated:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(process.pid, signal.SIGKILL)
        try:
            if process is not None and not reaped:
                process.wait(timeout=TERM_GRACE)
        except subprocess.SubprocessError:
            pass
        if status_read >= 0:
            os.close(status_read)
        if process is not None:
            for stream in (process.stdout, process.stderr):
                if stream is not None and not stream.closed:
                    stream.close()


def _git_boundary_identity(workdir: str) -> dict[str, Any] | None:
    """Return the V9 no-follow Git administration boundary for ``workdir``.

    This intentionally records repository *authority*, not repository state:
    no index, HEAD, ref, object, worktree-file, timestamp, directory-size, or
    link-count data reaches the returned mapping.  It is shared by the root
    binder and the candidate/worktree scanner, so those paths use one stable
    definition of a repository boundary.
    """
    root_fd = -1
    try:
        if not os.path.isabs(workdir):
            return None
        root = os.path.realpath(workdir)
        if MODEL_SELECTION._canonical_executable_path(root) != (
            MODEL_SELECTION._canonical_executable_path(workdir)
        ):
            return None
        named_root = os.lstat(workdir)
        if not stat.S_ISDIR(named_root.st_mode) or stat.S_ISLNK(named_root.st_mode):
            return None
        root_fd = os.open(
            os.fsencode(workdir),
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        opened_root = os.fstat(root_fd)
        root_binding = _full_stat_binding(opened_root)
        if _full_stat_binding(named_root) != root_binding:
            return None
        deadline = time.monotonic() + 5.0
        try:
            if not _marker_only_preflight(root_fd, deadline=deadline):
                return None
        except _MarkerPreflightLimit:
            return None

        def marker() -> dict[str, Any] | None:
            """Open the exact root marker once, never following it."""
            descriptor = -1
            try:
                before = os.stat(".git", dir_fd=root_fd, follow_symlinks=False)
                if stat.S_ISDIR(before.st_mode):
                    kind = "directory"
                    descriptor = os.open(
                        ".git", os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd,
                    )
                    payload_sha = None
                    payload_size = 0
                elif stat.S_ISREG(before.st_mode) and before.st_size <= 8192:
                    kind = "file"
                    descriptor = os.open(
                        ".git", os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd,
                    )
                    chunks: list[bytes] = []
                    total = 0
                    while True:
                        piece = os.read(descriptor, min(8193 - total, 8192))
                        if not piece:
                            break
                        chunks.append(piece)
                        total += len(piece)
                        if total > 8192:
                            return None
                    payload_sha = digest(b"".join(chunks))
                    payload_size = total
                else:
                    return None
                opened = os.fstat(descriptor)
                after = os.stat(".git", dir_fd=root_fd, follow_symlinks=False)
            except OSError:
                return None
            finally:
                if descriptor >= 0:
                    os.close(descriptor)
            if (
                _full_stat_binding(before) != _full_stat_binding(opened)
                or _full_stat_binding(opened) != _full_stat_binding(after)
                or (kind == "directory" and not stat.S_ISDIR(opened.st_mode))
                or (kind == "file" and (
                    not stat.S_ISREG(opened.st_mode)
                    or payload_sha is None
                    or opened.st_size != payload_size
                ))
            ):
                return None
            return {
                "kind": kind,
                "authority": _stable_git_authority(opened),
                "content_sha256": payload_sha,
            }

        initial_marker = marker()
        if initial_marker is None:
            return None
        safe_git = _safe_git_executable()
        if safe_git is None:
            return None
        executable, executable_authority = safe_git
        if not _safe_git_is_outside_worktree(executable, root):
            # Repository-controlled programs are outside the read-only probe
            # authority even when their mode and parent ownership look safe.
            return None

        def read_plumbing(arguments: list[str]) -> bytes | None:
            """Use fixed read-only plumbing with the snapshot's Git guards."""
            completed = _bounded_git_read(
                executable, executable_authority, root, arguments,
                deadline=deadline,
            )
            return None if completed is None else completed[1]

        def one_line(raw: bytes) -> str | None:
            if not raw.endswith(b"\n") or raw.count(b"\n") != 1 or b"\0" in raw:
                return None
            try:
                text = os.fsdecode(raw[:-1])
            except UnicodeError:
                return None
            return text if text else None

        def directory(
            path_text: str, *, allow_root_relative: bool = False,
        ) -> tuple[str, dict[str, int]] | None:
            """Bind a direct Git authority, allowing only macOS's /var alias."""
            if not os.path.isabs(path_text) and not allow_root_relative:
                return None
            named_path = os.path.abspath(
                path_text if os.path.isabs(path_text) else os.path.join(root, path_text)
            )
            try:
                named = os.lstat(os.fsencode(named_path))
                if not stat.S_ISDIR(named.st_mode) or stat.S_ISLNK(named.st_mode):
                    return None
                resolved_path = os.path.realpath(named_path)
                # ``realpath`` may change only macOS's documented /var
                # spelling.  An arbitrary outward symlink remains a boundary
                # failure even if its target happens to be a Git directory.
                if MODEL_SELECTION._canonical_executable_path(resolved_path) != (
                    MODEL_SELECTION._canonical_executable_path(named_path)
                ):
                    return None
                descriptor = os.open(
                    os.fsencode(named_path), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                )
                try:
                    opened = os.fstat(descriptor)
                finally:
                    os.close(descriptor)
                after = os.lstat(os.fsencode(named_path))
            except OSError:
                return None
            if (
                _full_stat_binding(named) != _full_stat_binding(opened)
                or _full_stat_binding(opened) != _full_stat_binding(after)
            ):
                return None
            return resolved_path, _stable_git_authority(opened)

        inside = read_plumbing(["rev-parse", "--is-inside-work-tree"])
        top_level = read_plumbing(["rev-parse", "--show-toplevel"])
        object_format = read_plumbing(["rev-parse", "--show-object-format"])
        git_dir_raw = read_plumbing(["rev-parse", "--absolute-git-dir"])
        common_dir_raw = read_plumbing(["rev-parse", "--git-common-dir"])
        if (
            inside != b"true\n"
            or not _bound_git_worktree_root(top_level, root, root_binding)
            or object_format not in {b"sha1\n", b"sha256\n"}
            or git_dir_raw is None or common_dir_raw is None
        ):
            return None
        git_dir_text = one_line(git_dir_raw)
        common_dir_text = one_line(common_dir_raw)
        if git_dir_text is None or common_dir_text is None:
            return None
        git_dir = directory(git_dir_text)
        common_dir = directory(common_dir_text, allow_root_relative=True)
        if git_dir is None or common_dir is None:
            return None
        final_marker = marker()
        if (
            final_marker != initial_marker
            or _full_stat_binding(os.fstat(root_fd)) != root_binding
            or _full_stat_binding(os.lstat(workdir)) != root_binding
            or (final_top_level := read_plumbing(["rev-parse", "--show-toplevel"])) != top_level
            or not _bound_git_worktree_root(final_top_level, root, root_binding)
            or read_plumbing(["rev-parse", "--show-object-format"]) != object_format
            or read_plumbing(["rev-parse", "--absolute-git-dir"]) != git_dir_raw
            or read_plumbing(["rev-parse", "--git-common-dir"]) != common_dir_raw
            or directory(git_dir_text) != git_dir
            or directory(common_dir_text, allow_root_relative=True) != common_dir
        ):
            return None
        return {
            "root": {"realpath": root, "dev": opened_root.st_dev, "ino": opened_root.st_ino},
            "git_marker": initial_marker,
            "git_dir": {"realpath": git_dir[0], "authority": git_dir[1]},
            "common_dir": {"realpath": common_dir[0], "authority": common_dir[1]},
            "object_format": object_format[:-1].decode("ascii"),
            "show_toplevel": root,
        }
    except (OSError, UnicodeError, ValueError, OverflowError):
        return None
    finally:
        if root_fd >= 0:
            os.close(root_fd)


def _worktree_snapshot(
    workdir: str, *, legacy: bool = False, explain_unsupported: bool = False,
) -> dict[str, Any] | None:
    """Hash a bounded worktree fact set without executing repository programs.

    This deliberately avoids ``status``, diff, attributes' clean/textconv
    filters, hooks, and external commands.  Read-only index/object plumbing
    provides the tracked baseline; files are opened relative to a no-follow
    root descriptor, so symlinks contribute their own target bytes only.  The
    persisted v7 form deliberately excludes volatile inode/timestamp/cache
    details; the complete bindings below remain in this one scan to detect
    replacement and TOCTOU races.  ``legacy`` retains the exact v6 digest
    algorithm for already-persisted v6 state only.
    """
    root_fd = -1
    try:
        if not os.path.isabs(workdir):
            return None
        root = os.path.realpath(workdir)
        root_fd = os.open(
            os.fsencode(workdir),
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        root_info = os.fstat(root_fd)
        if not stat.S_ISDIR(root_info.st_mode):
            return None

        def binding(info: os.stat_result) -> tuple[int, ...]:
            return (
                info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
                info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns, info.st_ctime_ns,
            )

        def authority(value: tuple[int, ...]) -> tuple[int, int, int, int, int]:
            """Project stable identity out of a full in-call race binding."""
            return value[0], value[1], value[4], value[5], stat.S_IMODE(value[2])

        def persistent_metadata(value: tuple[int, ...]) -> tuple[int, ...]:
            """Persist semantic file shape while retaining full race bindings."""
            if not value:
                return value
            if legacy:
                return value
            return stat.S_IFMT(value[2]), stat.S_IMODE(value[2])

        root_binding = binding(root_info)
        if binding(os.lstat(workdir)) != root_binding:
            return None
        # Do not start Git plumbing until a no-follow, marker-only traversal
        # established that the sole marker has the exact root spelling.  The
        # complete directory manifest below repeats the check as its later
        # bounded timing-consistency observation.
        deadline = time.monotonic() + 5.0
        try:
            marker_preflight = _marker_only_preflight(root_fd, deadline=deadline)
        except _MarkerPreflightLimit:
            return None
        if not marker_preflight:
            return None
        if not _worktree_git_admin_alias_boundary(root):
            return None

        def git_marker_binding() -> tuple[bytes, tuple[int, ...], bytes] | None:
            """Bind the root .git marker without following it or its contents."""
            try:
                before = os.stat(".git", dir_fd=root_fd, follow_symlinks=False)
                if stat.S_ISDIR(before.st_mode):
                    descriptor = os.open(
                        ".git", os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd,
                    )
                    kind = b"directory"
                    payload = b""
                elif stat.S_ISREG(before.st_mode) and before.st_size <= 8192:
                    descriptor = os.open(
                        ".git", os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd,
                    )
                    kind = b"file"
                else:
                    return None
                try:
                    if kind == b"file":
                        chunks: list[bytes] = []
                        size = 0
                        while True:
                            piece = os.read(descriptor, min(8193 - size, 8192))
                            if not piece:
                                break
                            chunks.append(piece); size += len(piece)
                            if size > 8192:
                                return None
                        payload = b"".join(chunks)
                    opened = os.fstat(descriptor)
                finally:
                    os.close(descriptor)
                named = os.stat(".git", dir_fd=root_fd, follow_symlinks=False)
            except OSError:
                return None
            if (
                binding(before) != binding(opened) or binding(opened) != binding(named)
                or (kind == b"directory" and not stat.S_ISDIR(opened.st_mode))
                or (kind == b"file" and (not stat.S_ISREG(opened.st_mode) or len(payload) != opened.st_size))
            ):
                return None
            return kind, binding(opened), hashlib.sha256(payload).digest()

        root_git_marker = git_marker_binding()
        if root_git_marker is None:
            return None
        safe_git = _safe_git_executable()
        if safe_git is None:
            return None
        target, target_authority = safe_git
        if not _safe_git_is_outside_worktree(target, root):
            return None
        target_binding = tuple(target_authority["target"])
        total = 0

        def git_read(
            arguments: list[str], payload: bytes = b"", *, allowed: tuple[int, ...] = (0,),
        ) -> tuple[int, bytes] | None:
            """Read fixed Git plumbing with no filters, hooks, fetches, or locks."""
            nonlocal total
            completed = _bounded_git_read(
                target, target_authority, root, arguments, payload=payload,
                allowed=allowed, deadline=deadline,
                stdout_limit=MAX_STREAM_BYTES - total,
            )
            if completed is None:
                return None
            total += len(completed[1])
            return completed

        def one_path(raw: bytes, *, resolve: bool = True) -> str | None:
            if not raw.endswith(b"\n") or raw.count(b"\n") != 1 or b"\0" in raw:
                return None
            value = os.fsdecode(raw[:-1])
            if not value:
                return None
            path = value if os.path.isabs(value) else os.path.join(root, value)
            return os.path.realpath(path) if resolve else os.path.abspath(path)

        def directory_boundary(path: str) -> tuple[str, tuple[int, ...]] | None:
            """Bind a direct Git directory without accepting arbitrary aliases."""
            if not os.path.isabs(path):
                return None
            named_path = os.path.abspath(path)
            try:
                named = os.lstat(os.fsencode(named_path))
                if not stat.S_ISDIR(named.st_mode) or stat.S_ISLNK(named.st_mode):
                    return None
                canonical_path = os.path.realpath(named_path)
                if MODEL_SELECTION._canonical_executable_path(canonical_path) != (
                    MODEL_SELECTION._canonical_executable_path(named_path)
                ):
                    return None
                descriptor = os.open(
                    os.fsencode(named_path), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                )
                try:
                    opened = os.fstat(descriptor)
                finally:
                    os.close(descriptor)
                after = os.lstat(os.fsencode(named_path))
            except OSError:
                return None
            if (
                binding(named) != binding(opened)
                or binding(opened) != binding(after)
            ):
                return None
            return canonical_path, binding(opened)

        def index_binding(path: str) -> tuple[bytes | None, tuple[int, ...] | None] | None:
            try:
                descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            except FileNotFoundError:
                return (None, None)
            except OSError:
                return None
            try:
                before = os.fstat(descriptor)
                if not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode) or before.st_size > MAX_STREAM_BYTES:
                    return None
                chunks: list[bytes] = []
                total_bytes = 0
                while True:
                    piece = os.read(descriptor, min(65536, MAX_STREAM_BYTES + 1 - total_bytes))
                    if not piece:
                        break
                    chunks.append(piece)
                    total_bytes += len(piece)
                    if total_bytes > MAX_STREAM_BYTES:
                        return None
                after = os.fstat(descriptor)
            finally:
                os.close(descriptor)
            try:
                named = os.lstat(path)
            except OSError:
                return None
            if binding(before) != binding(after) or binding(after) != binding(named):
                return None
            return b"".join(chunks), binding(after)

        def bound_git_worktree() -> bool:
            """Require Git's configured worktree to remain this held root.

            ``-C`` only chooses Git's process directory: a local
            ``core.worktree`` can otherwise redirect plumbing enumeration.  The
            initial and final fixed rev-parse facts therefore bind the context
            before it is passed directly to every enumeration below.
            """
            inside = git_read(["rev-parse", "--is-inside-work-tree"])
            top_level = git_read(["rev-parse", "--show-toplevel"])
            return (
                inside is not None and inside[1] == b"true\n"
                and top_level is not None
                and _bound_git_worktree_root(top_level[1], root, root_binding)
            )

        def bound_git_read(
            arguments: list[str], payload: bytes = b"", *, allowed: tuple[int, ...] = (0,),
        ) -> tuple[int, bytes] | None:
            """Use the no-follow-bound Git directory and held worktree root.

            The initial bare root proof rejects a configured redirected
            worktree.  The bounded reader then derives command-line global
            options from this exact Git-directory authority and held root;
            arbitrary argument lists cannot override either.  The final bare
            proof fails closed if repository configuration drifts during the
            scan.
            """
            return git_read(
                _BoundGitReadArguments(arguments, git_dir_boundary), payload, allowed=allowed,
            )

        if not bound_git_worktree():
            return None

        format_result = git_read(["rev-parse", "--show-object-format"])
        if format_result is None or format_result[1] not in {b"sha1\n", b"sha256\n"}:
            return None
        object_length = 40 if format_result[1] == b"sha1\n" else 64
        git_dir_result = git_read(["rev-parse", "--absolute-git-dir"])
        if git_dir_result is None:
            return None
        git_dir_path = one_path(git_dir_result[1], resolve=False)
        if git_dir_path is None:
            return None
        git_dir_boundary = directory_boundary(git_dir_path)
        if git_dir_boundary is None:
            return None
        index_path_result = git_read(["rev-parse", "--git-path", "index"])
        if index_path_result is None:
            return None
        index_path = one_path(index_path_result[1], resolve=False)
        if index_path is None:
            return None
        before_index = index_binding(index_path)
        if before_index is None:
            return None
        common_path_result = git_read(["rev-parse", "--git-common-dir"])
        if common_path_result is None:
            return None
        common_path = one_path(common_path_result[1], resolve=False)
        if common_path is None:
            return None
        common_dir_boundary = directory_boundary(common_path)
        if common_dir_boundary is None:
            return None
        for alternate_name in ("alternates", "http-alternates"):
            try:
                os.lstat(os.path.join(common_path, "objects", "info", alternate_name))
                return None
            except FileNotFoundError:
                pass
            except OSError:
                return None
        promisor = bound_git_read(
            ["config", "--local", "--no-includes", "--get-regexp", "^(extensions\\.partialclone|remote\\..*\\.promisor)$"],
            allowed=(0, 1),
        )
        sparse = bound_git_read(["config", "--bool", "--get", "core.sparseCheckout"], allowed=(0, 1))
        if promisor is None or sparse is None:
            return None
        if promisor[0] == 0 and promisor[1]:
            if explain_unsupported:
                raise _UnsupportedWorktreeError(
                    "partial/promisor Git clones are unsupported; use a full clone"
                )
            return None
        if (promisor[0] == 1 and promisor[1]) or (sparse[0] == 0 and sparse[1] != b"false\n") or (sparse[0] == 1 and sparse[1]):
            return None
        skip = bound_git_read(["ls-files", "-v", "-z"])
        if skip is None or (skip[1] and not skip[1].endswith(b"\0")):
            return None
        if any(
            len(record) < 3 or record[1:2] != b" " or record.startswith(b"S ") or record[:1].islower()
            for record in skip[1].split(b"\0")[:-1]
        ):
            return None

        def listings() -> tuple[bytes, bytes, bytes, bytes, bytes, bytes] | None:
            head_id = bound_git_read(["rev-parse", "--verify", "-q", "HEAD^{tree}"], allowed=(0, 1))
            staged = bound_git_read(["ls-files", "--stage", "-z"])
            debug = None if legacy else bound_git_read(["ls-files", "--debug", "-z"])
            resolve_undo = None if legacy else bound_git_read(["ls-files", "--resolve-undo", "-z"])
            other = bound_git_read(["ls-files", "-z", "--others", "--exclude-standard"])
            ignored = bound_git_read(["ls-files", "-z", "--others", "--ignored", "--exclude-standard"])
            if (
                head_id is None or staged is None or (not legacy and debug is None)
                or (not legacy and resolve_undo is None) or other is None or ignored is None
            ):
                return None
            if not legacy:
                parsed_resolve_undo = _parse_resolve_undo(resolve_undo[1], object_length)  # type: ignore[index]
                if parsed_resolve_undo is None or parsed_resolve_undo:
                    if explain_unsupported and parsed_resolve_undo:
                        second_resolve_undo = bound_git_read(["ls-files", "--resolve-undo", "-z"])
                        if (
                            second_resolve_undo is not None
                            and second_resolve_undo[1] == resolve_undo[1]
                            and index_binding(index_path) == before_index
                            and _parse_resolve_undo(second_resolve_undo[1], object_length) == parsed_resolve_undo
                        ):
                            raise _ResolveUndoPresentError("resolve_undo_present")
                    return None
            if head_id[0] == 1:
                if head_id[1]:
                    return None
                head = b""
            elif len(head_id[1]) == object_length + 1 and head_id[1].endswith(b"\n"):
                oid = head_id[1][:-1]
                if any(char not in b"0123456789abcdef" for char in oid):
                    return None
                tree = bound_git_read(["ls-tree", "-r", "-z", oid.decode("ascii")])
                if tree is None:
                    return None
                head = tree[1]
            else:
                return None
            values = (head, staged[1], other[1], ignored[1])
            if any(raw and not raw.endswith(b"\0") for raw in values):
                return None
            return values[0], values[1], b"" if debug is None else debug[1], values[2], values[3], head_id[1]

        first = listings()
        if first is None:
            return None
        head_raw, staged_raw, debug_raw, other_raw, ignored_raw, head_id_raw = first

        def valid_oid(value: bytes) -> bool:
            return len(value) == object_length and not any(char not in b"0123456789abcdef" for char in value)

        def parse_tree(raw: bytes) -> dict[bytes, tuple[int, bytes]] | None:
            parsed: dict[bytes, tuple[int, bytes]] = {}
            for record in raw.split(b"\0")[:-1]:
                try:
                    header, relative = record.split(b"\t", 1)
                    mode_raw, kind, oid = header.split(b" ")
                    mode = int(mode_raw, 8)
                except (ValueError, TypeError):
                    return None
                if kind != b"blob" or mode not in {0o100644, 0o100755, 0o120000} or not valid_oid(oid) or relative in parsed:
                    return None
                parsed[relative] = (mode, oid)
            return parsed

        def parse_index(raw: bytes) -> dict[bytes, tuple[int, bytes]] | None:
            parsed: dict[bytes, tuple[int, bytes]] = {}
            for record in raw.split(b"\0")[:-1]:
                try:
                    header, relative = record.split(b"\t", 1)
                    mode_raw, oid, stage_raw = header.split(b" ")
                    mode = int(mode_raw, 8)
                except (ValueError, TypeError):
                    return None
                if stage_raw != b"0" or mode not in {0o100644, 0o100755, 0o120000} or not valid_oid(oid) or relative in parsed:
                    return None
                parsed[relative] = (mode, oid)
            return parsed

        def debug_index_flags(raw: bytes) -> dict[bytes, int] | None:
            """Read documented ls-files debug flags, ignoring volatile stat cache.

            The debug record's pathname is NUL-delimited; its preceding stat
            cache lines are intentionally only shape-checked.  Flags are the
            semantic portion: unsupported nonzero values, including
            CE_INTENT_TO_ADD, reject rather than silently sharing an OID/mode
            digest with a different index meaning.
            """
            parsed: dict[bytes, int] = {}
            position = 0
            while position < len(raw):
                separator = raw.find(b"\0", position)
                if separator < position:
                    return None
                relative = raw[position:separator]
                position = separator + 1
                lines: list[bytes] = []
                for _ in range(5):
                    ending = raw.find(b"\n", position)
                    if ending < position:
                        return None
                    lines.append(raw[position:ending + 1])
                    position = ending + 1
                if not relative or relative in parsed or any(
                    re.fullmatch(shape, line) is None
                    for shape, line in zip((
                        br"  ctime: [0-9]+:[0-9]+\n",
                        br"  mtime: [0-9]+:[0-9]+\n",
                        br"  dev: [0-9]+\tino: [0-9]+\n",
                        br"  uid: [0-9]+\tgid: [0-9]+\n",
                    ), lines[:4])
                ):
                    return None
                flags = re.fullmatch(br"  size: [0-9]+\tflags: ([0-9a-f]+)\n", lines[4])
                if flags is None:
                    return None
                try:
                    parsed[relative] = int(flags.group(1), 16)
                except ValueError:
                    return None
            return parsed

        head = parse_tree(head_raw)
        staged = parse_index(staged_raw)
        flags = {} if legacy else debug_index_flags(debug_raw)
        if head is None or staged is None or flags is None:
            return None
        if not legacy and (set(flags) != set(staged) or any(value != 0 for value in flags.values())):
            return None
        other = set(other_raw.split(b"\0")[:-1])
        ignored = set(ignored_raw.split(b"\0")[:-1])
        if other & ignored or len(head) + len(staged) + len(other) + len(ignored) > MAX_BOUNDARY_ENTRIES:
            return None
        object_ids = sorted({oid for _mode, oid in staged.values()})
        objects_raw = bound_git_read(["cat-file", "--batch"], b"".join(item + b"\n" for item in object_ids))
        if objects_raw is None:
            return None
        objects: dict[bytes, bytes] = {}
        position = 0
        while position < len(objects_raw[1]):
            end = objects_raw[1].find(b"\n", position)
            if end < 0:
                return None
            fields = objects_raw[1][position:end].split(b" ")
            if len(fields) != 3 or fields[0] not in object_ids or fields[1] != b"blob":
                return None
            try:
                size = int(fields[2])
            except ValueError:
                return None
            start = end + 1
            finish = start + size
            if size < 0 or finish >= len(objects_raw[1]) or objects_raw[1][finish:finish + 1] != b"\n" or fields[0] in objects:
                return None
            objects[fields[0]] = objects_raw[1][start:finish]
            position = finish + 1
        if len(objects) != len(object_ids):
            return None

        nofollow = getattr(os, "O_NOFOLLOW", 0)
        directory = getattr(os, "O_DIRECTORY", 0)

        def directory_manifest() -> tuple[bytes, int] | None:
            """Bind bounded topology and count otherwise-unlisted empty directories."""
            manifest_bytes = 0
            manifest_entries = 0
            empty_directories = 0

            def walk(parent_fd: int, *, is_root: bool = False) -> bytes | None:
                nonlocal manifest_bytes, manifest_entries, empty_directories
                if time.monotonic() >= deadline:
                    return None
                before_directory = os.fstat(parent_fd)
                if not stat.S_ISDIR(before_directory.st_mode):
                    return None
                records: list[tuple[bytes, bytes, tuple[int, ...], bytes]] = []
                scan_fd = -1
                try:
                    # scandir does not own a caller-supplied descriptor on the
                    # supported runtimes, so retain and close this duplicate in
                    # our own finally path even if scandir rejects it.
                    scan_fd = os.dup(parent_fd)
                    with os.scandir(scan_fd) as scanned:
                        for entry in scanned:
                            if time.monotonic() >= deadline:
                                return None
                            name = entry.name
                            raw_name = os.fsencode(name)
                            if not raw_name or b"\0" in raw_name:
                                continue
                            if raw_name.lower() == b".git":
                                # Only the root marker was bound separately.
                                # Do not open or traverse a nested marker.
                                if is_root and raw_name == b".git":
                                    continue
                                return None
                            manifest_entries += 1
                            if manifest_entries > MAX_BOUNDARY_ENTRIES:
                                return None
                            try:
                                info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                            except OSError:
                                return None
                            metadata = binding(info)
                            if stat.S_ISDIR(info.st_mode):
                                try:
                                    child_fd = os.open(name, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd)
                                except OSError:
                                    return None
                                try:
                                    if binding(os.fstat(child_fd)) != metadata:
                                        return None
                                    payload = walk(child_fd)
                                    if payload is None or binding(os.fstat(child_fd)) != metadata:
                                        return None
                                finally:
                                    os.close(child_fd)
                                kind = b"directory"
                            elif stat.S_ISLNK(info.st_mode):
                                try:
                                    target_raw = os.fsencode(os.readlink(name, dir_fd=parent_fd))
                                    named = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                                except OSError:
                                    return None
                                manifest_bytes += len(target_raw)
                                if manifest_bytes > MAX_STREAM_BYTES or binding(named) != metadata:
                                    return None
                                payload = hashlib.sha256(target_raw).digest()
                                kind = b"symlink"
                            elif stat.S_ISREG(info.st_mode):
                                # Regular bytes and metadata are bound by the
                                # primary listed-path observation and its final
                                # revalidation.  This second pass is topology
                                # only, so it never re-reads file contents.
                                metadata = ()
                                payload = b""
                                kind = b"file"
                            else:
                                metadata = ()
                                payload = b""
                                kind = b"special"
                            records.append((raw_name, kind, persistent_metadata(metadata), payload))
                except OSError:
                    return None
                finally:
                    if scan_fd >= 0:
                        os.close(scan_fd)
                try:
                    if binding(os.fstat(parent_fd)) != binding(before_directory):
                        return None
                except OSError:
                    return None
                result = hashlib.sha256()
                result.update(b"agy-worker-directory-manifest-v1\0")
                for raw_name, kind, metadata, payload in sorted(records):
                    result.update(len(raw_name).to_bytes(8, "big")); result.update(raw_name)
                    result.update(len(kind).to_bytes(8, "big")); result.update(kind)
                    metadata_raw = canonical(list(metadata))
                    result.update(len(metadata_raw).to_bytes(8, "big")); result.update(metadata_raw)
                    result.update(len(payload).to_bytes(8, "big")); result.update(payload)
                if not is_root and not records:
                    empty_directories += 1
                return result.digest()

            manifest = walk(root_fd, is_root=True)
            if manifest is None:
                return None
            return manifest, empty_directories

        observation = hashlib.sha256()
        observation.update(b"agy-worker-worktree-v5\0" if legacy else b"agy-worker-worktree-v7\0")
        canonical_root = os.fsencode(root)
        observation.update(len(canonical_root).to_bytes(8, "big")); observation.update(canonical_root)
        observation.update(canonical([root_info.st_dev, root_info.st_ino]))
        observation.update(canonical([
            os.fsdecode(root_git_marker[0]), list(authority(root_git_marker[1])),
            root_git_marker[2].hex(),
        ]))
        observation.update(canonical([
            git_dir_boundary[0], list(authority(git_dir_boundary[1])),
            common_dir_boundary[0], list(authority(common_dir_boundary[1])),
            os.path.realpath(index_path) if legacy else None,
            None if before_index[0] is None else hashlib.sha256(before_index[0]).hexdigest() if legacy else None,
            None if before_index[1] is None else list(authority(before_index[1])) if legacy else None,
        ]))
        content_bytes = 0
        changed = 0
        observed_paths: dict[bytes, tuple[Any, ...]] = {}
        for relative in sorted(set(head) | set(staged) | other | ignored):
            parts = relative.split(b"/")
            if not relative or relative.startswith(b"/") or any(part in {b"", b".", b".."} for part in parts) or parts[0] == b".git":
                return None
            observation.update(len(relative).to_bytes(8, "big")); observation.update(relative)
            indexed = staged.get(relative)
            head_entry = head.get(relative)
            for label, entry in ((b"head", head_entry), (b"index", indexed)):
                observation.update(label + b"\0")
                if entry is None:
                    observation.update(b"missing\0")
                else:
                    observation.update(f"{entry[0]:o}".encode("ascii") + b"\0")
                    observation.update(entry[1])
            index_changed = indexed != head_entry
            is_other = relative in other or relative in ignored
            parent_fd = os.dup(root_fd)
            try:
                for component in parts[:-1]:
                    next_fd = os.open(component, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd)
                    os.close(parent_fd); parent_fd = next_fd
                name = parts[-1]
                try:
                    before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                except FileNotFoundError:
                    observation.update(b"missing\0")
                    observed_paths[relative] = (b"missing",)
                    differs = indexed is not None
                else:
                    metadata = binding(before); observation.update(canonical(list(persistent_metadata(metadata))))
                    if stat.S_ISLNK(before.st_mode):
                        target_raw = os.fsencode(os.readlink(name, dir_fd=parent_fd))
                        content_bytes += len(target_raw)
                        if content_bytes > MAX_STREAM_BYTES or binding(os.stat(name, dir_fd=parent_fd, follow_symlinks=False)) != metadata:
                            return None
                        observation.update(b"symlink\0"); observation.update(len(target_raw).to_bytes(8, "big")); observation.update(target_raw)
                        observed_paths[relative] = (b"symlink", metadata, target_raw)
                        differs = indexed is None or indexed[0] != 0o120000 or target_raw != objects[indexed[1]]
                    elif stat.S_ISREG(before.st_mode):
                        descriptor = os.open(name, os.O_RDONLY | nofollow, dir_fd=parent_fd)
                        try:
                            opened = os.fstat(descriptor)
                            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                                return None
                            content = hashlib.sha256()
                            while True:
                                piece = os.read(descriptor, 65536)
                                if not piece:
                                    break
                                content_bytes += len(piece)
                                if content_bytes > MAX_STREAM_BYTES:
                                    return None
                                content.update(piece)
                            after = os.fstat(descriptor)
                        finally:
                            os.close(descriptor)
                        if binding(after) != metadata or binding(os.stat(name, dir_fd=parent_fd, follow_symlinks=False)) != metadata:
                            return None
                        content_digest = content.digest()
                        observation.update(b"file\0"); observation.update(content_digest)
                        observed_paths[relative] = (b"file", metadata, content_digest)
                        differs = indexed is None or indexed[0] not in {0o100644, 0o100755} or bool(before.st_mode & 0o111) != bool(indexed[0] & 0o111) or before.st_size != len(objects[indexed[1]]) or content_digest != hashlib.sha256(objects[indexed[1]]).digest()
                    else:
                        observation.update(b"special\0")
                        observed_paths[relative] = (b"special", metadata)
                        differs = True
                if is_other or index_changed or differs:
                    changed += 1
            finally:
                os.close(parent_fd)
        initial_directory_observation = directory_manifest()
        if initial_directory_observation is None:
            return None
        initial_directory_manifest, initial_empty_directories = initial_directory_observation
        second = listings()
        if second is None or second != first or index_binding(index_path) != before_index:
            return None

        revalidated_bytes = 0
        for relative, expected in observed_paths.items():
            parts = relative.split(b"/")
            parent_fd = os.dup(root_fd)
            try:
                for component in parts[:-1]:
                    next_fd = os.open(component, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd)
                    os.close(parent_fd); parent_fd = next_fd
                name = parts[-1]
                try:
                    before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                except FileNotFoundError:
                    current: tuple[Any, ...] = (b"missing",)
                else:
                    metadata = binding(before)
                    if stat.S_ISLNK(before.st_mode):
                        target_raw = os.fsencode(os.readlink(name, dir_fd=parent_fd))
                        revalidated_bytes += len(target_raw)
                        if (
                            revalidated_bytes > MAX_STREAM_BYTES
                            or binding(os.stat(name, dir_fd=parent_fd, follow_symlinks=False)) != metadata
                        ):
                            return None
                        current = (b"symlink", metadata, target_raw)
                    elif stat.S_ISREG(before.st_mode):
                        descriptor = os.open(name, os.O_RDONLY | nofollow, dir_fd=parent_fd)
                        try:
                            opened = os.fstat(descriptor)
                            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                                return None
                            content = hashlib.sha256()
                            while True:
                                piece = os.read(descriptor, 65536)
                                if not piece:
                                    break
                                revalidated_bytes += len(piece)
                                if revalidated_bytes > MAX_STREAM_BYTES:
                                    return None
                                content.update(piece)
                            after = os.fstat(descriptor)
                        finally:
                            os.close(descriptor)
                        if (
                            binding(after) != metadata
                            or binding(os.stat(name, dir_fd=parent_fd, follow_symlinks=False)) != metadata
                        ):
                            return None
                        current = (b"file", metadata, content.digest())
                    else:
                        current = (b"special", metadata)
                if current != expected:
                    return None
            finally:
                os.close(parent_fd)
        third = listings()
        if (
            third is None
            or third != first
            or index_binding(index_path) != before_index
        ):
            return None
        # The second complete manifest is the bounded linearization point: all
        # Git/listing operations completed before it begins and it must equal
        # the first manifest. A same-UID mutation after an entry's final read
        # remains outside this finite observation and is a controller-TCB
        # residual, not a reason to alternate scans indefinitely.
        final_directory_observation = directory_manifest()
        if final_directory_observation is None:
            return None
        final_directory_manifest, final_empty_directories = final_directory_observation
        if (
            final_directory_manifest != initial_directory_manifest
            or final_empty_directories != initial_empty_directories
            or index_binding(index_path) != before_index
        ):
            return None
        if (
            os.path.realpath(workdir) != root
            or binding(os.fstat(root_fd)) != root_binding
            or binding(os.lstat(workdir)) != root_binding
            or git_marker_binding() != root_git_marker
            or directory_boundary(git_dir_path) != git_dir_boundary
            or directory_boundary(common_path) != common_dir_boundary
            or index_binding(index_path) != before_index
            or binding(os.lstat(target)) != target_binding
            or not bound_git_worktree()
        ):
            return None
        observation.update(b"directory-manifest-v1\0")
        observation.update(initial_directory_manifest)
        observation.update(initial_empty_directories.to_bytes(8, "big"))
        return {"sha256": observation.hexdigest(), "entries": changed + initial_empty_directories}
    except _UnsupportedWorktreeError:
        raise
    except (OSError, subprocess.TimeoutExpired, OverflowError, ValueError, RecursionError):
        return None
    finally:
        if root_fd >= 0:
            os.close(root_fd)


_IMPLEMENTATION_FUNCTIONS = frozenset({
    "_marker_only_preflight",
    "_resolved_path_is_git_administration",
    "_worktree_symlink_boundary",
    "_worktree_git_admin_alias_boundary",
    "_project_boundary",
    "_safe_git_owner_mode",
    "_safe_git_executable",
    "_confirm_safe_git_executable",
    "_safe_git_is_outside_worktree",
    "_stable_git_authority",
    "_full_stat_binding",
    "_bound_git_worktree_root",
    "_fixed_git_read_argv",
    "_bounded_git_read",
    "_git_boundary_identity",
    "_worktree_snapshot",
})
_IMPLEMENTATION_DEFAULTS = {
    name: globals()[name] for name in _IMPLEMENTATION_FUNCTIONS
}
