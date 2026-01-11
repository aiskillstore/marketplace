#!/usr/bin/env python3
"""
Download genomes from NCBI using BioProject or Assembly accessions

Usage:
    python download_ncbi_genomes.py --bioprojects PRJNA12345 PRJEB67890
    python download_ncbi_genomes.py --assemblies GCA_123456789.1 GCF_987654321.1

Requires: ncbi-datasets-pylib (pip install ncbi-datasets-pylib)

Author: Bruno de Medeiros (Field Museum)
Based on tutorials by Paul Frandsen (BYU)
"""

import argparse
import sys
import subprocess


def download_using_cli(accessions, output_file="genomes.zip"):
    """
    Download genomes using NCBI datasets CLI

    Args:
        accessions: List of BioProject or Assembly accessions
        output_file: Name of output zip file
    """
    cmd = ["datasets", "download", "genome", "accession"] + accessions + ["--filename", output_file]

    print(f"Running: {' '.join(cmd)}")
    print("")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"\nDownload complete: {output_file}")
        print("Extract with: unzip " + output_file)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading genomes: {e}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Error: 'datasets' command not found", file=sys.stderr)
        print("Install with: conda install -c conda-forge ncbi-datasets-cli", file=sys.stderr)
        return False


def get_bioproject_assemblies(bioprojects):
    """
    Get assembly accessions for given BioProjects using Python API

    Args:
        bioprojects: List of BioProject accessions

    Returns:
        List of tuples (assembly_accession, organism_name)
    """
    try:
        from ncbi.datasets.metadata.genome import get_assembly_metadata_by_bioproject_accessions
    except ImportError:
        print("Error: ncbi-datasets-pylib not installed", file=sys.stderr)
        print("Install with: pip install ncbi-datasets-pylib", file=sys.stderr)
        sys.exit(1)

    assemblies = []

    print(f"Fetching assembly information for {len(bioprojects)} BioProject(s)...")
    print("")

    for assembly in get_assembly_metadata_by_bioproject_accessions(bioprojects):
        acc = assembly.accession
        name = assembly.organism.organism_name
        assemblies.append((acc, name))
        print(f"  {name}: {acc}")

    print(f"\nFound {len(assemblies)} assemblies")

    return assemblies


def main():
    parser = argparse.ArgumentParser(
        description="Download genomes from NCBI using BioProject or Assembly accessions"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--bioprojects",
        nargs="+",
        help="BioProject accessions (e.g., PRJNA12345 PRJEB67890)"
    )
    group.add_argument(
        "--assemblies",
        nargs="+",
        help="Assembly accessions (e.g., GCA_123456789.1 GCF_987654321.1)"
    )

    parser.add_argument(
        "-o", "--output",
        default="genomes.zip",
        help="Output zip file name (default: genomes.zip)"
    )

    parser.add_argument(
        "--list-only",
        action="store_true",
        help="List assemblies without downloading (BioProject mode only)"
    )

    args = parser.parse_args()

    if args.bioprojects:
        assemblies = get_bioproject_assemblies(args.bioprojects)

        if args.list_only:
            print("\nAssembly accessions (use with --assemblies to download):")
            for acc, name in assemblies:
                print(acc)
            return

        # Download assemblies
        assembly_accs = [acc for acc, name in assemblies]
        success = download_using_cli(assembly_accs, args.output)

    elif args.assemblies:
        success = download_using_cli(args.assemblies, args.output)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
