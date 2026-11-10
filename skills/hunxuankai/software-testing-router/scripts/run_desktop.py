"""Select the native desktop runner without changing the Windows entry point."""
from __future__ import annotations

import subprocess
import sys
import time
import uuid
from pathlib import Path


def main(argv=None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    entry = {"win32": "run_uia.py", "darwin": "run_macos.py"}.get(sys.platform)
    if entry:
        return subprocess.call([sys.executable, str(Path(__file__).with_name(entry)), *arguments])
    from run_macos import _finish, build_parser, options_from_args

    parser = build_parser()
    args = parser.parse_args(arguments)
    options_from_args(args, parser)
    return _finish({"ok": False, "status": "unavailable", "error": "Native desktop automation supports Windows and macOS only"},
                   args, uuid.uuid4().hex, time.perf_counter(), 2)


if __name__ == "__main__":
    raise SystemExit(main())
