#!/usr/bin/env python3
"""Report built-in and optional color science capabilities."""

from __future__ import annotations

import importlib.util

from color_science_core import RGB_COLORSPACES, TRANSFER_NAMES


def module_status(name: str) -> str:
    return "installed" if importlib.util.find_spec(name) else "missing"


def main() -> None:
    print("Built-in RGB color spaces:")
    for key in sorted(RGB_COLORSPACES):
        print(f"  {key}: {RGB_COLORSPACES[key].name}")
    print("\nBuilt-in transfer functions:")
    for key in TRANSFER_NAMES:
        print(f"  {key}")
    print("\nOptional packages:")
    print(f"  colour-science import name 'colour': {module_status('colour')}")
    print(f"  PyOpenColorIO import name 'PyOpenColorIO': {module_status('PyOpenColorIO')}")
    print("\nUse ocio_generate_lut.py when an OCIO config defines the required camera, ACES, display, or show pipeline.")


if __name__ == "__main__":
    main()
