#!/usr/bin/env python3
"""
Convert FASconCAT info file to IQ-TREE partition format

Usage:
    python convert_fasconcat_to_partition.py FcC_info.xls [output_file.txt]

Author: Bruno de Medeiros (Field Museum)
Based on tutorials by Paul Frandsen (BYU)
"""

import sys


def convert_fcc_to_partition(fcc_file, output_file="partition_def.txt"):
    """
    Convert FASconCAT info file to IQ-TREE partition format

    Args:
        fcc_file: Path to FcC_info.xls file from FASconCAT
        output_file: Path to output partition definition file
    """

    try:
        with open(fcc_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{fcc_file}' not found")
        sys.exit(1)

    partitions_written = 0

    with open(output_file, 'w') as out:
        # Skip first two header lines (FASconCAT INFO and column headers)
        for line in lines[2:]:
            line = line.strip()
            if line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    locus = parts[0]
                    start = parts[1]
                    end = parts[2]
                    out.write(f"AA, {locus} = {start}-{end}\n")
                    partitions_written += 1

    print(f"Partition file created: {output_file}")
    print(f"Number of partitions: {partitions_written}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_fasconcat_to_partition.py FcC_info.xls [output_file.txt]")
        print("\nConverts FASconCAT info file to IQ-TREE partition format")
        sys.exit(1)

    fcc_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "partition_def.txt"

    convert_fcc_to_partition(fcc_file, output_file)


if __name__ == "__main__":
    main()
