#!/usr/bin/env python3
"""
Backlinks analysis using DataForSEO API
Usage: python3 scripts/backlinks.py "example.com" --limit 20
"""
import argparse
from dataforseo_api import api_post, get_result, print_backlinks_list, format_count


def main():
    parser = argparse.ArgumentParser(description="Backlinks analysis")
    parser.add_argument("target", help="Target domain")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Max results")
    args = parser.parse_args()

    data = [{
        "target": args.target,
        "limit": args.limit,
        "order_by": ["rank,desc"]
    }]
    
    response = api_post("backlinks/backlinks/live", data)
    results = get_result(response)
    
    print(f"target: {args.target}")
    
    if results:
        result = results[0]
        print(f"total_backlinks: {format_count(result.get('total_count'))}")
        items = result.get("items", [])
        print_backlinks_list(items[:args.limit])
    else:
        print("No results found")


if __name__ == "__main__":
    main()
