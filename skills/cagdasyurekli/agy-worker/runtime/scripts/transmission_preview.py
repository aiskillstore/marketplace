#!/usr/bin/env python3
"""Compatibility forwarder for the canonical transmission-preview engine."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RUNTIME_HELPER = HERE / "agy_dispatch_worktree.py"
if not RUNTIME_HELPER.is_file():
    RUNTIME_HELPER = (
        HERE.parent / "skills" / "agy-worker" / "runtime" / "scripts"
        / "agy_dispatch_worktree.py"
    )

spec = importlib.util.spec_from_file_location("agy_dispatch_worktree", str(RUNTIME_HELPER))
if spec and spec.loader:
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.exit(mod._preview_main(sys.argv[1:]))
sys.exit(64)
