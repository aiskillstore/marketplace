import argparse
import json
import sys
from chembl_webresource_client.new_client import new_client

def search_molecule(term=None, filters=None):
    """Search for molecules using ChEMBL client."""
    molecule = new_client.molecule
    query = molecule
    
    if term:
        # Default to pref_name search if term is provided
        query = query.filter(pref_name__icontains=term)
    
    if filters:
        for key, value in filters.items():
            query = query.filter(**{key: value})
            
    return list(query[:10]) # Limit to 10 results

def search_target(term):
    """Search for targets."""
    target = new_client.target
    res = target.filter(pref_name__icontains=term)
    return list(res[:10])

def main():
    parser = argparse.ArgumentParser(description="Query ChEMBL Database")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Molecule Search
    mol_parser = subparsers.add_parser('molecule', help='Search molecules')
    mol_parser.add_argument('--term', help='Search term (name)')
    mol_parser.add_argument('--filters', help='JSON string of additional filters')

    # Target Search
    target_parser = subparsers.add_parser('target', help='Search targets')
    target_parser.add_argument('--term', required=True, help='Target name')

    args = parser.parse_args()

    results = []
    try:
        if args.command == 'molecule':
            filters = json.loads(args.filters) if args.filters else {}
            results = search_molecule(args.term, filters)
        elif args.command == 'target':
            results = search_target(args.term)
        else:
            parser.print_help()
            return

        # Output results as JSON for Claude to parse
        print(json.dumps(results, default=str, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
