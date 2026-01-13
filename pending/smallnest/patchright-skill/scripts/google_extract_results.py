#!/usr/bin/env python3
"""
Extract Google Search Results from Current Page
================================================
Extracts search results from the currently open Google search page.

Usage:
    python google_extract_results.py
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from server import send_command


def extract_results():
    """Extract search results from current page."""
    script = """(function() {
  const results = [];
  const h3Elements = document.querySelectorAll("h3");
  const seen = new Set();

  h3Elements.forEach((h3, index) => {
    if (index >= 20) return;

    let parent = h3.closest("div[data-hveid]") || h3.closest("div.g") || h3.closest(".MjjYud") || h3.parentElement;

    if (parent) {
      const a = parent.querySelector("a");
      const link = a ? a.href : "";

      let description = "";
      const descSelectors = [".VwiC3b", ".st", ".ITZIwc", ".HGLXqc"];
      for (const sel of descSelectors) {
        const descEl = parent.querySelector(sel);
        if (descEl) {
          description = descEl.textContent.trim().substring(0, 200);
          break;
        }
      }

      const key = link || h3.textContent.trim();
      if (!seen.has(key) && h3.textContent.trim() && link) {
        seen.add(key);
        results.push({
          rank: results.length + 1,
          title: h3.textContent.trim(),
          link: link,
          description: description
        });
      }
    }
  });

  return results;
})();"""

    result = send_command({"tool": "evaluate", "args": {"script": script}})

    if result.get("status") == "success":
        results = result.get("result", [])
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return results
    else:
        print(json.dumps(result, indent=2))
        return []


if __name__ == "__main__":
    extract_results()
