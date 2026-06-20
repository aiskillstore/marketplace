#!/usr/bin/env python3
"""Shared HTML rendering helpers for static report generators."""

import html
from typing import Any


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Used by report renderers to escape HTML while preserving meaningful falsey values."


def html_text(value: Any) -> str:
    """Escape text for HTML without dropping 0 or False values."""
    return html.escape("" if value is None else str(value), quote=True)
