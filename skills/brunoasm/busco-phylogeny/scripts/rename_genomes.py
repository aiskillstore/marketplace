#!/usr/bin/env python3
"""
Rename genome files with clean, meaningful sample names for phylogenomics

This script helps create a mapping between genome files (often with cryptic
accession numbers) and clean species/sample names that will appear in the
final phylogenetic tree.

Usage:
    # Interactive mode - prompts for names
    python rename_genomes.py --interactive genome1.fasta genome2.fasta

    # From mapping file (TSV: old_name<TAB>new_name)
    python rename_genomes.py --mapping samples.tsv

    # Create template mapping file
    python rename_genomes.py --create-template *.fasta > samples.tsv

Author: Bruno de Medeiros (Field Museum)
Based on tutorials by Paul Frandsen (BYU)
"""

import argparse
import os
import sys
import shutil
from pathlib import Path


def sanitize_name(name):
    """
    Sanitize a name to be phylogenomics-safe
    - Replace spaces with underscores
    - Remove special characters
    - Keep only alphanumeric, underscore, hyphen
    """
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Remove special characters except underscore and hyphen
    name = ''.join(c for c in name if c.isalnum() or c in '_-')
    return name


def create_template(genome_files, output=sys.stdout):
    """Create a template mapping file"""
    output.write("# Sample mapping file\n")
    output.write("# Format: original_filename<TAB>new_sample_name\n")
    output.write("# Edit the second column with meaningful species/sample names\n")
    output.write("# Recommended format: [ACCESSION]_[NAME] (e.g., GCA000123456_Penstemon_eatonii)\n")
    output.write("# This keeps accession for traceability while having readable names in trees\n")
    output.write("# Names should contain only letters, numbers, underscores, and hyphens\n")
    output.write("#\n")

    for gfile in genome_files:
        basename = Path(gfile).stem  # Remove extension
        output.write(f"{gfile}\t{basename}\n")


def read_mapping(mapping_file):
    """Read mapping from TSV file"""
    mapping = {}
    with open(mapping_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            parts = line.split('\t')
            if len(parts) != 2:
                print(f"Warning: Skipping invalid line: {line}", file=sys.stderr)
                continue

            old_name, new_name = parts
            new_name = sanitize_name(new_name)
            mapping[old_name] = new_name

    return mapping


def interactive_rename(genome_files):
    """Interactively ask for new names"""
    mapping = {}

    print("Enter new sample names for each genome file.")
    print("Press Enter to keep the current name.")
    print("Names will be sanitized (spaces→underscores, special chars removed)\n")

    for gfile in genome_files:
        current_name = Path(gfile).stem
        new_name = input(f"{gfile} → [{current_name}]: ").strip()

        if not new_name:
            new_name = current_name

        new_name = sanitize_name(new_name)
        mapping[gfile] = new_name
        print(f"  Will rename to: {new_name}.fasta\n")

    return mapping


def rename_files(mapping, dry_run=False, backup=True):
    """Rename genome files according to mapping"""

    renamed = []
    errors = []

    for old_file, new_name in mapping.items():
        if not os.path.exists(old_file):
            errors.append(f"File not found: {old_file}")
            continue

        # Get extension from original file
        ext = Path(old_file).suffix
        if not ext:
            ext = '.fasta'

        new_file = f"{new_name}{ext}"

        # Check if target exists
        if os.path.exists(new_file) and new_file != old_file:
            errors.append(f"Target exists: {new_file}")
            continue

        # Skip if names are the same
        if old_file == new_file:
            print(f"Skip (no change): {old_file}")
            continue

        if dry_run:
            print(f"[DRY RUN] Would rename: {old_file} → {new_file}")
        else:
            # Backup if requested
            if backup:
                backup_file = f"{old_file}.backup"
                shutil.copy2(old_file, backup_file)
                print(f"Backup created: {backup_file}")

            # Rename
            shutil.move(old_file, new_file)
            print(f"Renamed: {old_file} → {new_file}")
            renamed.append((old_file, new_file))

    return renamed, errors


def main():
    parser = argparse.ArgumentParser(
        description="Rename genome files with meaningful sample names for phylogenomics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create template mapping file
  python rename_genomes.py --create-template *.fasta > samples.tsv
  # Edit samples.tsv, then apply mapping
  python rename_genomes.py --mapping samples.tsv

  # Interactive renaming
  python rename_genomes.py --interactive genome1.fasta genome2.fasta

  # Dry run (preview changes)
  python rename_genomes.py --mapping samples.tsv --dry-run
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--create-template',
        nargs='+',
        metavar='GENOME',
        help='Create a template mapping file from genome files'
    )
    group.add_argument(
        '--mapping',
        metavar='FILE',
        help='TSV file with mapping (old_name<TAB>new_name)'
    )
    group.add_argument(
        '--interactive',
        nargs='+',
        metavar='GENOME',
        help='Interactively rename genome files'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be renamed without actually renaming'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )

    args = parser.parse_args()

    # Create template
    if args.create_template:
        create_template(args.create_template)
        return

    # Interactive mode
    if args.interactive:
        mapping = interactive_rename(args.interactive)
    # Mapping file mode
    elif args.mapping:
        mapping = read_mapping(args.mapping)
    else:
        parser.error("No mode specified")

    if not mapping:
        print("No files to rename", file=sys.stderr)
        return

    # Perform renaming
    renamed, errors = rename_files(
        mapping,
        dry_run=args.dry_run,
        backup=not args.no_backup
    )

    # Summary
    print("\n" + "="*60)
    if args.dry_run:
        print("DRY RUN - No files were actually renamed")
    else:
        print(f"Successfully renamed {len(renamed)} file(s)")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
