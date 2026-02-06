#!/usr/bin/env python3
"""
SERP analysis using DataForSEO API
Usage: python3 scripts/serp_analysis.py "best seo tools" --depth 20
"""
import argparse
from dataforseo_api import api_post, get_result, print_serp_list, format_count


def main():
    parser = argparse.ArgumentParser(description="SERP analysis")
    parser.add_argument("keyword", help="Search keyword")
    parser.add_argument("--location", "-loc", type=int, default=2840,
                        help="Location code (default: 2840 = US)")
    parser.add_argument("--depth", "-d", type=int, default=20, help="Search depth")
    args = parser.parse_args()

    data = [{
        "keyword": args.keyword,
        "location_code": args.location,
        "language_code": "en",
        "depth": args.depth
    }]
    
    response = api_post("serp/google/organic/live/advanced", data)
    results = get_result(response)
    
    print(f"keyword: {args.keyword}")
    print(f"location: {args.location}")
    
    if results:
        result = results[0]
        print(f"total_results: {format_count(result.get('se_results_count'))}")
        items = result.get("items", [])
        print_serp_list(items)
    else:
        print("No results found")


if __name__ == "__main__":
    main()
