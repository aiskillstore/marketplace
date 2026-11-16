#!/usr/bin/env python3
"""Compatibility entry point for Reword's previous internal module name."""

from reword import *  # Preserve the existing Python API as well as the CLI.

if __name__ == "__main__":
    raise SystemExit(main())
