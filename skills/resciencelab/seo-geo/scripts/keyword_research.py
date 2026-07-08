#!/usr/bin/env python3
"""
Keyword research using DataForSEO API
Usage: python3 scripts/keyword_research.py "seo tools" --limit 20
"""
import argparse
from dataforseo_api import api_post, get_result, print_keywords_list


def main():
    parser = argparse.ArgumentParser(description="Keyword research")
    parser.add_argument("keyword", help="Seed keyword")
    parser.add_argument("--location", "-loc", type=int, default=2840,
                        help="Location code (default: 2840 = US)")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Max results")
    args = parser.parse_args()

    data = [{
        "keywords": [args.keyword],  # API requires 'keywords' array (up to 20)
        "location_code": args.location,
        "language_code": "en",
        "limit": args.limit
    }]
    
    response = api_post("keywords_data/google_ads/keywords_for_keywords/live", data)
    results = get_result(response)
    
    print(f"keyword: {args.keyword}")
    print(f"location: {args.location}")
    
    if results:
        print_keywords_list(results[:args.limit])
    else:
        print("No results found")


if __name__ == "__main__":
    main()
