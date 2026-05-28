import argparse
import json
import sys
try:
    from habanero import Crossref
except ImportError:
    print("Error: habanero library not found. Please run 'pip install habanero'", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Query CrossRef Database")
    parser.add_argument("--doi", help="DOI of the work to retrieve")
    parser.add_argument("--query", help="Search query string")
    parser.add_argument("--limit", type=int, default=5, help="Number of results to return for search")
    
    args = parser.parse_args()
    
    cr = Crossref()
    # Set mailto to be polite, using a dummy or env var if available, 
    # but here we leave it default or user should configure. 
    # For now, we rely on default behavior.
    
    try:
        if args.doi:
            # Get metadata for a specific DOI
            work = cr.works(ids=args.doi)
            # Output the message part which contains the metadata
            print(json.dumps(work['message'], indent=2, ensure_ascii=False))
            
        elif args.query:
            # Search
            results = cr.works(query=args.query, limit=args.limit)
            # Output the items list
            print(json.dumps(results['message']['items'], indent=2, ensure_ascii=False))
            
        else:
            print("Error: Please provide either --doi or --query", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error querying CrossRef: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
