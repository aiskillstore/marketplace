"""UNO bridge for connecting to LibreOffice."""

# pyright: reportMissingImports=false

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

from exceptions import UnoBridgeError


def find_libreoffice() -> Optional[str]:
    """Auto-detect LibreOffice installation.

    Returns:
        Path to soffice executable, or None if not found.
    """
    for exe in ("soffice", "libreoffice"):
        found = shutil.which(exe)
        if found:
            return found

    # Check common installation locations
    common_paths = [
        "/usr/bin/soffice",
        "/usr/bin/libreoffice",
        "/usr/local/bin/soffice",
        "/opt/libreoffice/program/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "C:/Program Files/LibreOffice/program/soffice",
    ]

    for path in common_paths:
        if Path(path).exists():
            return path

    return None


def _resolve_uno_module() -> None:
    """Ensure the LibreOffice-provided ``uno`` module can be imported.

    Resolution order:
    1. Already importable from the current Python environment.
    2. ``LIBREOFFICE_PROGRAM_PATH`` environment variable override.
    3. Parent directory of the detected ``soffice`` executable.

    Raises:
        UnoBridgeError: If no valid LibreOffice program directory is found.
    """
    if importlib.util.find_spec("uno") is not None:
        return

    candidates: list[Path] = []

    default_candidates = [
        Path("/usr/lib/python3/dist-packages"),
        Path("/usr/lib/libreoffice/program"),
    ]
    candidates.extend(default_candidates)

    env_path = os.environ.get("LIBREOFFICE_PROGRAM_PATH")
    if env_path:
        candidates.append(Path(env_path))

    soffice_path = find_libreoffice()
    if soffice_path:
        candidates.append(Path(soffice_path).resolve().parent)

    seen: set[str] = set()
    for candidate in candidates:
        if candidate.is_dir():
            candidate_str = str(candidate)
            if candidate_str in seen:
                continue
            seen.add(candidate_str)
            if candidate_str not in sys.path:
                sys.path.insert(0, candidate_str)
            if importlib.util.find_spec("uno") is not None:
                return

    raise UnoBridgeError(
        "Unable to import the LibreOffice UNO Python module. "
        "Install LibreOffice with Python UNO support or set "
        "LIBREOFFICE_PROGRAM_PATH to the LibreOffice program directory."
    )


def validate_lo_path(path: str) -> None:
    """Validate that LibreOffice installation exists at the given path.

    Args:
        path: Path to LibreOffice installation directory.

    Raises:
        UnoBridgeError: If the path does not exist.
    """
    if not Path(path).exists():
        raise UnoBridgeError(f"LibreOffice not found: {path}")


@contextmanager
def uno_context() -> Generator[Any, None, None]:
    """Context manager for UNO connection to LibreOffice.

    Yields:
        Desktop object for creating/loading documents.

    Raises:
        UnoBridgeError: If LibreOffice cannot be found or connection fails.

    Example:
        with uno_context() as desktop:
            doc = desktop.loadComponentFromURL(...)
    """
    _resolve_uno_module()

    import uno
    from com.sun.star.connection import NoConnectException

    # Find LibreOffice
    soffice_path = find_libreoffice()
    if not soffice_path:
        raise UnoBridgeError("LibreOffice not found. Please install LibreOffice.")

    # Generate unique pipe name
    pipe_name = f"uno_pipe_{os.getpid()}_{int(time.time() * 1000)}"
    connection_string = f"pipe,name={pipe_name}"
    profile_dir = Path(tempfile.mkdtemp(prefix="libreoffice-skills-"))
    profile_url = profile_dir.resolve().as_uri()

    # Start LibreOffice in headless mode
    process = subprocess.Popen(
        [
            soffice_path,
            "--headless",
            "--invisible",
            "--nocrashreport",
            "--nodefault",
            "--nofirststartwizard",
            "--nologo",
            "--norestore",
            f"-env:UserInstallation={profile_url}",
            f"--accept=pipe,name={pipe_name};urp;",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        local_context = uno.getComponentContext()
        resolver = local_context.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_context
        )

        max_retries = 50
        for attempt in range(max_retries):
            try:
                ctx = resolver.resolve(
                    f"uno:{connection_string};urp;StarOffice.ComponentContext"
                )
                smgr = ctx.ServiceManager
                desktop = smgr.createInstanceWithContext(
                    "com.sun.star.frame.Desktop", ctx
                )
                yield desktop
                break
            except NoConnectException:
                if attempt == max_retries - 1:
                    raise UnoBridgeError(
                        f"Failed to connect to LibreOffice after {max_retries} attempts"
                    )
                time.sleep(0.2)
    finally:
        # Clean up: terminate LibreOffice
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        shutil.rmtree(profile_dir, ignore_errors=True)
