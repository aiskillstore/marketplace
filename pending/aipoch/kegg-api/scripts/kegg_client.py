import sys
import argparse
import urllib.request
import urllib.error

BASE_URL = "https://rest.kegg.jp"

def call_kegg(operation, args, option=None):
    # Construct URL
    # Format: BASE_URL/<operation>/<arg1>/<arg2>/...[/<option>]
    
    url_parts = [BASE_URL, operation]
    
    if args:
        url_parts.extend(args)
        
    if option:
        url_parts.append(option)
        
    # Ensure no double slashes and correct joining
    # p.strip('/') might be dangerous if arg is just "/", but args are usually IDs.
    # Safe approach: join with /
    url = "/".join([str(p).strip("/") for p in url_parts])
    
    print(f"Requesting: {url}", file=sys.stderr)
    
    try:
        # User-Agent is often required or good practice
        req = urllib.request.Request(url, headers={'User-Agent': 'Trae-Skill/1.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print(f"Error: HTTP {e.code} - {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: URL Error - {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="KEGG API Client")
    parser.add_argument("operation", choices=["info", "list", "find", "get", "conv", "link", "ddi"], help="API operation")
    parser.add_argument("args", nargs="*", help="Arguments for the operation (database, query, etc.)")
    parser.add_argument("--option", help="Optional parameter (e.g., formula, exact_mass, image)")
    
    args = parser.parse_args()
    
    result = call_kegg(args.operation, args.args, args.option)
    print(result)

if __name__ == "__main__":
    main()
