#!/usr/bin/env python3
"""
Competitor keyword gap analysis using DataForSEO API
Finds keywords where competitor ranks but you don't

Usage: python3 scripts/competitor_gap.py "opc.dev" "claudemarketplaces.com" --limit 50
"""
import argparse
from dataforseo_api import api_post, get_result, format_count


def main():
    parser = argparse.ArgumentParser(description="Competitor keyword gap analysis")
    parser.add_argument("my_domain", help="Your domain (without https://)")
    parser.add_argument("competitor_domain", help="Competitor domain (without https://)")
    parser.add_argument("--location", "-loc", type=int, default=2840,
                        help="Location code (default: 2840 = US)")
    parser.add_argument("--limit", "-l", type=int, default=50, 
                        help="Max results (default: 50)")
    args = parser.parse_args()

    data = [{
        "target1": args.my_domain,
        "target2": args.competitor_domain,
        "location_code": args.location,
        "language_code": "en",
        "intersections": False,  # Only show keywords where target2 ranks but target1 doesn't
        "limit": args.limit
    }]
    
    response = api_post("dataforseo_labs/google/domain_intersection/live", data)
    results = get_result(response)
    
    print(f"my_domain: {args.my_domain}")
    print(f"competitor_domain: {args.competitor_domain}")
    print(f"location: {args.location}")
    print()
    
    if results:
        all_items = []
        for result in results:
            items = result.get("items", [])
            if items:
                all_items.extend(items)
        
        if not all_items:
            print("No keyword gaps found")
            return
        
        # Results show keywords where competitor ranks but you don't
        print(f"keyword_gaps[{len(all_items)}]{{keyword,volume,difficulty,comp_position}}:")
        for item in all_items:
            kw_data = item.get("keyword_data", {})
            keyword = kw_data.get("keyword", "N/A")
            
            # Get search volume from keyword_info
            kw_info = kw_data.get("keyword_info", {})
            volume = format_count(kw_info.get("search_volume", 0))
            
            # Get keyword difficulty
            difficulty = kw_info.get("competition_level", "N/A")
            
            # Get competitor's ranking position
            # When intersections=false, we get keywords where only second_domain (competitor) ranks
            comp_element = item.get("second_domain_serp_element")
            if comp_element and isinstance(comp_element, dict):
                comp_pos = comp_element.get("rank_absolute", comp_element.get("rank_group", "N/A"))
            else:
                comp_pos = "N/A"
            
            print(f"  {keyword},{volume},{difficulty},{comp_pos}")
    else:
        print("No keyword gaps found")
    
    print()
    print("Tip: Focus on keywords with high volume and low difficulty where competitor ranks in top 10")


if __name__ == "__main__":
    main()
