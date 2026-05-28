import requests
import json
import sys
import argparse
from typing import Optional

BASE_URL = "https://rest.genenames.org"
HEADERS = {"Accept": "application/json"}

def get_info():
    """Retrieves information about the HGNC REST service."""
    url = f"{BASE_URL}/info"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def fetch(term: str, field: str = "symbol"):
    """
    Fetches data for a specific term in a specific field.
    Default field is 'symbol'.
    """
    # URL encode is handled by requests usually, but for path params we might need care.
    # requests doesn't auto-encode path params if we construct string manually.
    # However, for simple usage, f-string is usually okay unless special chars.
    # The docs mention spaces should be %20.
    
    url = f"{BASE_URL}/fetch/{field}/{term}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def search(term: str, field: Optional[str] = None):
    """
    Searches for a term.
    If field is provided: search/{field}/{term}
    If field is NOT provided: search/{term}
    """
    if field:
        url = f"{BASE_URL}/search/{field}/{term}"
    else:
        url = f"{BASE_URL}/search/{term}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="HGNC API Client")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Info command
    subparsers.add_parser("info", help="Get service info")

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch gene details")
    fetch_parser.add_argument("term", help="The term to fetch (e.g., BRAF)")
    fetch_parser.add_argument("--field", default="symbol", help="The field to query (default: symbol)")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for genes")
    search_parser.add_argument("term", help="The search term")
    search_parser.add_argument("--field", help="The specific field to search in (optional)")

    args = parser.parse_args()

    if args.command == "info":
        result = get_info()
    elif args.command == "fetch":
        result = fetch(args.term, args.field)
    elif args.command == "search":
        result = search(args.term, args.field)
    else:
        parser.print_help()
        return

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
