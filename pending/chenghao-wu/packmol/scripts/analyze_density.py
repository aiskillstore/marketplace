#!/usr/bin/env python3
"""
Analyze density and composition of PDB files.

This script calculates the density, mass, and composition of molecular
systems from PDB files, useful for verifying Packmol output quality.

Usage:
    python analyze_density.py output.pdb

Example:
    python analyze_density.py system.pdb --target-density 1.0
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import math


# Atomic masses (IUPAC atomic weights)
ATOMIC_MASSES = {
    'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999,
    'P': 30.974, 'S': 32.06, 'Na': 22.990, 'K': 39.098,
    'CL': 35.45, 'CA': 40.078, 'MG': 24.305, 'FE': 55.845,
    'ZN': 65.38, 'CU': 63.546, 'MN': 54.938, 'CO': 58.933,
    'F': 18.998, 'BR': 79.904, 'I': 126.90, 'SE': 78.971,
}


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
        self.element = self._get_element(line)
        self.mass = ATOMIC_MASSES.get(self.element, 0.0)

    def _get_element(self, line: str) -> str:
        """Extract element symbol from atom name."""
        # Try columns 13-14 first (standard PDB)
        elem = line[12:14].strip().upper()
        if elem and elem[0].isalpha():
            # Check if two-letter element
            if len(elem) == 2 and elem[1].isalpha():
                return elem
            # Single letter element
            if len(elem) == 1:
                return elem

        # Fallback: parse from atom name
        name = self.name.upper()
        # Remove numbers
        name = ''.join(c for c in name if c.isalpha())

        # Try two-letter element
        if len(name) >= 2 and name[:2] in ATOMIC_MASSES:
            return name[:2]
        # Try single letter
        if name and name[0] in ATOMIC_MASSES:
            return name[0]

        return 'UNKNOWN'


class DensityAnalyzer:
    """Analyze density and composition of PDB files."""

    def __init__(self, pdb_file: str):
        """Initialize analyzer with PDB file."""
        self.pdb_file = Path(pdb_file)
        self.atoms = []
        self.box_size = None
        self.volume = None
        self.mass = None
        self.density = None

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
                        except (ValueError, IndexError):
                            print(f"Warning: Could not parse line: {line.strip()}")
            return True
        except Exception as e:
            print(f"Error reading file: {e}")
            return False

    def calculate_box_size(self) -> Tuple[float, float, float]:
        """Calculate box dimensions from atom coordinates."""
        if not self.atoms:
            return (0.0, 0.0, 0.0)

        x_coords = [atom.x for atom in self.atoms]
        y_coords = [atom.y for atom in self.atoms]
        z_coords = [atom.z for atom in self.atoms]

        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        z_min, z_max = min(z_coords), max(z_coords)

        x_size = x_max - x_min
        y_size = y_max - y_min
        z_size = z_max - z_min

        self.box_size = (x_size, y_size, z_size)
        return self.box_size

    def calculate_volume(self) -> float:
        """Calculate system volume."""
        if self.box_size is None:
            self.calculate_box_size()

        # Assume rectangular box
        x, y, z = self.box_size
        self.volume = x * y * z
        return self.volume

    def calculate_mass(self) -> float:
        """Calculate total system mass."""
        total_mass = sum(atom.mass for atom in self.atoms if atom.mass > 0)
        self.mass = total_mass
        return self.mass

    def calculate_density(self) -> float:
        """Calculate system density in g/cm³."""
        if self.volume is None:
            self.calculate_volume()
        if self.mass is None:
            self.calculate_mass()

        # Convert Å³ to cm³: 1 Å = 10^-8 cm, 1 Å³ = 10^-24 cm³
        volume_cm3 = self.volume * 1e-24

        if volume_cm3 > 0:
            # Density = mass / volume
            self.density = self.mass / volume_cm3
        else:
            self.density = 0.0

        return self.density

    def analyze_composition(self) -> Dict[str, int]:
        """Analyze system composition."""
        composition = {}

        # Count by element
        elements = {}
        for atom in self.atoms:
            elements[atom.element] = elements.get(atom.element, 0) + 1

        # Count by residue
        residues = {}
        for atom in self.atoms:
            key = f"{atom.res_name}:{atom.chain}"
            residues[key] = residues.get(key, 0) + 1

        composition['elements'] = elements
        composition['residues'] = residues
        composition['total_atoms'] = len(self.atoms)
        composition['unique_elements'] = len(elements)
        composition['unique_residues'] = len(residues)

        return composition

    def estimate_water_count(self) -> int:
        """Estimate number of water molecules."""
        water_count = 0
        for atom in self.atoms:
            if atom.res_name.strip() in ['HOH', 'WAT', 'TIP3']:
                # Count by residue sequence
                water_count = max(water_count, atom.res_seq)
        return water_count

    def print_report(self, target_density: float = None):
        """Print analysis report."""
        if not self.atoms:
            print("Error: No atoms found in PDB file")
            return

        print("="*60)
        print("DENSITY ANALYSIS REPORT")
        print("="*60)
        print(f"\nPDB file:     {self.pdb_file}")
        print(f"Total atoms:  {len(self.atoms)}")

        # Box dimensions
        box = self.calculate_box_size()
        print(f"\nBox dimensions:")
        print(f"  X: {box[0]:.2f} Å")
        print(f"  Y: {box[1]:.2f} Å")
        print(f"  Z: {box[2]:.2f} Å")

        # Volume
        volume = self.calculate_volume()
        print(f"\nVolume:       {volume:.2f} Å³ = {volume * 1e-24:.2e} cm³")

        # Mass
        mass = self.calculate_mass()
        print(f"\nTotal mass:   {mass:.2f} Da = {mass / 6.022e23:.2e} g")

        # Density
        density = self.calculate_density()
        print(f"\nDensity:      {density:.3f} g/cm³")

        if target_density:
            diff = density - target_density
            pct = (diff / target_density) * 100
            print(f"Target:       {target_density:.3f} g/cm³")
            print(f"Difference:  {diff:+.3f} g/cm³ ({pct:+.1f}%)")

            if abs(diff) < 0.1:
                print("✓ Density is close to target!")
            elif diff > 0:
                print("⚠ Density is higher than target (too many molecules)")
            else:
                print("⚠ Density is lower than target (too few molecules)")

        # Composition
        composition = self.analyze_composition()
        print(f"\n" + "-"*60)
        print("COMPOSITION")
        print("-"*60)

        print(f"\nUnique elements: {composition['unique_elements']}")
        print("Element distribution:")
        elements = composition['elements']
        sorted_elements = sorted(elements.items(), key=lambda x: x[1], reverse=True)
        for element, count in sorted_elements[:15]:
            mass = count * ATOMIC_MASSES.get(element, 0)
            pct = (mass / self.mass) * 100 if self.mass > 0 else 0
            print(f"  {element:3s}: {count:6d} atoms ({pct:5.1f}% mass)")

        # Water count
        water_count = self.estimate_water_count()
        if water_count > 0:
            print(f"\nEstimated water molecules: {water_count}")
            if volume > 0:
                vol_per_water = volume / water_count
                print(f"  Volume per water: {vol_per_water:.1f} Å³")
                print(f"  (Expected: ~30 Å³ at 1.0 g/cm³)")

        # Top residues
        if composition['unique_residues'] > 0:
            print(f"\nUnique residue types: {composition['unique_residues']}")
            residues = composition['residues']
            sorted_residues = sorted(residues.items(), key=lambda x: x[1], reverse=True)
            print("Top residue types:")
            for residue, count in sorted_residues[:10]:
                print(f"  {residue}: {count} atoms")

        print("="*60)

    def suggest_molecule_count(self, target_density: float = 1.0) -> int:
        """Suggest molecule count for target density."""
        if self.volume is None:
            self.calculate_volume()
        if self.mass is None:
            self.calculate_mass()

        # Current density
        current_density = self.density if self.density else self.calculate_density()

        if current_density == 0:
            return 0

        # Suggested scaling
        scaling_factor = target_density / current_density

        # Estimate based on atoms
        suggested_atoms = int(len(self.atoms) * scaling_factor)

        print(f"\nSuggestions for {target_density:.2f} g/cm³ density:")
        print(f"  Scale molecule count by: {scaling_factor:.2f}x")
        print(f"  Suggested total atoms: {suggested_atoms}")
        print(f"  Change: {suggested_atoms - len(self.atoms):+d} atoms")

        return suggested_atoms


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze density and composition of PDB files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze density
  python analyze_density.py system.pdb

  # Compare to target density
  python analyze_density.py system.pdb --target-density 1.0

  # Get suggestions for correct density
  python analyze_density.py system.pdb --target-density 1.0 --suggest

Typical densities:
  Water: 1.0 g/cm³
  Proteins in water: ~1.0-1.4 g/cm³ (depends on protein content)
  Pure organic liquids: 0.7-1.5 g/cm³ (depends on molecule)
        """
    )

    parser.add_argument('pdb_file', help='PDB file to analyze')
    parser.add_argument('--target-density', type=float, default=None,
                       help='Target density for comparison (g/cm³)')
    parser.add_argument('--suggest', action='store_true',
                       help='Suggest molecule count for target density')

    args = parser.parse_args()

    # Create analyzer
    analyzer = DensityAnalyzer(args.pdb_file)

    # Read PDB
    if not analyzer.read_pdb():
        sys.exit(1)

    # Print report
    analyzer.print_report(args.target_density)

    # Suggest if requested
    if args.suggest and args.target_density:
        analyzer.suggest_molecule_count(args.target_density)

    # Exit with appropriate code
    if args.target_density and analyzer.density:
        diff = abs(analyzer.density - args.target_density)
        if diff > 0.2:  # More than 20% difference
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
