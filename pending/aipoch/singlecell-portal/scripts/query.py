#!/usr/bin/env python3
"""Single Cell Portal API query script

How to use:
1. Install dependencies: pip install requests
2. Run: python scripts/query.py [keyword]

Description:
- Query Broad Institute Single Cell Portal based on REST API
- Support natural language input and automatically convert to ontology ID
- Fall back to keyword search when ID cannot be found
- No API key required
- Windows compatible"""

from __future__ import annotations

import json
import sys
from pathlib import Path

API_BASE = "https://singlecell.broadinstitute.org/single_cell/api/v1"

# Mapping of common names to IDs (speeding up queries)
KNOWN_MAPPINGS = {
    "human": ("species", "NCBITaxon_9606"),
    "mouse": ("species", "NCBITaxon_10090"),
    "liver": ("organ", "UBERON_0002107"),
    "lung": ("organ", "UBERON_0002048"),
    "brain": ("organ", "UBERON_0000955"),
    "heart": ("organ", "UBERON_0000948"),
    "kidney": ("organ", "UBERON_0002113"),
    "normal": ("disease", "PATO:0000461"),
    "healthy": ("disease", "PATO:0000461"),
    "cancer": ("disease", "MONDO:0000001"),
}


def require_requests():
    try:
        import requests
        import urllib3

        # Disable SSL warnings (Windows certificate issues)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return requests
    except ImportError:
        print("[ERROR] The requests library is missing.")
        print("[Tip] Please run: pip install requests")
        raise SystemExit(1)


def get_facets_dict(requests):
    """Get the facets dictionary for easy search"""
    url = f"{API_BASE}/search/facets"

    try:
        response = requests.get(url, timeout=30, verify=False)
        facets_list = response.json()

        # Convert to dictionary
        facets_dict = {}
        for facet in facets_list:
            name = facet.get("name", "")
            filters = facet.get("filters", [])
            facets_dict[name] = {
                f.get("name", "").lower(): f.get("id", "") for f in filters
            }

        return facets_dict
    except Exception as e:
        print(f"[warn] get facets fail: {e}")
        return {}


def find_id_by_name(facets_dict, facet_name, user_input):
    """Find the corresponding ontology ID based on user input"""
    user_input_lower = user_input.lower()

    # 1. Check known mappings
    key = user_input_lower.strip()
    if key in KNOWN_MAPPINGS:
        fn, oid = KNOWN_MAPPINGS[key]
        if fn == facet_name:
            return oid

    # 2. Fuzzy search in facets
    if facet_name in facets_dict:
        facet_values = facets_dict[facet_name]
        for name, oid in facet_values.items():
            # exact match
            if name == user_input_lower:
                return oid
            # contains matches
            if user_input_lower in name or name in user_input_lower:
                return oid

    return None


def build_facets_string(requests, organism="", organ="", disease="", cell_type=""):
    """Build facets query string"""
    facets_dict = get_facets_dict(requests)

    facet_parts = []
    missing_parts = []  # Log part of ID not found

    # Map user input to facet name
    mappings = [
        (organism, "species"),
        (organ, "organ"),
        (disease, "disease"),
        (cell_type, "cell type"),
    ]

    for user_input, facet_name in mappings:
        if not user_input:
            continue

        oid = find_id_by_name(facets_dict, facet_name, user_input)

        if oid:
            facet_parts.append(f"{facet_name}:{oid}")
        else:
            missing_parts.append(user_input)

    return facet_parts, missing_parts


def search_by_facets(
    requests, organism="", organ="", disease="", cell_type="", size=10
):
    """Filter datasets by facets"""
    facet_parts, missing_parts = build_facets_string(
        requests, organism, organ, disease, cell_type
    )

    if not facet_parts and not missing_parts:
        # No conditions entered
        return [], [], "default"

    if missing_parts:
        # ID not found for some conditions, use keyword search
        keyword = " ".join(missing_parts)
        return search_by_keyword(requests, keyword, size), [keyword], "keyword"

    # Search using facets
    url = f"{API_BASE}/search"
    params = {"facets": ",".join(facet_parts), "size": size}

    try:
        response = requests.get(url, params=params, timeout=60, verify=False)
        data = response.json()
        return data.get("studies", []), [], "facets"
    except Exception as e:
        print(f"[warn] Facets Search failed，Return to keyword search: {e}")
        return (
            search_by_keyword(requests, " ".join(facet_parts), size),
            facet_parts,
            "keyword",
        )


def search_by_keyword(requests, keyword: str, size: int = 10):
    """Search datasets by keywords"""
    if not keyword:
        keyword = "single cell"

    url = f"{API_BASE}/search"
    params = {"q": keyword, "size": size}

    try:
        response = requests.get(url, params=params, timeout=60, verify=False)
        data = response.json()
        return data.get("studies", [])
    except Exception as e:
        print(f"[warn] Keyword search failed: {e}")
        return []


def print_studies(studies, search_type="", keyword=""):
    """Print search results"""
    if not studies:
        print("[Tip] No matching data set found")
        return

    if keyword:
        print(f"\nkeywords '{keyword}' Related results：\n")
    elif search_type == "facets":
        print(f"\nturn up {len(studies)} eligible data sets：\n")
    else:
        print(f"\nturn up {len(studies)} data sets：\n")

    for i, study in enumerate(studies, 1):
        name = study.get("name", "Unknown")[:65]
        accession = study.get("accession", "N/A")
        cell_count = study.get("cell_count", "N/A")

        print(f"{i}. {name}")
        print(f"   Accession: {accession}")
        if isinstance(cell_count, int):
            print(f"   Cells: {cell_count:,}")
        else:
            print(f"   Cells: {cell_count}")
        print()


def interactive_query(requests):
    """interactive query"""
    print("=" * 60)
    print("Single Cell Portal Interactive Query")
    print("=" * 60)

    print("Please enter filter conditions (just press Enter to skip):")
    organism = input("Species (human/mouse):").strip()
    organ = input("Organization (lung/brain/liver):").strip()
    disease = input("Disease (normal/cancer):").strip()
    cell_type = input("Cell type (T cell/neuron):").strip()
    size = input("Return quantity [10]:").strip()

    size_int = int(size) if size.isdigit() else 10

    print(f"\n[INFO] English...")

    studies, keyword, search_type = search_by_facets(
        requests, organism, organ, disease, cell_type, size_int
    )

    if keyword:
        print(f"[hint] Search using keywords: '{keyword}'")
    else:
        print(f"[hint] use Facets Precise filtering")

    print_studies(
        studies,
        search_type,
        " ".join(keyword) if isinstance(keyword, list) else keyword,
    )

    return studies


def main():
    requests = require_requests()

    # Check command line parameters
    if len(sys.argv) > 1:
        # Command line mode: keyword search
        keyword = " ".join(sys.argv[1:])
        print(f"[INFO] Search keywords: '{keyword}'")
        studies = search_by_keyword(requests, keyword)
        print_studies(studies, "keyword", keyword)
    else:
        # interactive mode
        interactive_query(requests)

    print("\n" + "=" * 60)
    print("Query completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
