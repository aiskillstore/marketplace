import argparse
import json
import sys
import requests

def main():
    parser = argparse.ArgumentParser(description="Ensembl Database Query Tool")
    parser.add_argument("--action", required=True, choices=["lookup", "sequence", "vep"], help="Action to perform")
    parser.add_argument("--species", help="Species (e.g., human)")
    parser.add_argument("--symbol", help="Gene symbol (e.g., BRCA2)")
    parser.add_argument("--id", help="Ensembl ID")
    parser.add_argument("--hgvs", help="HGVS notation for VEP")
    
    args = parser.parse_args()
    
    # Try to import ensembl_rest, otherwise use requests directly as fallback
    try:
        from ensembl_rest import EnsemblClient
        client = EnsemblClient()
        use_library = True
    except ImportError:
        use_library = False
        # Fallback to requests if library is missing (to ensure it works in basic envs)
        base_url = "https://rest.ensembl.org"
        headers = {"Content-Type": "application/json"}

    result = None

    try:
        if args.action == "lookup":
            if not args.species or not args.symbol:
                print("Error: --species and --symbol are required for lookup", file=sys.stderr)
                sys.exit(1)
            
            if use_library:
                result = client.symbol_lookup(species=args.species, symbol=args.symbol)
            else:
                ext = f"/lookup/symbol/{args.species}/{args.symbol}?"
                r = requests.get(base_url + ext, headers=headers)
                if not r.ok:
                    r.raise_for_status()
                result = r.json()

        elif args.action == "sequence":
            if not args.id:
                print("Error: --id is required for sequence", file=sys.stderr)
                sys.exit(1)
            
            if use_library:
                result = client.sequence_id(id=args.id)
            else:
                ext = f"/sequence/id/{args.id}?"
                r = requests.get(base_url + ext, headers=headers)
                if not r.ok:
                    r.raise_for_status()
                result = r.json()

        elif args.action == "vep":
            if not args.species or not args.hgvs:
                print("Error: --species and --hgvs are required for vep", file=sys.stderr)
                sys.exit(1)
            
            if use_library:
                # Assuming standard method name pattern or documented method
                if hasattr(client, 'vep_hgvs'):
                    result = client.vep_hgvs(species=args.species, hgvs=args.hgvs)
                else:
                    # Fallback if method name guess is wrong
                    print("Error: VEP method not found in installed ensembl_rest library.", file=sys.stderr)
                    sys.exit(1)
            else:
                ext = f"/vep/{args.species}/hgvs/{args.hgvs}?"
                r = requests.get(base_url + ext, headers=headers)
                if not r.ok:
                    r.raise_for_status()
                result = r.json()

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"Error executing query: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
