#!/usr/bin/env python3
"""macOS OS containment for selected-content and self-verification launches.

The dispatcher remains responsible for deciding whether a launch is scoped and
for binding the provider selection.  This module owns only the native launch
envelope: an owner-private profile, private provider state, a per-attempt temp
directory, and identity-safe process-group termination.

``sandbox-exec`` is a deprecated macOS interface.  The implementation therefore
binds the Darwin build and launcher bytes and fails closed everywhere else.  A
caller must re-run :func:`confirm_contained_launch` immediately before ``Popen``.

This primitive binds the stage directory, not its contents. The trusted dispatcher
must supply a freshly copied, no-hardlink stage and rebind its complete approved
manifest before launch. A pre-existing hardlink inside an allowed directory still
names the outside inode. It must also launch with DEVNULL stdin, private pipes for
stdout/stderr, close_fds=True and no pass_fds: an inherited open descriptor is not
revoked by a pathname sandbox. Neither prerequisite is proved by directory binding.
"""

from __future__ import annotations

import ctypes
import dataclasses
import hashlib
import os
from pathlib import Path
import platform
import signal
import stat
import sys
import time
from typing import Mapping, Sequence


SANDBOX_EXEC = Path("/usr/bin/sandbox-exec")
MAX_EXECUTABLE_BYTES = 512 * 1024 * 1024
MAX_PROFILE_BYTES = 64 * 1024
MAX_GROUP_MEMBERS = 4096
PROCESS_GROUP_CLEANUP_SCOPE = "bound-process-group-only"
ROLE_PROVIDER = "provider"
ROLE_SELF_VERIFY = "self-verify"
NETWORK_DENY_ALL = "deny-all"
NETWORK_PROVIDER_TLS = "provider-tls"
_ROLES = frozenset({ROLE_PROVIDER, ROLE_SELF_VERIFY})
_PROC_PIDTBSDINFO = 3
_MAXCOMLEN = 16


class ContainmentError(RuntimeError):
    """The scoped native launch boundary could not be established exactly."""


@dataclasses.dataclass(frozen=True)
class FileBinding:
    path: str
    device: int
    inode: int
    uid: int
    gid: int
    mode: int
    nlink: int
    size: int
    mtime_ns: int
    ctime_ns: int
    sha256: str | None


@dataclasses.dataclass(frozen=True)
class DirectoryBinding:
    path: str
    device: int
    inode: int
    uid: int
    gid: int
    mode: int
    nlink: int


@dataclasses.dataclass(frozen=True)
class ProcessIdentity:
    pid: int
    parent_pid: int
    process_group: int
    session_id: int
    uid: int
    start_seconds: int
    start_microseconds: int


@dataclasses.dataclass(frozen=True)
class PreparedContainedLaunch:
    role: str
    network_policy: str
    darwin_release: str
    darwin_version: str
    launcher: FileBinding
    target: FileBinding
    profile: FileBinding
    read_only_inputs: tuple[FileBinding, ...]
    stage: DirectoryBinding
    private_home: DirectoryBinding
    attempt_tmp: DirectoryBinding
    target_argv: tuple[str, ...]
    environment: tuple[tuple[str, str], ...]
    allow_keychain: bool


@dataclasses.dataclass(frozen=True)
class ConfirmedContainedLaunch:
    argv: tuple[str, ...]
    executable: str
    cwd: str
    environment: dict[str, str]


