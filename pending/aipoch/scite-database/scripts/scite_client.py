import argparse
import requests
import json
import sys

def get_tallies(doi, proxies=None):
    """
    Retrieve tallies for a given DOI from Scite API.
    """
    url = f"https://api.scite.ai/tallies/{doi}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"get DOI {doi} There was an error in the statistics of: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response content: {e.response.text}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Scite database client")
    parser.add_argument("doi", help="Paper DOI to be analyzed")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--proxy", help="Proxy URL (example: http://127.0.0.1:7890)", default=None)
    
    args = parser.parse_args()
    
    proxies = None
    if args.proxy:
        proxies = {"http": args.proxy, "https": args.proxy}
    
    data = get_tallies(args.doi, proxies=proxies)
    
    if data:
        if args.format == "json":
            print(json.dumps(data, indent=2))
        else:
            print(f"--- Scite analysis report: {args.doi} ---")
            print(f"Total citations: {data.get('total', 0)}")
            print(f"support:      {data.get('supporting', 0)}")
            print(f"refute:      {data.get('contrasting', 0)}")
            print(f"mention:      {data.get('mentioning', 0)}")
            
            if 'journal' in data:
                 print(f"Journal:      {data['journal']}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
