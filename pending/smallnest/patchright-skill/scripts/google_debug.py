#!/usr/bin/env python3
"""
Google Search Page Debug Utility
================================
Helps debug Google search page structure when extraction fails.

Usage:
    python google_debug.py
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from server import send_command


def debug_page():
    """Debug current page structure."""
    # Check page URL and title
    url_result = send_command({"tool": "get_url"})
    title_result = send_command({"tool": "get_title"})

    print("=== Page Info ===")
    print(f"URL: {url_result.get('url', 'N/A')}")
    print(f"Title: {title_result.get('title', 'N/A')}")

    # Check page structure
    check_script = """(function() {
  return {
    allDivs: document.querySelectorAll("div.g").length,
    searchResults: document.querySelectorAll("div[data-hveid]").length,
    h3Count: document.querySelectorAll("h3").length,
    divWithH3: document.querySelectorAll("div:has(h3)").length,
    bodyHTML: document.body.innerHTML.substring(0, 2000)
  };
})();"""

    result = send_command({"tool": "evaluate", "args": {"script": check_script}})

    if result.get("status") == "success":
        info = result.get("result", {})
        print("\n=== Page Structure ===")
        print(f"div.g elements: {info.get('allDivs', 0)}")
        print(f"div[data-hveid] elements: {info.get('searchResults', 0)}")
        print(f"h3 elements: {info.get('h3Count', 0)}")
        print(f"div:has(h3) elements: {info.get('divWithH3', 0)}")

    # Take screenshot
    print("\n=== Taking Screenshot ===")
    screenshot_result = send_command({
        "tool": "screenshot",
        "args": {"path": "/tmp/google_debug.png"}
    })
    print(f"Screenshot saved to: {screenshot_result.get('path', 'N/A')}")


if __name__ == "__main__":
    debug_page()