class _ProcBsdInfo(ctypes.Structure):
    _fields_ = [
        ("pbi_flags", ctypes.c_uint32),
        ("pbi_status", ctypes.c_uint32),
        ("pbi_xstatus", ctypes.c_uint32),
        ("pbi_pid", ctypes.c_uint32),
        ("pbi_ppid", ctypes.c_uint32),
        ("pbi_uid", ctypes.c_uint32),
        ("pbi_gid", ctypes.c_uint32),
        ("pbi_ruid", ctypes.c_uint32),
        ("pbi_rgid", ctypes.c_uint32),
        ("pbi_svuid", ctypes.c_uint32),
        ("pbi_svgid", ctypes.c_uint32),
        ("rfu_1", ctypes.c_uint32),
        ("pbi_comm", ctypes.c_char * _MAXCOMLEN),
        ("pbi_name", ctypes.c_char * (2 * _MAXCOMLEN)),
        ("pbi_nfiles", ctypes.c_uint32),
        ("pbi_pgid", ctypes.c_uint32),
        ("pbi_pjobc", ctypes.c_uint32),
        ("e_tdev", ctypes.c_uint32),
        ("e_tpgid", ctypes.c_uint32),
        ("pbi_nice", ctypes.c_int32),
        ("pbi_start_tvsec", ctypes.c_uint64),
        ("pbi_start_tvusec", ctypes.c_uint64),
    ]


def require_supported_host() -> None:
    """Reject unsupported hosts even when no check has been selected."""
    if sys.platform != "darwin" or platform.system() != "Darwin":
        raise ContainmentError("native launch containment requires macOS")


def _canonical_existing(path: str | Path) -> Path:
    candidate = Path(os.fsdecode(path))
    if not candidate.is_absolute() or "\0" in str(candidate):
        raise ContainmentError("containment path must be canonical and absolute")
    if Path(os.path.realpath(candidate)) != candidate:
        raise ContainmentError("containment path must not contain aliases")
    return candidate


def _read_hash(descriptor: int, limit: int) -> str:
    digest = hashlib.sha256()
    size = 0
    os.lseek(descriptor, 0, os.SEEK_SET)
    while True:
        chunk = os.read(descriptor, 1024 * 1024)
        if not chunk:
            break
        size += len(chunk)
        if size > limit:
            raise ContainmentError("containment executable or profile exceeds its byte limit")
        digest.update(chunk)
    return digest.hexdigest()


def _bind_file(
    path: str | Path, *, modes: set[int], executable: bool = False,
    limit: int = MAX_EXECUTABLE_BYTES, require_single_link: bool = True,
) -> FileBinding:
    candidate = _canonical_existing(path)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    try:
        named = os.lstat(candidate)
        descriptor = os.open(candidate, os.O_RDONLY | nofollow)
    except OSError as exc:
        raise ContainmentError("containment file is unavailable") from exc
    try:
        before = os.fstat(descriptor)
        mode = stat.S_IMODE(before.st_mode)
        identity = (
            before.st_dev, before.st_ino, before.st_uid, before.st_gid,
            before.st_mode, before.st_nlink, before.st_size,
            before.st_mtime_ns, before.st_ctime_ns,
        )
        named_identity = (
            named.st_dev, named.st_ino, named.st_uid, named.st_gid,
            named.st_mode, named.st_nlink, named.st_size,
            named.st_mtime_ns, named.st_ctime_ns,
        )
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid not in {0, os.getuid()}
            or (require_single_link and before.st_nlink != 1)
            or (not require_single_link and before.st_nlink < 1)
            or mode not in modes
            or identity != named_identity
            or (executable and mode & 0o111 == 0)
        ):
            raise ContainmentError("containment file authority is invalid")
        content_sha = _read_hash(descriptor, limit)
        after = os.fstat(descriptor)
        after_identity = (
            after.st_dev, after.st_ino, after.st_uid, after.st_gid,
            after.st_mode, after.st_nlink, after.st_size,
            after.st_mtime_ns, after.st_ctime_ns,
        )
        if after_identity != identity or os.lstat(candidate) != after:
            raise ContainmentError("containment file changed during binding")
        return FileBinding(
            str(candidate), before.st_dev, before.st_ino, before.st_uid,
            before.st_gid, mode, before.st_nlink, before.st_size,
            before.st_mtime_ns, before.st_ctime_ns, content_sha,
        )
    finally:
        os.close(descriptor)


