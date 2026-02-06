#!/usr/bin/env python3
"""
Related keywords from Google "searches related to" using DataForSEO API
Get up to 4,680 keyword ideas from Google's related searches

Usage: python3 scripts/related_keywords.py "AI agent" --depth 2 --limit 50
"""
import argparse
from dataforseo_api import api_post, get_result, format_count


def main():
    parser = argparse.ArgumentParser(description="Related keywords from Google")
    parser.add_argument("keyword", help="Seed keyword")
    parser.add_argument("--location", "-loc", type=int, default=2840,
                        help="Location code (default: 2840 = US)")
    parser.add_argument("--depth", "-d", type=int, default=1,
                        help="Search depth 1-3 (default: 1, max keywords: depth^3 * 10)")
    parser.add_argument("--limit", "-l", type=int, default=50, 
                        help="Max results to display (default: 50)")
    args = parser.parse_args()

    # Validate depth
    if args.depth < 1 or args.depth > 3:
        print("Error: depth must be between 1 and 3")
        return

    data = [{
        "keyword": args.keyword,
        "location_code": args.location,
        "language_code": "en",
        "depth": args.depth,
        "limit": 1000  # API limit, we'll filter in display
    }]
    
    response = api_post("dataforseo_labs/google/related_keywords/live", data)
    results = get_result(response)
    
    print(f"keyword: {args.keyword}")
    print(f"location: {args.location}")
    print(f"depth: {args.depth}")
    print()
    
    if results:
        keywords = []
        for result in results:
            items = result.get("items", [])
            for item in items:
                kw_data = item.get("keyword_data", {})
                keyword = kw_data.get("keyword", item.get("keyword", ""))
                volume = kw_data.get("search_volume", item.get("search_volume", 0))
                difficulty = kw_data.get("keyword_difficulty", item.get("keyword_difficulty", "N/A"))
                
                if keyword:
                    keywords.append({
                        "keyword": keyword,
                        "volume": volume if volume is not None else 0,
                        "difficulty": difficulty
                    })
        
        # Sort by volume desc
        keywords.sort(key=lambda x: x["volume"], reverse=True)
        
        # Display limited results
        display_keywords = keywords[:args.limit]
        print(f"related_keywords[{len(display_keywords)} of {len(keywords)}]{{keyword,volume,difficulty}}:")
        for kw in display_keywords:
            keyword = kw["keyword"]
            volume = format_count(kw["volume"])
            difficulty = kw["difficulty"]
            print(f"  {keyword},{volume},{difficulty}")
        
        if len(keywords) > args.limit:
            print(f"\n... and {len(keywords) - args.limit} more keywords (use --limit to show more)")
    else:
        print("No related keywords found")
    
    print()
    print("Tip: Higher depth finds more keywords but costs more API credits")
    print(f"  Depth 1: ~10 keywords, Depth 2: ~100, Depth 3: ~1,000+")


if __name__ == "__main__":
    main()
