"""UNO bridge for connecting to LibreOffice."""

import os
import subprocess
import time
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

from exceptions import UnoBridgeError


def find_libreoffice() -> Optional[str]:
    """Auto-detect LibreOffice installation.

    Returns:
        Path to soffice executable, or None if not found.
    """
    # Common executable names
    executables = ["soffice", "libreoffice"]

    # Check PATH first
    for exe in executables:
        path = subprocess.run(
            ["which", exe],
            capture_output=True,
            text=True,
        ).stdout.strip()
        if path:
            return path

    # Check common installation locations
    common_paths = [
        "/usr/bin/soffice",
        "/usr/bin/libreoffice",
        "/usr/local/bin/soffice",
        "/opt/libreoffice/program/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]

    for path in common_paths:
        if Path(path).exists():
            return path

    return None


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
    import importlib.util

    uno_spec = importlib.util.find_spec("uno")
    if uno_spec is None:
        soffice_path = find_libreoffice()
        if not soffice_path:
            raise UnoBridgeError("LibreOffice not found. Please install LibreOffice.")
        lo_program = Path(soffice_path).resolve().parent
        if lo_program.is_dir():
            sys.path.insert(0, str(lo_program))

    import uno
    from com.sun.star.connection import NoConnectException

    # Find LibreOffice
    soffice_path = find_libreoffice()
    if not soffice_path:
        raise UnoBridgeError("LibreOffice not found. Please install LibreOffice.")

    # Generate unique pipe name
    pipe_name = f"uno_pipe_{os.getpid()}_{int(time.time() * 1000)}"
    connection_string = f"pipe,name={pipe_name}"

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
            f"--accept=pipe,name={pipe_name};urp;",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        # Wait for LibreOffice to start and accept connections
        local_context = uno.getComponentContext()
        resolver = local_context.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_context
        )

        # Try to connect with retries
        max_retries = 20
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
                time.sleep(0.1)
    finally:
        # Clean up: terminate LibreOffice
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