def _bind_directory(path: str | Path) -> DirectoryBinding:
    candidate = _canonical_existing(path)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory = getattr(os, "O_DIRECTORY", 0)
    try:
        named = os.lstat(candidate)
        descriptor = os.open(candidate, os.O_RDONLY | nofollow | directory)
    except OSError as exc:
        raise ContainmentError("containment directory is unavailable") from exc
    try:
        current = os.fstat(descriptor)
        if (
            not stat.S_ISDIR(current.st_mode)
            or stat.S_ISLNK(named.st_mode)
            or current.st_uid != os.getuid()
            or stat.S_IMODE(current.st_mode) != 0o700
            or (
                current.st_dev, current.st_ino, current.st_uid,
                current.st_gid, current.st_mode, current.st_nlink
            ) != (
                named.st_dev, named.st_ino, named.st_uid,
                named.st_gid, named.st_mode, named.st_nlink
            )
        ):
            raise ContainmentError("containment directory authority is invalid")
        return DirectoryBinding(
            str(candidate), current.st_dev, current.st_ino, current.st_uid,
            current.st_gid, stat.S_IMODE(current.st_mode), current.st_nlink,
        )
    finally:
        os.close(descriptor)


def _ensure_private_directory(path: Path, *, existing_ok: bool) -> DirectoryBinding:
    try:
        os.mkdir(path, 0o700)
    except FileExistsError:
        if not existing_ok:
            raise ContainmentError("per-attempt containment directory already exists")
    except OSError as exc:
        raise ContainmentError("cannot create containment directory") from exc
    try:
        os.chmod(path, 0o700, follow_symlinks=False)
    except OSError as exc:
        raise ContainmentError("cannot normalize containment directory") from exc
    return _bind_directory(path)


def _publish_profile(path: Path, payload: bytes) -> FileBinding:
    if not payload or len(payload) > MAX_PROFILE_BYTES:
        raise ContainmentError("containment profile has invalid size")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as exc:
        raise ContainmentError("cannot create containment profile") from exc
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise ContainmentError("cannot write containment profile")
            view = view[written:]
        os.fsync(descriptor)
        os.fchmod(descriptor, 0o400)
    finally:
        os.close(descriptor)
    return _bind_file(path, modes={0o400}, limit=MAX_PROFILE_BYTES)


def _scheme_string(value: str) -> str:
    if "\0" in value:
        raise ContainmentError("sandbox profile value contains NUL")
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return f'"{escaped}"'


