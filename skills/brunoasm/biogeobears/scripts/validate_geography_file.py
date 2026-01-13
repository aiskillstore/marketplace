#!/usr/bin/env python3
"""
Validates and optionally reformats a BioGeoBEARS geography file.

Geography files must follow the PHYLIP-like format:
Line 1: n_species [TAB] n_areas [TAB] (area1 area2 area3 ...)
Lines 2+: species_name [TAB] binary_string (e.g., 011 for absent in area1, present in area2 and area3)

Common errors:
- Spaces instead of tabs
- Spaces in species names
- Spaces within binary strings
- Species names not matching tree tip labels
"""

import sys
import argparse
import re
from pathlib import Path


def validate_geography_file(filepath, tree_tips=None):
    """
    Validate geography file format.

    Args:
        filepath: Path to geography file
        tree_tips: Optional set of tree tip labels to validate against

    Returns:
        dict with validation results and any errors/warnings
    """
    errors = []
    warnings = []
    info = {}

    with open(filepath, 'r') as f:
        lines = [line.rstrip('\n\r') for line in f.readlines()]

    if not lines:
        errors.append("File is empty")
        return {'valid': False, 'errors': errors, 'warnings': warnings, 'info': info}

    # Parse header line
    header = lines[0]
    if '\t' not in header:
        errors.append("Line 1: Missing tab delimiter (should be: n_species [TAB] n_areas [TAB] (area_names))")
    else:
        parts = header.split('\t')
        if len(parts) < 3:
            errors.append("Line 1: Expected format 'n_species [TAB] n_areas [TAB] (area_names)'")
        else:
            try:
                n_species = int(parts[0])
                n_areas = int(parts[1])

                # Parse area names
                area_part = parts[2].strip()
                if not (area_part.startswith('(') and area_part.endswith(')')):
                    errors.append("Line 1: Area names should be in parentheses: (A B C)")
                else:
                    areas = area_part[1:-1].split()
                    if len(areas) != n_areas:
                        errors.append(f"Line 1: Declared {n_areas} areas but found {len(areas)} area names")

                    info['n_species'] = n_species
                    info['n_areas'] = n_areas
                    info['areas'] = areas

                    # Validate species lines
                    species_found = []
                    for i, line in enumerate(lines[1:], start=2):
                        if not line.strip():
                            continue

                        if '\t' not in line:
                            errors.append(f"Line {i}: Missing tab between species name and binary code")
                            continue

                        parts = line.split('\t')
                        if len(parts) != 2:
                            errors.append(f"Line {i}: Expected exactly one tab between species name and binary code")
                            continue

                        species_name = parts[0]
                        binary_code = parts[1]

                        # Check for spaces in species name
                        if ' ' in species_name:
                            errors.append(f"Line {i}: Species name '{species_name}' contains spaces (use underscores instead)")

                        # Check for spaces in binary code
                        if ' ' in binary_code or '\t' in binary_code:
                            errors.append(f"Line {i}: Binary code '{binary_code}' contains spaces or tabs (should be like '011' with no spaces)")

                        # Check binary code length
                        if len(binary_code) != n_areas:
                            errors.append(f"Line {i}: Binary code length ({len(binary_code)}) doesn't match number of areas ({n_areas})")

                        # Check binary code characters
                        if not all(c in '01' for c in binary_code):
                            errors.append(f"Line {i}: Binary code contains invalid characters (only 0 and 1 allowed)")

                        species_found.append(species_name)

                    # Check species count
                    if len(species_found) != n_species:
                        warnings.append(f"Header declares {n_species} species but found {len(species_found)} data lines")

                    info['species'] = species_found

                    # Check against tree tips if provided
                    if tree_tips:
                        species_set = set(species_found)
                        tree_set = set(tree_tips)

                        missing_in_tree = species_set - tree_set
                        missing_in_geog = tree_set - species_set

                        if missing_in_tree:
                            errors.append(f"Species in geography file but not in tree: {', '.join(sorted(missing_in_tree))}")
                        if missing_in_geog:
                            errors.append(f"Species in tree but not in geography file: {', '.join(sorted(missing_in_geog))}")

            except ValueError:
                errors.append("Line 1: First two fields must be integers (n_species and n_areas)")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'info': info
    }


