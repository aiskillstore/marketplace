import sys
import json
import urllib.parse
import urllib.request
import argparse

BASE_URL = "https://api.cellosaurus.org"

def make_request(url):
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Trae-Skill-Client/1.0'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        sys.exit(1)

def get_release_info(format='json'):
    url = f"{BASE_URL}/release-info?format={format}"
    return make_request(url)

def get_cell_line(ac, format='json', fields=None):
    params = {'format': format}
    if fields:
        params['fields'] = fields
    
    query_string = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/cell-line/{ac}?{query_string}"
    return make_request(url)

def search_cell_lines(query, rows=10, format='json', fields=None, sort=None):
    params = {
        'q': query,
        'rows': rows,
        'format': format
    }
    if fields:
        params['fields'] = fields
    if sort:
        params['sort'] = sort
        
    query_string = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/search/cell-line?{query_string}"
    return make_request(url)

def main():
    parser = argparse.ArgumentParser(description="Cellosaurus API Client")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Release Info
    info_parser = subparsers.add_parser("info", help="Get release information")
    info_parser.add_argument("--format", default="json", choices=["json", "xml", "txt", "tsv"], help="Output format")
    
    # Get Cell Line
    get_parser = subparsers.add_parser("get", help="Get cell line details")
    get_parser.add_argument("ac", help="Accession number (e.g., CVCL_0030)")
    get_parser.add_argument("--format", default="json", choices=["json", "xml", "txt", "tsv"], help="Output format")
    get_parser.add_argument("--fields", help="Comma-separated list of fields to return")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search cell lines")
    search_parser.add_argument("query", help="Search query (e.g., id:HeLa)")
    search_parser.add_argument("--rows", type=int, default=10, help="Number of rows to return")
    search_parser.add_argument("--format", default="json", choices=["json", "xml", "txt", "tsv"], help="Output format")
    search_parser.add_argument("--fields", help="Comma-separated list of fields to return")
    search_parser.add_argument("--sort", help="Sort order (e.g., 'group asc')")
    
    args = parser.parse_args()
    
    if args.command == "info":
        print(get_release_info(args.format))
    elif args.command == "get":
        print(get_cell_line(args.ac, args.format, args.fields))
    elif args.command == "search":
        print(search_cell_lines(args.query, args.rows, args.format, args.fields, args.sort))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