def render_profile(
    *, target_executable: str, role: str, network_policy: str,
    allow_keychain: bool, read_only_inputs: Sequence[str] = (),
) -> bytes:
    """Render the fixed default-deny profile; dynamic paths use ``-D`` params."""
    if role not in _ROLES:
        raise ContainmentError("containment role is invalid")
    if network_policy not in {NETWORK_DENY_ALL, NETWORK_PROVIDER_TLS}:
        raise ContainmentError("containment network policy is invalid")
    if network_policy == NETWORK_PROVIDER_TLS and role != ROLE_PROVIDER:
        raise ContainmentError("only provider launches may use provider TLS")
    if role != ROLE_PROVIDER and allow_keychain:
        raise ContainmentError("only provider launches may access the keychain")
    if len(read_only_inputs) > 8 or any(
        not isinstance(path, str) or not path.startswith("/") for path in read_only_inputs
    ):
        raise ContainmentError("containment read-only inputs are invalid")
    runtime_reads = ""
    if read_only_inputs:
        runtime_reads = "\n(allow file-read*\n" + "".join(
            f"  (literal {_scheme_string(path)})\n" for path in read_only_inputs
        ) + ")\n"
    keychain = ""
    if allow_keychain:
        # A fork retains the target image and its exact service authority. An
        # exec normally loses that authority; /usr/bin/security is the sole
        # Keychain-helper exception and inherits every other profile boundary.
        keychain = f"""
(with-filter (process-path {_scheme_string(target_executable)})
  (allow mach-lookup
    (global-name "com.apple.SecurityServer")
    (global-name "com.apple.securityd.xpc")
    (global-name "com.apple.securityd.general")
    (global-name "com.apple.trustd")
    (global-name "com.apple.trustd.agent")))
(with-filter (process-path {_scheme_string("/usr/bin/security")})
  (allow mach-lookup
    (global-name "com.apple.SecurityServer")
    (global-name "com.apple.securityd.xpc")
    (global-name "com.apple.securityd.general")
    (global-name "com.apple.trustd")
    (global-name "com.apple.trustd.agent")))
"""
    network = ""
    if network_policy == NETWORK_PROVIDER_TLS:
        # Apple's localhost token was qualified against owned IPv4, IPv6, and
        # interface-local listeners. This is a process/port boundary, not a
        # recipient allowlist or proof that the connection uses TLS. For local
        # listeners it also permits wildcard binds; the exact provider image is
        # trusted to request its advertised localhost endpoint.
        network = f"""
(with-filter (process-path {_scheme_string(target_executable)})
  (allow network-outbound
    (require-all (remote tcp "*:443")
      (require-not (remote ip "localhost:*"))))
  (allow network-outbound (literal "/private/var/run/mDNSResponder"))
  (allow network-bind network-inbound (local tcp "localhost:*"))
  (allow mach-lookup (global-name "com.apple.mDNSResponder")))
(deny network-outbound (remote ip "localhost:*"))
"""
    profile_text = f"""(version 1)
(deny default)
(import "dyld-support.sb")

; Fork/exec is required for ordinary build tools.  Every exec inherits this
; profile.  Darwin implements setsid/setpgid without a process-info-setcontrol
; hook, so explicitly deny those two syscalls while leaving fork available.
(allow syscall*)
(allow mach-bootstrap)
(deny syscall-unix
  (syscall-number SYS_setsid)
  (syscall-number SYS_setpgid))
(allow process-fork)
(allow process-exec
  (literal (param "TARGET"))
  (subpath (param "STAGE"))
  (subpath "/bin")
  (subpath "/usr/bin")
  (subpath "/Library/Developer/CommandLineTools"))
(allow process-info-pidinfo (target self))
(allow sysctl-read)

(allow file-read* file-map-executable
  (literal (param "TARGET"))
  (subpath (param "STAGE"))
  (subpath (param "HOME"))
  (subpath (param "TMPDIR"))
  (subpath "/bin")
  (subpath "/usr/bin")
  (subpath "/usr/lib")
  (subpath "/usr/share")
  (subpath "/System")
  (subpath "/Library/Apple")
  (subpath "/Library/Developer/CommandLineTools")
  (subpath "/private/var/db/timezone")
  (literal "/")
  (literal "/dev/null")
  (literal "/dev/zero")
  (literal "/dev/random")
  (literal "/dev/urandom")
  (literal "/etc/resolv.conf")
  (literal "/private/etc/resolv.conf")
  (literal "/private/var/run/resolv.conf"))
(allow file-read-metadata file-test-existence
  (path-ancestors "/Library/Developer/CommandLineTools")
  (literal "/var")
  (literal "/private/var/select")
  (literal "/private/var/select/developer_dir")
  (literal "/private/var/select/sh"))
(allow file-write-data
  (literal "/dev/null")
  (literal "/dev/zero")
  (subpath "/dev/fd"))
(allow file-read* file-write*
  (subpath (param "STAGE"))
  (subpath (param "HOME"))
  (subpath (param "TMPDIR")))

{runtime_reads}{keychain}{network}"""
    return profile_text.encode("utf-8")


