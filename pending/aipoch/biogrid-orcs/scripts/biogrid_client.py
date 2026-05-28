import argparse
import json
import sys
import urllib.request
import urllib.parse
from typing import Dict, Any

BASE_URL = "https://orcsws.thebiogrid.org"

def make_request(endpoint: str, params: Dict[str, Any]) -> Any:
    # Ensure accesskey is present
    if 'accesskey' not in params or not params['accesskey']:
        print("Error: accesskey is required. Please provide it via --accesskey argument.", file=sys.stderr)
        sys.exit(1)
    
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    
    # Default format to json
    if 'format' not in params:
        params['format'] = 'json'
        
    query_string = urllib.parse.urlencode(params)
    url = f"{BASE_URL}{endpoint}?{query_string}"
    
    try:
        # User-Agent is often good practice
        req = urllib.request.Request(url, headers={'User-Agent': 'BioGRID-ORCS-Skill/1.0'})
        with urllib.request.urlopen(req) as response:
            data = response.read()
            if params.get('format') == 'json':
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    return data.decode('utf-8')
            return data.decode('utf-8')
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="BioGRID ORCS API Client")
    subparsers = parser.add_subparsers(dest="command", help="API Operation")
    
    # Common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--accesskey", required=True, help="BioGRID Access Key")
    parent_parser.add_argument("--format", default="json", choices=["json", "tab"], help="Output format")
    parent_parser.add_argument("--header", choices=["yes", "no"], default="no", help="Include header (tab format only)")

    # 1. /organisms/
    subparsers.add_parser("organisms", parents=[parent_parser], help="Fetch Supported Organisms List")
    
    # 2. /vocabs/
    subparsers.add_parser("vocabs", parents=[parent_parser], help="Fetch Controlled Vocabulary Categories")
    
    # 3. /vocab/<ID>
    vocab_parser = subparsers.add_parser("vocab", parents=[parent_parser], help="Fetch terms in a vocabulary category")
    vocab_parser.add_argument("category_id", help="Vocabulary Category ID")
    
    # 4. /screens/
    screens_parser = subparsers.add_parser("screens", parents=[parent_parser], help="Fetch list of screens")
    screens_parser.add_argument("--start", type=int, help="Start index (pagination)")
    screens_parser.add_argument("--max", type=int, help="Max results")
    screens_parser.add_argument("--screenType", help="Filter by screen type")
    screens_parser.add_argument("--throughput", help="Filter by throughput")
    screens_parser.add_argument("--experimentalSetup", help="Filter by experimental setup")
    screens_parser.add_argument("--conditionName", help="Filter by condition name")
    screens_parser.add_argument("--libraryName", help="Filter by library name")
    screens_parser.add_argument("--libraryType", help="Filter by library type")
    screens_parser.add_argument("--libraryMethodology", help="Filter by library methodology")
    screens_parser.add_argument("--screenFormat", help="Filter by screen format")
    screens_parser.add_argument("--enzyme", help="Filter by enzyme")
    screens_parser.add_argument("--cellLine", help="Filter by cell line")
    screens_parser.add_argument("--cellType", help="Filter by cell type")
    screens_parser.add_argument("--phenotype", help="Filter by phenotype")
    screens_parser.add_argument("--statisticalAnalysis", help="Filter by statistical analysis")
    screens_parser.add_argument("--organismID", help="Filter by organism ID")
    screens_parser.add_argument("--pubmedID", help="Filter by pubmed ID")
    screens_parser.add_argument("--screenID", help="Filter by screen ID")

    # 5. /screen/<ID>
    screen_parser = subparsers.add_parser("screen", parents=[parent_parser], help="Fetch scores for a single screen")
    screen_parser.add_argument("screen_id", help="Screen ID")
    screen_parser.add_argument("--hit", choices=["yes", "no", "all"], default="all", help="Filter by hit significance")
    screen_parser.add_argument("--idType", help="Identifier types (gene, unknown, ambiguous)")
    screen_parser.add_argument("--geneID", help="Filter by gene IDs")
    screen_parser.add_argument("--name", help="Filter by official symbols")
    # Score min/max params can be handled generically if needed, but let's add a few common ones or rely on flexible parsing?
    # To keep it simple, we won't add scoreXMin/Max individually as arguments unless requested. 
    # Users can modify script if needed for those specific numeric filters.

    # 6. /gene/<ID>
    gene_parser = subparsers.add_parser("gene", parents=[parent_parser], help="Fetch scores for a single gene across screens")
    gene_parser.add_argument("gene_id", help="Gene ID")
    gene_parser.add_argument("--hit", choices=["yes", "no", "all"], default="all", help="Filter by hit significance")

    # 7. /genes/
    genes_parser = subparsers.add_parser("genes", parents=[parent_parser], help="Fetch scores for multiple genes")
    genes_parser.add_argument("--geneID", help="Pipe-separated list of gene IDs")
    genes_parser.add_argument("--name", help="Pipe-separated list of official symbols")
    genes_parser.add_argument("--organismID", help="Filter by organism ID")
    genes_parser.add_argument("--hit", choices=["yes", "no", "all"], default="all", help="Filter by hit significance")

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Construct params dictionary
    params = vars(args).copy()
    command = params.pop('command')
    
    # Remove command-specific positional args from params to avoid sending them as query params if not needed
    if command == 'vocab':
        category_id = params.pop('category_id')
        endpoint = f"/vocab/{category_id}"
    elif command == 'screen':
        screen_id = params.pop('screen_id')
        endpoint = f"/screen/{screen_id}"
    elif command == 'gene':
        gene_id = params.pop('gene_id')
        endpoint = f"/gene/{gene_id}"
    else:
        endpoint = f"/{command}/"

    result = make_request(endpoint, params)
    
    if params.get('format') == 'json':
        print(json.dumps(result, indent=2))
    else:
        print(result)

if __name__ == "__main__":
    main()
