#!/usr/bin/env python3
"""
Google Autocomplete keyword suggestions using DataForSEO API
Get real-time search suggestions from Google Autocomplete

Usage: python3 scripts/autocomplete_ideas.py "Claude Code"
"""
import argparse
from dataforseo_api import api_post, get_result


def main():
    parser = argparse.ArgumentParser(description="Google Autocomplete keyword suggestions")
    parser.add_argument("keyword", help="Seed keyword for autocomplete")
    parser.add_argument("--location", "-loc", type=int, default=2840,
                        help="Location code (default: 2840 = US)")
    args = parser.parse_args()

    data = [{
        "keyword": args.keyword,
        "location_code": args.location,
        "language_code": "en"
    }]
    
    response = api_post("serp/google/autocomplete/live/advanced", data)
    results = get_result(response)
    
    print(f"keyword: {args.keyword}")
    print(f"location: {args.location}")
    print()
    
    if results:
        suggestions = []
        for result in results:
            items = result.get("items", [])
            
            # Try different possible field names if items is empty
            if not items:
                items = result.get("autocomplete", [])
                if not items:
                    items = result.get("suggestions", [])
            
            for item in items:
                # Handle different response formats
                suggestion = None
                if isinstance(item, dict):
                    if item.get("type") == "autocomplete_item":
                        suggestion = item.get("title", "").strip()
                    elif "value" in item:
                        suggestion = item.get("value", "").strip()
                elif isinstance(item, str):
                    suggestion = item.strip()
                
                if suggestion:
                    suggestions.append(suggestion)
        
        if suggestions:
            print(f"autocomplete_suggestions[{len(suggestions)}]:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("No suggestions found")
    else:
        print("No results found")
    
    print()
    print("Tip: These are real user searches. Use them to:")
    print("  - Create content matching user intent")
    print("  - Optimize page titles and meta descriptions")
    print("  - Discover long-tail keyword opportunities")


if __name__ == "__main__":
    main()
