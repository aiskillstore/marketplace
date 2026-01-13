#!/usr/bin/env python3
"""
Check for atomic overlaps in Packmol output PDB files.

This script reads a PDB file and checks for atoms that are closer than
the specified tolerance, indicating potential overlaps that should be
resolved before using the structure in MD simulations.

Usage:
    python check_overlaps.py output.pdb --tolerance 2.0

Example:
    python check_overlaps.py system.pdb --tolerance 2.0
"""

import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
import math


class Atom:
    """Represent an atom from a PDB file."""

    def __init__(self, line: str):
        """Parse atom from PDB line."""
        self.serial = int(line[6:11].strip())
        self.name = line[12:16].strip()
        self.alt_loc = line[16:17].strip()
        self.res_name = line[17:20].strip()
        self.chain = line[21:22].strip()
        self.res_seq = int(line[22:26].strip())
        self.x = float(line[30:38].strip())
        self.y = float(line[38:46].strip())
        self.z = float(line[46:54].strip())
        self.element = line[12:14].strip().replace(' ', '')
        self.line = line

    def __repr__(self):
        """String representation."""
        return f"{self.element}{self.serial}/{self.res_name}{self.res_seq}"


class OverlapChecker:
    """Check for atomic overlaps in PDB files."""

    def __init__(self, pdb_file: str, tolerance: float):
        """Initialize checker with PDB file and tolerance."""
        self.pdb_file = Path(pdb_file)
        self.tolerance = tolerance
        self.atoms = []
        self.overlaps = []

    def read_pdb(self) -> bool:
        """Read PDB file and extract atoms."""
        if not self.pdb_file.exists():
            print(f"Error: File not found: {self.pdb_file}")
            return False

        try:
            with open(self.pdb_file, 'r') as f:
                for line in f:
                    if line.startswith('ATOM') or line.startswith('HETATM'):
                        try:
                            atom = Atom(line)
                            self.atoms.append(atom)
                        except (ValueError, IndexError) as e:
                            print(f"Warning: Could not parse line: {line.strip()}")
            return True
        except Exception as e:
            print(f"Error reading file: {e}")
            return False

    def calculate_distance(self, atom1: Atom, atom2: Atom) -> float:
        """Calculate distance between two atoms."""
        dx = atom1.x - atom2.x
        dy = atom1.y - atom2.y
        dz = atom1.z - atom2.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def check_overlaps(self):
        """Check for overlapping atoms."""
        n_atoms = len(self.atoms)
        print(f"Checking {n_atoms} atoms for overlaps < {self.tolerance} Å...\n")

        # Check all pairs
        for i in range(n_atoms):
            atom1 = self.atoms[i]

            # Skip same residue (intramolecular)
            for j in range(i + 1, n_atoms):
                atom2 = self.atoms[j]

                # Skip if same molecule/residue
                if atom1.res_seq == atom2.res_seq and atom1.chain == atom2.chain:
                    continue

                # Calculate distance
                dist = self.calculate_distance(atom1, atom2)

                # Check for overlap
                if dist < self.tolerance:
                    self.overlaps.append({
                        'atom1': atom1,
                        'atom2': atom2,
                        'distance': dist,
                        'violation': self.tolerance - dist
                    })

    def report_overlaps(self, max_display: int = 20):
        """Generate overlap report."""
        if not self.overlaps:
            print("✓ No overlaps found!")
            print(f"  All atom pairs are >= {self.tolerance} Å apart.")
            return

        # Sort by violation magnitude
        self.overlaps.sort(key=lambda x: x['violation'], reverse=True)

        print(f"❌ Found {len(self.overlaps)} overlapping atom pairs!\n")

        # Display worst violations
        display_count = min(max_display, len(self.overlaps))
        print(f"Top {display_count} worst violations:\n")

        for i, overlap in enumerate(self.overlaps[:display_count], 1):
            atom1 = overlap['atom1']
            atom2 = overlap['atom2']
            dist = overlap['distance']
            violation = overlap['violation']

            print(f"{i}. {atom1} - {atom2}")
            print(f"   Distance: {dist:.3f} Å (violation: {violation:.3f} Å)")

        if len(self.overlaps) > max_display:
            print(f"\n... and {len(self.overlaps) - max_display} more overlaps")

        # Statistics
        print("\n" + "="*60)
        print("Statistics:")
        print("="*60)
        violations = [o['violation'] for o in self.overlaps]
        print(f"  Mean violation:    {sum(violations)/len(violations):.3f} Å")
        print(f"  Max violation:     {max(violations):.3f} Å")
        print(f"  Min violation:     {min(violations):.3f} Å")
        print(f"  Total overlaps:    {len(self.overlaps)}")

        # Distribution
        small = sum(1 for v in violations if v < 0.1)
        medium = sum(1 for v in violations if 0.1 <= v < 0.5)
        large = sum(1 for v in violations if v >= 0.5)

        print("\nViolation distribution:")
        print(f"  < 0.1 Å:   {small:4d} (minor)")
        print(f"  0.1-0.5 Å: {medium:4d} (moderate)")
        print(f"  > 0.5 Å:   {large:4d} (severe)")

    def get_atom_statistics(self):
        """Print atom statistics."""
        if not self.atoms:
            return

        # Count by element
        elements = {}
        for atom in self.atoms:
            elements[atom.element] = elements.get(atom.element, 0) + 1

        print("\nAtom statistics:")
        print("-" * 40)
        print(f"  Total atoms:  {len(self.atoms)}")
        print(f"  Unique elements: {len(elements)}")

        # Top elements
        sorted_elements = sorted(elements.items(), key=lambda x: x[1], reverse=True)
        for element, count in sorted_elements[:10]:
            print(f"    {element:2s}: {count:6d}")

    def check_system_quality(self) -> bool:
        """Check if system quality is acceptable."""
        if not self.overlaps:
            return True

        # Check for severe violations
        severe = sum(1 for o in self.overlaps if o['violation'] > 0.5)
        moderate = sum(1 for o in self.overlaps if 0.1 < o['violation'] <= 0.5)

        if severe > 0:
            print("\n" + "!"*60)
            print("WARNING: Severe overlaps detected!")
            print("The system should not be used for MD simulation without fixing.")
            print("!"*60)
            return False
        elif moderate > 10:
            print("\n" + "!"*60)
            print("CAUTION: Multiple moderate overlaps detected.")
            print("Consider energy minimization before MD simulation.")
            print("!"*60)
            return False
        else:
            print("\n" + "*"*60)
            print("Minor overlaps detected.")
            print("These may be resolved during MD equilibration.")
            print("*"*60)
            return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Check for atomic overlaps in PDB files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check with default tolerance of 2.0 Å
  python check_overlaps.py system.pdb

  # Check with custom tolerance
  python check_overlaps.py system.pdb --tolerance 1.5

  # Show detailed report
  python check_overlaps.py system.pdb --tolerance 2.0 --max-display 50
        """
    )

    parser.add_argument('pdb_file', help='PDB file to check')
    parser.add_argument('--tolerance', type=float, default=2.0,
                       help='Minimum allowed distance between atoms (Å) [default: 2.0]')
    parser.add_argument('--max-display', type=int, default=20,
                       help='Maximum number of overlaps to display [default: 20]')

    args = parser.parse_args()

    print("="*60)
    print("Packmol Overlap Checker")
    print("="*60)
    print(f"PDB file:     {args.pdb_file}")
    print(f"Tolerance:    {args.tolerance} Å")
    print("="*60)
    print()

    # Create checker
    checker = OverlapChecker(args.pdb_file, args.tolerance)

    # Read PDB
    if not checker.read_pdb():
        sys.exit(1)

    # Get statistics
    checker.get_atom_statistics()

    print()

    # Check overlaps
    checker.check_overlaps()

    # Report
    checker.report_overlaps(args.max_display)

    # Check quality
    print()
    quality_ok = checker.check_system_quality()

    print()
    if quality_ok:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
