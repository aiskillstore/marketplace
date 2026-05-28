import argparse
import json
import sys
import pandas as pd

# Try to import gget, handle missing dependency gracefully
try:
    import gget
except ImportError:
    print(json.dumps({"error": "gget module not found. Please install it using 'uv pip install gget'"}), file=sys.stderr)
    sys.exit(1)

def to_json_serializable(data):
    """Convert pandas DataFrame or other types to JSON serializable format."""
    if isinstance(data, pd.DataFrame):
        return data.to_dict(orient='records')
    if isinstance(data, list):
        return [to_json_serializable(item) for item in data]
    if isinstance(data, dict):
        return {k: to_json_serializable(v) for k, v in data.items()}
    return data

def handle_search(args):
    """Handle gget search command."""
    # gget.search(searchwords, species, limit=None, ...)
    try:
        results = gget.search(args.keywords, species=args.species)
        return results
    except Exception as e:
        return {"error": str(e)}

def handle_info(args):
    """Handle gget info command."""
    # gget.info(ens_ids, ...)
    try:
        results = gget.info(args.ids)
        return results
    except Exception as e:
        return {"error": str(e)}

def handle_seq(args):
    """Handle gget seq command."""
    # gget.seq(ens_ids, ...)
    try:
        results = gget.seq(args.ids)
        return results
    except Exception as e:
        return {"error": str(e)}

def handle_alphafold(args):
    """Handle gget alphafold command."""
    # gget.alphafold(sequence, ...)
    try:
        # Note: AlphaFold might return complex objects or trigger long running processes
        # This is a simplified wrapper
        results = gget.alphafold(args.sequence, plot=args.plot)
        return {"status": "AlphaFold prediction initiated/completed", "output": str(results)}
    except Exception as e:
        return {"error": str(e)}

def handle_ref(args):
    """Handle gget ref command."""
    try:
        results = gget.ref(args.species, which=args.which, release=args.release)
        return results
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Wrapper for gget bioinformatics tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search
    search_parser = subparsers.add_parser('search', help='Search for genes')
    search_parser.add_argument('--keywords', nargs='+', required=True, help='Keywords to search for')
    search_parser.add_argument('--species', type=str, help='Species to search in')

    # Info
    info_parser = subparsers.add_parser('info', help='Get gene information')
    info_parser.add_argument('--ids', nargs='+', required=True, help='Ensembl IDs')

    # Seq
    seq_parser = subparsers.add_parser('seq', help='Fetch sequences')
    seq_parser.add_argument('--ids', nargs='+', required=True, help='Ensembl IDs or gene names')

    # AlphaFold
    af_parser = subparsers.add_parser('alphafold', help='Predict protein structure')
    af_parser.add_argument('--sequence', type=str, required=True, help='Amino acid sequence')
    af_parser.add_argument('--plot', action='store_true', help='Generate plot')

    # Ref
    ref_parser = subparsers.add_parser('ref', help='Download reference genomes')
    ref_parser.add_argument('--species', type=str, required=True, help='Species name')
    ref_parser.add_argument('--which', nargs='+', default=['all'], help='Which files to download (gtf, fasta, etc)')
    ref_parser.add_argument('--release', type=str, help='Ensembl release version')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    result = None
    if args.command == 'search':
        result = handle_search(args)
    elif args.command == 'info':
        result = handle_info(args)
    elif args.command == 'seq':
        result = handle_seq(args)
    elif args.command == 'alphafold':
        result = handle_alphafold(args)
    elif args.command == 'ref':
        result = handle_ref(args)

    # Output formatting
    if isinstance(result, dict) and "error" in result:
        print(json.dumps(result), file=sys.stderr)
        sys.exit(1)
    
    print(json.dumps(to_json_serializable(result), indent=2))

if __name__ == "__main__":
    main()
