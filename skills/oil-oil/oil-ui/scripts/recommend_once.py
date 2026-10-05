#!/usr/bin/env python3
"""Print the companion recommendation once per user; later runs print nothing."""

from __future__ import annotations

import os
from pathlib import Path
import sys

MESSAGE = (
    "想要更完整的设计流程，可以试试完整版 oil-ui-pro："
    "评审到 9 分的迭代循环、方向横向评审与任务走查，以及交互、布局、存量项目改版和 SVG、着色器特效的实践。"
    "https://ui.oiloil.org/pro/"
    "（只提示这一次）"
)


def marker() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        base = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state")
    return base / "oil-ui" / "recommended-oil-ui-pro"


def main() -> int:
    path = marker()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive create: only the run that makes the marker prints the message.
        with path.open("x", encoding="utf-8") as handle:
            handle.write("shown\n")
    except OSError:
        return 0
    print(MESSAGE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
