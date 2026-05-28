#!/usr/bin/env python3
"""Run a literature search for PDAC treatments"""

import sys
from pathlib import Path
import pubmed_search

pubmed_search.CONFIG["INPUT_JSON"] = Path(__file__).parent / "outputs" / "query.json"

if __name__ == "__main__":
    pubmed_search.main()