def reformat_geography_file(input_path, output_path, delimiter=','):
    """
    Attempt to reformat a geography file from common formats.

    Args:
        input_path: Path to input file
        output_path: Path for output file
        delimiter: Delimiter used in input file (default: comma)
    """
    with open(input_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    # Detect if first line is a header
    header_line = lines[0]
    has_header = not header_line[0].isdigit()

    if has_header:
        # Parse area names from header
        parts = header_line.split(delimiter)
        species_col = parts[0]
        area_names = [p.strip() for p in parts[1:]]
        data_lines = lines[1:]
    else:
        # No header, infer from first data line
        parts = lines[0].split(delimiter)
        n_areas = len(parts) - 1
        area_names = [chr(65 + i) for i in range(n_areas)]  # A, B, C, ...
        data_lines = lines

    # Parse species data
    species_data = []
    for line in data_lines:
        if not line:
            continue
        parts = line.split(delimiter)
        if len(parts) < 2:
            continue

        species_name = parts[0].strip().replace(' ', '_')
        presence = ''.join(['1' if p.strip() in ['1', 'present', 'Present', 'TRUE', 'True'] else '0'
                           for p in parts[1:]])
        species_data.append((species_name, presence))

    # Write output
    with open(output_path, 'w') as f:
        # Header line
        n_species = len(species_data)
        n_areas = len(area_names)
        f.write(f"{n_species}\t{n_areas}\t({' '.join(area_names)})\n")

        # Species lines
        for species_name, binary_code in species_data:
            f.write(f"{species_name}\t{binary_code}\n")

    print(f"Reformatted {n_species} species across {n_areas} areas")
    print(f"Output written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate and reformat BioGeoBEARS geography files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a geography file
  python validate_geography_file.py input.txt --validate

  # Reformat from CSV to PHYLIP format
  python validate_geography_file.py input.csv --reformat -o output.data

  # Reformat with tab delimiter
  python validate_geography_file.py input.txt --reformat --delimiter tab -o output.data
        """
    )

    parser.add_argument('input', help='Input geography file')
    parser.add_argument('--validate', action='store_true',
                       help='Validate the file format')
    parser.add_argument('--reformat', action='store_true',
                       help='Reformat file to BioGeoBEARS format')
    parser.add_argument('-o', '--output',
                       help='Output file path (required for --reformat)')
    parser.add_argument('--delimiter', default=',',
                       help='Delimiter in input file (default: comma). Use "tab" for tab-delimited.')
    parser.add_argument('--tree',
                       help='Newick tree file to validate species names against')

    args = parser.parse_args()

    if args.delimiter.lower() == 'tab':
        args.delimiter = '\t'

    # Parse tree tips if provided
    tree_tips = None
    if args.tree:
        try:
            with open(args.tree, 'r') as f:
                tree_string = f.read().strip()
            # Extract tip labels using regex
            tree_tips = re.findall(r'([^(),:\s]+):', tree_string)
            if not tree_tips:
                tree_tips = re.findall(r'([^(),:\s]+)[,)]', tree_string)
            print(f"Found {len(tree_tips)} tips in tree file")
        except Exception as e:
            print(f"Warning: Could not parse tree file: {e}")

    if args.validate:
        result = validate_geography_file(args.input, tree_tips)

        print(f"\nValidation Results for: {args.input}")
        print("=" * 60)

        if result['info']:
            print(f"\nFile Info:")
            print(f"  Species: {result['info'].get('n_species', 'unknown')}")
            print(f"  Areas: {result['info'].get('n_areas', 'unknown')}")
            if 'areas' in result['info']:
                print(f"  Area names: {', '.join(result['info']['areas'])}")

        if result['warnings']:
            print(f"\nWarnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"  ⚠️  {warning}")

        if result['errors']:
            print(f"\nErrors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  ❌ {error}")
        else:
            print(f"\n✅ File is valid!")

        return 0 if result['valid'] else 1

    elif args.reformat:
        if not args.output:
            print("Error: --output required when using --reformat")
            return 1

        try:
            reformat_geography_file(args.input, args.output, args.delimiter)

            # Validate reformatted file
            result = validate_geography_file(args.output, tree_tips)
            if result['valid']:
                print("✅ Reformatted file is valid!")
            else:
                print("\n⚠️  Reformatted file has validation errors:")
                for error in result['errors']:
                    print(f"  ❌ {error}")
                return 1

        except Exception as e:
            print(f"Error during reformatting: {e}")
            return 1

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
