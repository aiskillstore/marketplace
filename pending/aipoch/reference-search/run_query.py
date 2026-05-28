#!/usr/bin/env python3
"""Run a literature search query"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

import pubmed_search

pubmed_search.CONFIG["INPUT_JSON"] = Path(__file__).parent / "inputs" / "query.json"
pubmed_search.CONFIG["EMAIL"] = "researcher@example.com"

if __name__ == "__main__":
    pubmed_search.main()
