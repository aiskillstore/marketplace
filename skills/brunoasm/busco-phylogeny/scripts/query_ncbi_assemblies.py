#!/usr/bin/env python3
"""
Query NCBI for available genome assemblies using command-line tools

Requires: NCBI datasets command-line tool
Install: https://www.ncbi.nlm.nih.gov/datasets/docs/v2/download-and-install/

Author: Bruno de Medeiros (Field Museum)
"""

import argparse
import json
import subprocess
import sys
import shutil


def check_datasets_installed():
    """Check if datasets CLI tool is installed"""
    if not shutil.which('datasets'):
        print("Error: 'datasets' command-line tool not found", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please install NCBI datasets CLI tool:", file=sys.stderr)
        print("  https://www.ncbi.nlm.nih.gov/datasets/docs/v2/download-and-install/", file=sys.stderr)
        sys.exit(1)


def format_number(num):
    """Format large numbers with commas"""
    if num is None or num == 'N/A':
        return 'N/A'
    try:
        return f"{int(num):,}"
    except (ValueError, TypeError):
        return str(num)


def query_assemblies_by_taxon(taxon, max_results=20, refseq_only=False,
                               assembly_level=None, min_contig_n50=None,
                               annotated_only=False):
    """
    Query NCBI for genome assemblies using datasets CLI tool

    Args:
        taxon: Taxon name (e.g., "Felidae", "Drosophila melanogaster")
        max_results: Maximum number of results to return
        refseq_only: If True, only return RefSeq assemblies (GCF_*)
        assembly_level: Filter by assembly level (Chromosome, Scaffold, Contig)
        min_contig_n50: Minimum contig N50 value
        annotated_only: If True, only return annotated assemblies

    Returns:
        List of dictionaries with assembly information
    """
    assemblies = []

    print(f"Querying NCBI for '{taxon}' genome assemblies...")
    print(f"(Limiting to {max_results} results)")
    if refseq_only:
        print("(RefSeq assemblies only)")
    if annotated_only:
        print("(Annotated assemblies only)")
    if assembly_level:
        print(f"(Assembly level: {assembly_level})")
    if min_contig_n50:
        print(f"(Minimum contig N50: {format_number(min_contig_n50)})")
    print("")

    # Build command - request more results than needed for filtering
    search_limit = max_results * 5 if (assembly_level or min_contig_n50 or annotated_only) else max_results

    cmd = [
        'datasets', 'summary', 'genome', 'taxon', taxon,
        '--limit', str(search_limit),
        '--as-json-lines'
    ]

    if refseq_only:
        cmd.extend(['--reference', '--annotated'])

    try:
        # Execute command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Parse JSON Lines output
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            try:
                data = json.loads(line)

                # Extract assembly info
                asm_info = data.get('assembly_info', {})
                asm_stats = data.get('assembly_stats', {})
                annot_info = data.get('annotation_info', {})

                # Get assembly level
                level = asm_info.get('assembly_level', 'N/A')

                # Apply assembly level filter
                if assembly_level and level != assembly_level:
                    continue

                # Get contig N50
                contig_n50 = asm_stats.get('contig_n50', None)

                # Apply contig N50 filter
                if min_contig_n50 and (contig_n50 is None or contig_n50 < min_contig_n50):
                    continue

                # Apply annotation filter
                if annotated_only and not annot_info:
                    continue

                # Extract BUSCO scores if available
                busco_complete = None
                if annot_info and 'busco' in annot_info:
                    busco_data = annot_info['busco']
                    busco_complete = busco_data.get('complete', None)
                    if busco_complete:
                        busco_complete = round(busco_complete * 100, 1)

                # Extract relevant fields
                assembly_info = {
                    'accession': data.get('accession', 'N/A'),
                    'organism': data.get('organism', {}).get('organism_name', 'N/A'),
                    'assembly_level': level,
                    'assembly_name': asm_info.get('assembly_name', 'N/A'),
                    'contig_n50': contig_n50,
                    'scaffold_n50': asm_stats.get('scaffold_n50', None),
                    'total_length': asm_stats.get('total_sequence_length', None),
                    'busco_complete': busco_complete,
                    'annotated': 'Yes' if annot_info else 'No'
                }
                assemblies.append(assembly_info)

                # Stop if we have enough results
                if len(assemblies) >= max_results:
                    break

            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse line: {e}", file=sys.stderr)
                continue

        if not assemblies:
            print(f"No assemblies found matching criteria for taxon '{taxon}'")

    except subprocess.CalledProcessError as e:
        print(f"Error running datasets command: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    return assemblies


def format_table(assemblies, show_quality=False):
    """Format assemblies as a readable table"""
    if not assemblies:
        return

    print(f"Found {len(assemblies)} assemblies:\n")

    if show_quality:
        # Extended table with quality metrics
        print(f"{'#':<4} {'Accession':<20} {'Organism':<30} {'Level':<12} {'Contig N50':<15} {'BUSCO %':<10} {'Annot':<6}")
        print("-" * 100)

        for i, asm in enumerate(assemblies, 1):
            organism = asm['organism'][:28] + '..' if len(asm['organism']) > 30 else asm['organism']
            contig_n50 = format_number(asm['contig_n50'])
            busco = f"{asm['busco_complete']}%" if asm['busco_complete'] else 'N/A'

            print(f"{i:<4} {asm['accession']:<20} {organism:<30} {asm['assembly_level']:<12} {contig_n50:<15} {busco:<10} {asm['annotated']:<6}")
    else:
        # Simple table
        print(f"{'#':<4} {'Accession':<20} {'Organism':<40} {'Level':<15} {'Assembly Name':<30}")
        print("-" * 110)

        for i, asm in enumerate(assemblies, 1):
            organism = asm['organism'][:38] + '..' if len(asm['organism']) > 40 else asm['organism']
            assembly_name = asm['assembly_name'][:28] + '..' if len(asm['assembly_name']) > 30 else asm['assembly_name']

            print(f"{i:<4} {asm['accession']:<20} {organism:<40} {asm['assembly_level']:<15} {assembly_name:<30}")

    print("")

    # Print quality summary
    if show_quality and assemblies:
        print("Quality Summary:")
        levels = {}
        for asm in assemblies:
            level = asm['assembly_level']
            levels[level] = levels.get(level, 0) + 1

        for level, count in sorted(levels.items()):
            print(f"  {level}: {count}")
        print("")


def save_accessions(assemblies, output_file):
    """Save assembly accessions to a file"""
    with open(output_file, 'w') as f:
        for asm in assemblies:
            f.write(f"{asm['accession']}\n")

    print(f"Accessions saved to: {output_file}")
    print(f"You can download these assemblies using:")
    print(f"  python download_ncbi_genomes.py --assemblies $(cat {output_file})")


def main():
    parser = argparse.ArgumentParser(
        description="Query NCBI for available genome assemblies by taxon name with quality filtering",
        epilog="""
Examples:
  # Basic query
  python query_ncbi_assemblies.py --taxon 'Felidae' --max-results 50

  # Show quality metrics
  python query_ncbi_assemblies.py --taxon 'Coleoptera' --show-quality

  # Filter for chromosome-level assemblies only
  python query_ncbi_assemblies.py --taxon 'Drosophila' --assembly-level Chromosome

  # Filter for high-quality assemblies (N50 > 1 Mbp)
  python query_ncbi_assemblies.py --taxon 'Apis' --min-contig-n50 1000000 --show-quality

  # RefSeq annotated assemblies only
  python query_ncbi_assemblies.py --taxon 'Felidae' --refseq-only --annotated
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--taxon",
        required=True,
        help="Taxon name (e.g., 'Felidae', 'Drosophila melanogaster')"
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=20,
        help="Maximum number of results to return (default: 20)"
    )

    parser.add_argument(
        "--refseq-only",
        action="store_true",
        help="Only return RefSeq assemblies (GCF_* accessions)"
    )

    parser.add_argument(
        "--assembly-level",
        choices=['Chromosome', 'Scaffold', 'Contig'],
        help="Filter by assembly level (Chromosome, Scaffold, or Contig)"
    )

    parser.add_argument(
        "--min-contig-n50",
        type=int,
        help="Minimum contig N50 value (e.g., 1000000 for 1 Mbp)"
    )

    parser.add_argument(
        "--annotated",
        action="store_true",
        help="Only return assemblies with gene annotations"
    )

    parser.add_argument(
        "--show-quality",
        action="store_true",
        help="Show quality metrics (N50, BUSCO scores) in output table"
    )

    parser.add_argument(
        "--save",
        metavar="FILE",
        help="Save accessions to a file for later download"
    )

    args = parser.parse_args()

    # Check if datasets CLI is installed
    check_datasets_installed()

    # Query NCBI
    assemblies = query_assemblies_by_taxon(
        taxon=args.taxon,
        max_results=args.max_results,
        refseq_only=args.refseq_only,
        assembly_level=args.assembly_level,
        min_contig_n50=args.min_contig_n50,
        annotated_only=args.annotated
    )

    # Display results
    format_table(assemblies, show_quality=args.show_quality)

    # Save if requested
    if args.save and assemblies:
        save_accessions(assemblies, args.save)


if __name__ == "__main__":
    main()