def _bind_target(path: str | Path) -> FileBinding:
    binding = _bind_file(
        path, modes={0o700, 0o750, 0o755}, executable=True,
        require_single_link=False,
    )
    if binding.uid != 0 and binding.nlink != 1:
        raise ContainmentError("user-owned containment target has multiple links")
    return binding


def prepare_contained_launch(
    *,
    role: str,
    network_policy: str,
    job_dir: str | Path,
    attempt: int,
    stage_dir: str | Path,
    target_executable: str | Path,
    target_argv: Sequence[str],
    child_environment: Mapping[str, str],
    allow_keychain: bool = False,
    read_only_inputs: Sequence[str | Path] = (),
) -> PreparedContainedLaunch:
    """Create and bind one native selected-content launch envelope."""
    require_supported_host()
    if role not in _ROLES:
        raise ContainmentError("containment role is invalid")
    if network_policy not in {NETWORK_DENY_ALL, NETWORK_PROVIDER_TLS}:
        raise ContainmentError("containment network policy is invalid")
    if network_policy == NETWORK_PROVIDER_TLS and role != ROLE_PROVIDER:
        raise ContainmentError("only provider launches may use provider TLS")
    if role != ROLE_PROVIDER and allow_keychain:
        raise ContainmentError("only provider launches may access the keychain")
    if type(attempt) is not int or not 1 <= attempt <= 999:
        raise ContainmentError("containment attempt is invalid")
    if not target_argv or any(
        not isinstance(value, str) or "\0" in value for value in target_argv
    ):
        raise ContainmentError("containment target argv is invalid")
    if any(
        not isinstance(key, str) or not isinstance(value, str)
        or not key or "=" in key or "\0" in key or "\0" in value
        for key, value in child_environment.items()
    ):
        raise ContainmentError("child environment is invalid")
    job = _canonical_existing(job_dir)
    job_binding = _bind_directory(job)
    stage = _bind_directory(stage_dir)
    if Path(stage.path).parent != Path(job_binding.path):
        raise ContainmentError("scoped stage must be an immediate job child")
    launcher = _bind_file(SANDBOX_EXEC, modes={0o755}, executable=True)
    target = _bind_target(target_executable)
    if target_argv[0] != target.path:
        raise ContainmentError("containment target argv does not name the bound executable")
    if len(read_only_inputs) > 8:
        raise ContainmentError("too many containment read-only inputs")
    bound_inputs = tuple(
        _bind_file(
            path, modes={0o400, 0o444, 0o600, 0o644},
            limit=MAX_PROFILE_BYTES,
        )
        for path in read_only_inputs
    )
    if len({item.path for item in bound_inputs}) != len(bound_inputs):
        raise ContainmentError("containment read-only inputs are repeated")
    stem = "provider" if role == ROLE_PROVIDER else "self-verify"
    home = _ensure_private_directory(job / f"{stem}-home", existing_ok=True)
    attempt_tmp = _ensure_private_directory(
        job / f"{stem}-tmp-{attempt:03d}", existing_ok=False,
    )
    profile_payload = render_profile(
        target_executable=target.path,
        role=role,
        network_policy=network_policy,
        allow_keychain=allow_keychain,
        read_only_inputs=tuple(item.path for item in bound_inputs),
    )
    profile_binding = _publish_profile(
        job / f"{stem}-sandbox-{attempt:03d}.sb", profile_payload,
    )
    if role == ROLE_SELF_VERIFY:
        environment = {
            "PATH": "/usr/bin:/bin",
            "LANG": "C",
            "LC_ALL": "C",
            "TERM": "dumb",
            "NO_COLOR": "1",
        }
    else:
        environment = dict(child_environment)
    environment.update({
        "HOME": home.path,
        "TMPDIR": attempt_tmp.path,
        "XDG_CACHE_HOME": str(Path(home.path) / ".cache"),
        "XDG_CONFIG_HOME": str(Path(home.path) / ".config"),
        "XDG_DATA_HOME": str(Path(home.path) / ".local" / "share"),
        "XDG_STATE_HOME": str(Path(home.path) / ".local" / "state"),
    })
    return PreparedContainedLaunch(
        role, network_policy, platform.release(), platform.version(), launcher,
        target, profile_binding, bound_inputs, stage, home, attempt_tmp, tuple(target_argv),
        tuple(sorted(environment.items())), bool(allow_keychain),
    )


