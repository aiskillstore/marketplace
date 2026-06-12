#!/usr/bin/env python3
"""Listing 上下文抓取与解析的最小回归测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import fetch_listing_context as listing_fetch


SAMPLE_HTML = """
<html>
  <head>
    <meta name="description" content="Portable karaoke machine with lyrics display and two wireless microphones." />
  </head>
  <body>
    <span id="productTitle">
      ExampleBrand Smart Karaoke Machine for Adults with Lyrics Display
    </span>
    <a id="bylineInfo">Brand: ExampleBrand</a>
    <div id="feature-bullets">
      <ul>
        <li><span class="a-list-item">13.3 inch lyrics display for easier singing</span></li>
        <li><span class="a-list-item">2 wireless microphones with self charging dock</span></li>
      </ul>
    </div>
    <div id="productDescription">
      <p>Built for home party and outdoor karaoke sessions.</p>
    </div>
    <div id="wayfinding-breadcrumbs_feature_div">
      <a>Musical Instruments</a>
      <a>Karaoke Equipment</a>
    </div>
    <span class="a-price"><span class="a-offscreen">$399.99</span></span>
    <div id="productOverview_feature_div">
      <table>
        <tr><th>Color</th><td>Black</td></tr>
        <tr><th>Connectivity</th><td>Bluetooth</td></tr>
      </table>
    </div>
  </body>
</html>
"""


class ListingContextFetchTests(unittest.TestCase):
    def test_extract_listing_context_parses_core_fields(self) -> None:
        payload = listing_fetch.extract_listing_context(
            SAMPLE_HTML,
            asin="B0PUBLIC01",
            site_code="US",
            domain="amazon.com",
        )
        self.assertEqual(payload["page_status"], "ok")
        self.assertIn("ExampleBrand Smart Karaoke Machine", payload["title"])
        self.assertGreaterEqual(len(payload["bullets"]), 2)
        self.assertIn("2 wireless microphones", " ".join(payload["bullets"]).lower())
        self.assertIn("home party", payload["description"].lower())
        self.assertIn("Karaoke Equipment", payload["breadcrumb"])
        self.assertEqual(payload["product_overview"].get("Connectivity"), "Bluetooth")


if __name__ == "__main__":
    unittest.main()
