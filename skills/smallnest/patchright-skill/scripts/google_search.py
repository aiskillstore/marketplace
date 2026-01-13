#!/usr/bin/env python3
"""
Google Search Automation Script
================================
Automates Google searches and extracts search results in JSON format.

Usage:
    python google_search.py "<search_query>" [max_results]

Example:
    python google_search.py "2026年Go语言展望" 20
"""

import json
import sys
import time
from urllib.parse import quote
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from server import send_command


class GoogleSearcher:
    def __init__(self):
        self.results = []

    def search(self, query, max_results=20):
        """
        Perform Google search and extract results.

        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 20)

        Returns:
            List of search result dictionaries with rank, title, link, description
        """
        encoded_query = quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"

        print(f"Searching for: {query}")
        print(f"URL: {search_url}")

        # Launch browser and navigate
        print("Launching browser...")
        send_command({"tool": "launch", "args": {"headless": False}})

        print(f"Navigating to search results...")
        result = send_command({"tool": "navigate", "args": {"url": search_url}})
        print(f"Page title: {result.get('title', 'N/A')}")

        # Wait for page to load
        time.sleep(2)

        # Extract results from first page
        results = self._extract_results()

        # If we need more results and got fewer than max_results, navigate to next page
        if len(results) < max_results:
            print(f"Got {len(results)} results from page 1, navigating to page 2...")
            time.sleep(1)
            self._click_next_page()
            time.sleep(3)
            page2_results = self._extract_results()
            results.extend(page2_results)

        # Renumber results sequentially
        for i, result in enumerate(results):
            result["rank"] = i + 1

        # Limit to max_results
        self.results = results[:max_results]

        return self.results

    def _extract_results(self):
        """Extract search results from current page."""
        script = """(function() {
  const results = [];
  const h3Elements = document.querySelectorAll("h3");
  const seen = new Set();

  h3Elements.forEach((h3, index) => {
    if (index >= 15) return;

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
            return result.get("result", [])
        return []

    def _click_next_page(self):
        """Click the next page button."""
        script = """(function() {
  const nextButton = document.querySelector("#pnnext");
  if (nextButton) {
    nextButton.click();
    return "clicked_next";
  }
  return "no_next_button";
})();"""

        result = send_command({"tool": "evaluate", "args": {"script": script}})
        print(f"Next page: {result.get('result', 'unknown')}")

    def save_results(self, output_path):
        """Save results to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_path}")

    def print_results(self):
        """Print results in JSON format."""
        print(json.dumps(self.results, indent=2, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print("Usage: python google_search.py \"<search_query>\" [max_results]")
        print("Example: python google_search.py \"2026年Go语言展望\" 20")
        sys.exit(1)

    query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    searcher = GoogleSearcher()
    results = searcher.search(query, max_results)

    print(f"\n=== Found {len(results)} results ===\n")
    searcher.print_results()

    # Optionally save to file
    output_path = Path("/tmp") / f"google_search_{int(time.time())}.json"
    searcher.save_results(output_path)


if __name__ == "__main__":
    main()