def confirm_contained_launch(
    prepared: PreparedContainedLaunch,
) -> ConfirmedContainedLaunch:
    """Revalidate every native authority immediately before caller ``Popen``."""
    require_supported_host()
    if (platform.release(), platform.version()) != (
        prepared.darwin_release, prepared.darwin_version,
    ):
        raise ContainmentError("Darwin build changed before scoped launch")
    if _bind_file(prepared.launcher.path, modes={0o755}, executable=True) != prepared.launcher:
        raise ContainmentError("sandbox launcher changed before scoped launch")
    if _bind_file(
        prepared.target.path, modes={0o700, 0o750, 0o755}, executable=True,
        require_single_link=False,
    ) != prepared.target:
        raise ContainmentError("target executable changed before contained launch")
    if _bind_file(
        prepared.profile.path, modes={0o400}, limit=MAX_PROFILE_BYTES,
    ) != prepared.profile:
        raise ContainmentError("sandbox profile changed before scoped launch")
    if any(
        _bind_file(
            item.path, modes={0o400, 0o444, 0o600, 0o644},
            limit=MAX_PROFILE_BYTES,
        ) != item
        for item in prepared.read_only_inputs
    ):
        raise ContainmentError("containment read-only input changed before launch")
    if _bind_directory(prepared.stage.path) != prepared.stage:
        raise ContainmentError("scoped stage changed before launch")
    if _bind_directory(prepared.private_home.path) != prepared.private_home:
        raise ContainmentError("private HOME changed before launch")
    if _bind_directory(prepared.attempt_tmp.path) != prepared.attempt_tmp:
        raise ContainmentError("private provider TMPDIR changed before launch")
    argv = (
        prepared.launcher.path,
        "-f", prepared.profile.path,
        "-D", f"TARGET={prepared.target.path}",
        "-D", f"STAGE={prepared.stage.path}",
        "-D", f"HOME={prepared.private_home.path}",
        "-D", f"TMPDIR={prepared.attempt_tmp.path}",
        prepared.target.path,
        *prepared.target_argv[1:],
    )
    return ConfirmedContainedLaunch(
        argv, prepared.launcher.path, prepared.stage.path,
        dict(prepared.environment),
    )


def _libproc() -> ctypes.CDLL:
    require_supported_host()
    library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
    library.proc_pidinfo.argtypes = [
        ctypes.c_int, ctypes.c_int, ctypes.c_uint64,
        ctypes.c_void_p, ctypes.c_int,
    ]
    library.proc_pidinfo.restype = ctypes.c_int
    library.proc_listpgrppids.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
    library.proc_listpgrppids.restype = ctypes.c_int
    return library


def capture_process_identity(pid: int) -> ProcessIdentity:
    """Bind a Darwin PID to kernel start time, owner, group, and session."""
    if type(pid) is not int or pid <= 1:
        raise ContainmentError("provider PID is invalid")
    info = _ProcBsdInfo()
    library = _libproc()
    size = library.proc_pidinfo(
        pid, _PROC_PIDTBSDINFO, 0, ctypes.byref(info), ctypes.sizeof(info),
    )
    if size != ctypes.sizeof(info) or int(info.pbi_pid) != pid:
        raise ContainmentError("provider process identity is unavailable")
    try:
        session_id = os.getsid(pid)
    except OSError as exc:
        raise ContainmentError("provider process session is unavailable") from exc
    return ProcessIdentity(
        pid, int(info.pbi_ppid), int(info.pbi_pgid), session_id,
        int(info.pbi_uid), int(info.pbi_start_tvsec), int(info.pbi_start_tvusec),
    )


