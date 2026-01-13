#!/usr/bin/env python3
"""
Query NCBI for available genome assemblies by taxon name

Usage:
    python query_ncbi_assemblies.py --taxon "Coleoptera"
    python query_ncbi_assemblies.py --taxon "Drosophila" --max-results 50
    python query_ncbi_assemblies.py --taxon "Apis" --refseq-only

Requires: ncbi-datasets-pylib (pip install ncbi-datasets-pylib)

Author: Bruno de Medeiros (Field Museum)
"""

import argparse
import sys


def query_assemblies_by_taxon(taxon, max_results=20, refseq_only=False):
    """
    Query NCBI for genome assemblies of a given taxon

    Args:
        taxon: Taxon name (e.g., "Coleoptera", "Drosophila melanogaster")
        max_results: Maximum number of results to return
        refseq_only: If True, only return RefSeq assemblies (GCF_*)

    Returns:
        List of dictionaries with assembly information
    """
    try:
        from ncbi.datasets import GenomeApi
        from ncbi.datasets.openapi import ApiClient, ApiException
    except ImportError:
        print("Error: ncbi-datasets-pylib not installed", file=sys.stderr)
        print("Install with: pip install ncbi-datasets-pylib", file=sys.stderr)
        sys.exit(1)

    assemblies = []

    print(f"Querying NCBI for '{taxon}' genome assemblies...")
    print(f"(Limiting to {max_results} results)")
    if refseq_only:
        print("(RefSeq assemblies only)")
    print("")

    try:
        with ApiClient() as api_client:
            api = GenomeApi(api_client)

            # Query genome assemblies for the taxon
            genome_summary = api.genome_summary_by_taxon(
                taxon=taxon,
                limit=str(max_results),
                filters_refseq_only=refseq_only
            )

            if not genome_summary.reports:
                print(f"No assemblies found for taxon '{taxon}'")
                return []

            for report in genome_summary.reports:
                assembly_info = {
                    'accession': report.accession,
                    'organism': report.organism.organism_name,
                    'assembly_level': report.assembly_info.assembly_level,
                    'assembly_name': report.assembly_info.assembly_name,
                    'submission_date': report.assembly_info.release_date if hasattr(report.assembly_info, 'release_date') else 'N/A'
                }
                assemblies.append(assembly_info)

    except ApiException as e:
        print(f"Error querying NCBI: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    return assemblies


def format_table(assemblies):
    """
    Format assemblies as a readable table

    Args:
        assemblies: List of assembly dictionaries
    """
    if not assemblies:
        return

    print(f"Found {len(assemblies)} assemblies:\n")

    # Print header
    print(f"{'#':<4} {'Accession':<20} {'Organism':<40} {'Level':<15} {'Assembly Name':<30}")
    print("-" * 110)

    # Print data rows
    for i, asm in enumerate(assemblies, 1):
        organism = asm['organism'][:38] + '..' if len(asm['organism']) > 40 else asm['organism']
        assembly_name = asm['assembly_name'][:28] + '..' if len(asm['assembly_name']) > 30 else asm['assembly_name']

        print(f"{i:<4} {asm['accession']:<20} {organism:<40} {asm['assembly_level']:<15} {assembly_name:<30}")

    print("")


def save_accessions(assemblies, output_file):
    """
    Save assembly accessions to a file

    Args:
        assemblies: List of assembly dictionaries
        output_file: Output file path
    """
    with open(output_file, 'w') as f:
        for asm in assemblies:
            f.write(f"{asm['accession']}\n")

    print(f"Accessions saved to: {output_file}")
    print(f"You can download these assemblies using:")
    print(f"  python download_ncbi_genomes.py --assemblies $(cat {output_file})")


def main():
    parser = argparse.ArgumentParser(
        description="Query NCBI for available genome assemblies by taxon name",
        epilog="Example: python query_ncbi_assemblies.py --taxon 'Coleoptera' --max-results 50"
    )

    parser.add_argument(
        "--taxon",
        required=True,
        help="Taxon name (e.g., 'Coleoptera', 'Drosophila melanogaster')"
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
        "--save",
        metavar="FILE",
        help="Save accessions to a file for later download"
    )

    args = parser.parse_args()

    # Query NCBI
    assemblies = query_assemblies_by_taxon(
        taxon=args.taxon,
        max_results=args.max_results,
        refseq_only=args.refseq_only
    )

    # Display results
    format_table(assemblies)

    # Save if requested
    if args.save and assemblies:
        save_accessions(assemblies, args.save)


if __name__ == "__main__":
    main()
