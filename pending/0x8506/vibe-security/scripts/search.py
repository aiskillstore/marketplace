#!/usr/bin/env python3
"""
Search utility for Vibe Security skill
Usage: python3 search.py "<keyword>" --domain <domain> [-n <max_results>]
"""
import argparse
import sys
from pathlib import Path

# Add parent directory to path to import core
sys.path.insert(0, str(Path(__file__).parent))
from core import (
    search_vulnerabilities,
    search_patterns,
    search_rules,
    search_frameworks,
    format_result
)


def main():
    parser = argparse.ArgumentParser(
        description="Search Vibe Security knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for SQL injection vulnerabilities
  python3 search.py "sql" --domain vulnerability
  
  # Search for JavaScript security patterns
  python3 search.py "javascript" --domain pattern
  
  # Search for authentication rules
  python3 search.py "auth" --domain rule
  
  # Get Express.js security best practices
  python3 search.py "express" --domain framework
  
  # Search JavaScript patterns with critical severity
  python3 search.py "javascript" --domain pattern --severity critical
        """
    )
    
    parser.add_argument(
        "keyword",
        help="Keyword to search for"
    )
    
    parser.add_argument(
        "--domain",
        choices=["vulnerability", "pattern", "rule", "framework"],
        default="vulnerability",
        help="Domain to search in (default: vulnerability)"
    )
    
    parser.add_argument(
        "--language",
        help="Filter patterns by language (javascript, python, php, etc.)"
    )
    
    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low"],
        help="Filter by severity level"
    )
    
    parser.add_argument(
        "-n", "--max-results",
        type=int,
        default=5,
        help="Maximum number of results (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Perform search based on domain
    results = []
    result_type = args.domain
    
    if args.domain == "vulnerability":
        results = search_vulnerabilities(args.keyword, args.max_results)
    elif args.domain == "pattern":
        results = search_patterns(
            language=args.language or args.keyword,
            severity=args.severity,
            max_results=args.max_results
        )
    elif args.domain == "rule":
        results = search_rules(args.keyword, args.max_results)
    elif args.domain == "framework":
        results = search_frameworks(args.keyword)
    
    # Display results
    if not results:
        print(f"No results found for '{args.keyword}' in {args.domain} domain.")
        return
    
    print(f"\n{'='*60}")
    print(f"Search Results: '{args.keyword}' in {args.domain.upper()}")
    print(f"{'='*60}")
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(format_result(result, result_type))
    
    print(f"\n{'='*60}")
    print(f"Found {len(results)} result(s)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