def bind_new_process_group(pid: int) -> ProcessIdentity:
    """Bind the session leader created by ``Popen(start_new_session=True)``."""
    identity = capture_process_identity(pid)
    if (
        identity.uid != os.getuid()
        or identity.process_group != pid
        or identity.session_id != pid
    ):
        raise ContainmentError("provider process is not a new bound session leader")
    return identity


def _process_group_members(process_group: int) -> tuple[int, ...]:
    library = _libproc()
    capacity = 64
    while capacity <= MAX_GROUP_MEMBERS:
        values = (ctypes.c_int * capacity)()
        size = library.proc_listpgrppids(
            process_group, ctypes.byref(values), ctypes.sizeof(values),
        )
        if size < 0:
            raise ContainmentError("provider process group is unavailable")
        # Unlike proc_pidinfo(), proc_listpgrppids() returns a PID count.
        count = size
        if count < capacity:
            return tuple(sorted({int(values[index]) for index in range(count) if values[index] > 1}))
        capacity *= 2
    raise ContainmentError("provider process group exceeds the cleanup bound")


def _bind_group_members(root: ProcessIdentity) -> tuple[ProcessIdentity, ...]:
    # A member may exit after proc_listpgrppids() reports it but before its
    # identity is queried. Re-list that race; never treat an unbound PID as a
    # group member and never signal until one complete pass is stable.
    for _attempt in range(32):
        members: list[ProcessIdentity] = []
        retry = False
        for pid in _process_group_members(root.process_group):
            try:
                current = capture_process_identity(pid)
            except ContainmentError:
                retry = True
                break
            if (
                current.uid != root.uid
                or current.process_group != root.process_group
                or current.session_id != root.session_id
                or (current.start_seconds, current.start_microseconds)
                < (root.start_seconds, root.start_microseconds)
            ):
                raise ContainmentError("contained process group identity drifted")
            members.append(current)
        if retry:
            time.sleep(0.005)
            continue
        live_root = next((item for item in members if item.pid == root.pid), None)
        if live_root is not None and live_root != root:
            raise ContainmentError("contained root PID was reused")
        return tuple(members)
    raise ContainmentError("contained process group changed during binding")


def process_group_is_quiescent(root: ProcessIdentity) -> bool:
    """Return true when the bound group is empty, without a lineage claim.

    A child can create another session through posix_spawn attributes even
    though direct setsid/setpgid syscalls are denied. Such a child retains this
    Seatbelt profile but is outside this process-group cleanup primitive.
    """
    return not _bind_group_members(root)


def terminate_bound_process_group(
    root: ProcessIdentity, number: int = signal.SIGKILL,
) -> tuple[ProcessIdentity, ...]:
    """Signal only members of the exact new session rooted at ``root``.

    Direct ``setsid`` and ``setpgid`` syscalls are denied, but posix_spawn
    session/group attributes are a confirmed bypass. This function covers only
    processes still in the bound group. It binds and re-checks every current
    member before ``killpg``; a PID-reused or unrelated group is rejected
    instead of signalled. Escaped descendants retain filesystem/network
    containment but are outside this cleanup primitive.
    """
    if number not in {signal.SIGTERM, signal.SIGKILL}:
        raise ContainmentError("cleanup signal is invalid")
    members = _bind_group_members(root)
    if not members:
        return ()
    # A surviving member with the bound session ID proves this is still the
    # original session even if its leader has already exited.
    for item in members:
        if capture_process_identity(item.pid) != item:
            raise ContainmentError("provider process changed before cleanup")
    try:
        os.killpg(root.process_group, number)
    except ProcessLookupError:
        return ()
    except OSError as exc:
        raise ContainmentError("provider process-group cleanup failed") from exc
    return members
