#!/usr/bin/env python3
"""
Automatic protein solvation setup for Packmol.

This script analyzes a protein structure and generates a Packmol input
file for solvating it with water and ions, calculating appropriate box
size, molecule counts, and ion numbers automatically.

Usage:
    python solvate_helper.py protein.pdb --shell 15.0 --charge +4

Example:
    python solvate_helper.py protein.pdb --shell 15.0 --charge +4 --conc 0.15 --run
"""

import sys
import argparse
import math
from pathlib import Path
from typing import Tuple, List, Optional


class ProteinAnalyzer:
    """Analyze protein structure for solvation."""

    def __init__(self, protein_file: str):
        """Initialize analyzer with protein PDB file."""
        self.protein_file = Path(protein_file)
        self.atoms = []
        self.dimensions = None
        self.center = None
        self.charge = None

    def read_protein(self) -> bool:
        """Read protein PDB file."""
        if not self.protein_file.exists():
            print(f"Error: Protein file not found: {self.protein_file}")
            return False

        try:
            with open(self.protein_file, 'r') as f:
                for line in f:
                    if line.startswith('ATOM') or line.startswith('HETATM'):
                        try:
                            x = float(line[30:38].strip())
                            y = float(line[38:46].strip())
                            z = float(line[46:54].strip())
                            self.atoms.append((x, y, z))
                        except (ValueError, IndexError):
                            continue
            return True
        except Exception as e:
            print(f"Error reading protein file: {e}")
            return False

    def calculate_dimensions(self) -> Tuple[float, float, float]:
        """Calculate protein dimensions (min/max in x, y, z)."""
        if not self.atoms:
            return (0.0, 0.0, 0.0)

        x_coords = [a[0] for a in self.atoms]
        y_coords = [a[1] for a in self.atoms]
        z_coords = [a[2] for a in self.atoms]

        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        z_min, z_max = min(z_coords), max(z_coords)

        x_size = x_max - x_min
        y_size = y_max - y_min
        z_size = z_max - z_min

        self.dimensions = (x_size, y_size, z_size)
        return self.dimensions

    def calculate_center(self) -> Tuple[float, float, float]:
        """Calculate protein center of mass."""
        if not self.atoms:
            return (0.0, 0.0, 0.0)

        x_coords = [a[0] for a in self.atoms]
        y_coords = [a[1] for a in self.atoms]
        z_coords = [a[2] for a in self.atoms]

        center_x = (max(x_coords) + min(x_coords)) / 2.0
        center_y = (max(y_coords) + min(y_coords)) / 2.0
        center_z = (max(z_coords) + min(z_coords)) / 2.0

        self.center = (center_x, center_y, center_z)
        return self.center

    def estimate_volume(self) -> float:
        """Estimate protein volume."""
        if not self.dimensions:
            self.calculate_dimensions()

        # Approximate as ellipsoid
        x, y, z = self.dimensions
        volume = (4.0/3.0) * math.pi * (x/2) * (y/2) * (z/2)
        return volume

    def calculate_box_size(self, shell_thickness: float) -> Tuple[float, float, float]:
        """Calculate solvation box size."""
        if not self.dimensions:
            self.calculate_dimensions()

        x, y, z = self.dimensions

        # Add shell on both sides
        box_x = x + 2 * shell_thickness
        box_y = y + 2 * shell_thickness
        box_z = z + 2 * shell_thickness

        # Round to nice numbers
        box_x = math.ceil(box_x)
        box_y = math.ceil(box_y)
        box_z = math.ceil(box_z)

        return (box_x, box_y, box_z)

    def estimate_water_count(self, box_size: Tuple[float, float, float],
                             target_density: float = 1.0) -> int:
        """Estimate number of water molecules needed."""
        box_volume = box_size[0] * box_size[1] * box_size[2]
        protein_volume = self.estimate_volume()

        water_volume = box_volume - protein_volume

        # At 1.0 g/cm³: 1 water molecule ≈ 30 Å³
        water_per_angstrom3 = target_density / 30.0
        n_water = int(water_volume * water_per_angstrom3)

        return n_water

    def calculate_ions(self, protein_charge: int, concentration: float,
                      box_size: Tuple[float, float, float]) -> Tuple[int, int]:
        """Calculate number of ions for neutrality and concentration."""
        # Box volume in liters
        box_volume_angstrom3 = box_size[0] * box_size[1] * box_size[2]
        box_volume_liters = box_volume_angstrom3 * 1e-30

        # Avogadro's number
        NA = 6.022e23

        # Ions for concentration (of each type)
        n_conc = concentration * box_volume_liters * NA
        n_conc = int(n_conc)

        # Ions for neutralization
        if protein_charge > 0:
            # Need negative ions to neutralize positive charge
            n_anions_extra = protein_charge
            n_cations_extra = 0
        elif protein_charge < 0:
            # Need positive ions to neutralize negative charge
            n_cations_extra = -protein_charge
            n_anions_extra = 0
        else:
            n_cations_extra = 0
            n_anions_extra = 0

        # Total ions
        n_cations = n_conc + n_cations_extra
        n_anions = n_conc + n_anions_extra

        return (n_cations, n_anions)


def generate_solvation_input(protein_file: str, output_file: str,
                             box_size: Tuple[float, float, float],
                             center: Tuple[float, float, float],
                             n_water: int, n_cations: int, n_anions: int,
                             tolerance: float = 2.0,
                             use_pbc: bool = True) -> str:
    """Generate Packmol solvation input file."""
    lines = []

    # Header
    lines.append("# Solvation input generated by solvate_helper.py")
    lines.append(f"# Protein: {protein_file}")
    lines.append(f"# Box size: {box_size[0]:.0f} × {box_size[1]:.0f} × {box_size[2]:.0f} Å")
    lines.append(f"# Water molecules: {n_water}")
    if n_cations > 0 or n_anions > 0:
        lines.append(f"# Ions: {n_cations} Na+, {n_anions} Cl-")
    lines.append("")

    # Required parameters
    lines.append(f"tolerance {tolerance}")
    lines.append("filetype pdb")
    lines.append(f"output {output_file}")
    lines.append("")

    # PBC
    if use_pbc:
        lines.append(f"pbc 0. 0. 0. {box_size[0]:.0f} {box_size[1]:.0f} {box_size[2]:.0f}")
        lines.append("")

    # Protein
    cx, cy, cz = center
    lines.append(f"structure {protein_file}")
    lines.append("  number 1")
    lines.append(f"  fixed {cx:.1f} {cy:.1f} {cz:.1f} 0. 0. 0.")
    lines.append("  center")
    lines.append("  chain A")
    lines.append("end structure")
    lines.append("")

    # Water
    lines.append("structure water.pdb")
    lines.append(f"  number {n_water}")
    lines.append(f"  inside box 0. 0. 0. {box_size[0]:.0f} {box_size[1]:.0f} {box_size[2]:.0f}")
    lines.append("  chain W")
    lines.append("end structure")
    lines.append("")

    # Cations
    if n_cations > 0:
        lines.append("structure SOD.pdb")
        lines.append(f"  number {n_cations}")
        lines.append(f"  inside box 0. 0. 0. {box_size[0]:.0f} {box_size[1]:.0f} {box_size[2]:.0f}")
        lines.append("  chain NA")
        lines.append("end structure")
        lines.append("")

    # Anions
    if n_anions > 0:
        lines.append("structure CLA.pdb")
        lines.append(f"  number {n_anions}")
        lines.append(f"  inside box 0. 0. 0. {box_size[0]:.0f} {box_size[1]:.0f} {box_size[2]:.0f}")
        lines.append("  chain CL")
        lines.append("end structure")
        lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Automatic protein solvation setup for Packmol',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic solvation with 15 Å solvent shell
  python solvate_helper.py protein.pdb --shell 15.0

  # With charged protein and salt
  python solvate_helper.py protein.pdb --shell 15.0 --charge +4 --conc 0.15

  # Generate input and run Packmol
  python solvate_helper.py protein.pdb --shell 15.0 --run

  # Custom output names
  python solvate_helper.py protein.pdb --shell 15.0 \\
      --output solvated.pdb --input solvation.inp

Typical values:
  --shell: 10-20 Å (15 Å recommended)
  --conc: 0.15 M (physiological salt concentration)
  --charge: Protein charge (determine with pdb2gmx or similar)

Required structure files:
  - protein.pdb: Your protein structure
  - water.pdb: Single water molecule (TIP3P recommended)
  - SOD.pdb: Sodium ion (if adding ions)
  - CLA.pdb: Chloride ion (if adding ions)
        """
    )

    parser.add_argument('protein', help='Protein PDB file')
    parser.add_argument('--shell', type=float, default=15.0,
                       help='Solvent shell thickness (Å) [default: 15.0]')
    parser.add_argument('--charge', type=int, default=0,
                       help='Protein charge for neutralization [default: 0]')
    parser.add_argument('--conc', type=float, default=0.15,
                       help='Salt concentration (M) [default: 0.15]')
    parser.add_argument('--density', type=float, default=1.0,
                       help='Target water density (g/cm³) [default: 1.0]')
    parser.add_argument('--tolerance', type=float, default=2.0,
                       help='Packmol tolerance (Å) [default: 2.0]')
    parser.add_argument('--output', default='solvated.pdb',
                       help='Output PDB filename [default: solvated.pdb]')
    parser.add_argument('--input', default='solvation.inp',
                       help='Packmol input filename [default: solvation.inp]')
    parser.add_argument('--no-pbc', action='store_true',
                       help='Disable periodic boundary conditions')
    parser.add_argument('--run', action='store_true',
                       help='Run Packmol after generating input')

    args = parser.parse_args()

    print("="*60)
    print("Packmol Solvation Helper")
    print("="*60)
    print(f"\nProtein file:     {args.protein}")
    print(f"Solvent shell:    {args.shell} Å")
    print(f"Protein charge:   {args.charge:+d}")
    print(f"Salt conc:        {args.conc} M")
    print(f"Target density:   {args.density} g/cm³")

    # Analyze protein
    print("\nAnalyzing protein structure...")
    analyzer = ProteinAnalyzer(args.protein)

    if not analyzer.read_protein():
        sys.exit(1)

    dimensions = analyzer.calculate_dimensions()
    center = analyzer.calculate_center()

    print(f"\nProtein dimensions:")
    print(f"  X: {dimensions[0]:.1f} Å")
    print(f"  Y: {dimensions[1]:.1f} Å")
    print(f"  Z: {dimensions[2]:.1f} Å")

    print(f"\nProtein center:")
    print(f"  ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})")

    # Calculate box size
    box_size = analyzer.calculate_box_size(args.shell)
    print(f"\nBox size (with {args.shell} Å shell):")
    print(f"  {box_size[0]:.0f} × {box_size[1]:.0f} × {box_size[2]:.0f} Å")

    # Estimate water count
    n_water = analyzer.estimate_water_count(box_size, args.density)
    print(f"\nEstimated water molecules: {n_water}")

    # Calculate ions
    n_cations, n_anions = analyzer.calculate_ions(
        args.charge, args.conc, box_size
    )

    if args.charge != 0:
        print(f"\nIon calculations for charge neutralization:")
        print(f"  Protein charge: {args.charge:+d}")
        if args.charge > 0:
            print(f"  Adding {args.charge} extra anions for neutralization")
        else:
            print(f"  Adding {-args.charge} extra cations for neutralization")

    if args.conc > 0:
        print(f"\nIon calculations for {args.conc} M salt:")
        print(f"  Na+: {n_cations}")
        print(f"  Cl-: {n_anions}")

    # Total atoms estimate
    total_water_atoms = n_water * 3
    total_atoms = total_water_atoms + len(analyzer.atoms) + n_cations + n_anions
    print(f"\nEstimated total atoms: ~{total_atoms:,}")

    # Generate input file
    print(f"\nGenerating Packmol input file: {args.input}")
    input_content = generate_solvation_input(
        args.protein,
        args.output,
        box_size,
        center,
        n_water,
        n_cations,
        n_anions,
        args.tolerance,
        use_pbc=not args.no_pbc
    )

    with open(args.input, 'w') as f:
        f.write(input_content)

    print(f"✓ Input file written: {args.input}")
    print(f"  Output will be: {args.output}")

    # Run Packmol if requested
    if args.run:
        print("\nRunning Packmol...")
        print("-"*60)

        import subprocess
        try:
            result = subprocess.run(
                ['packmol'],
                stdin=open(args.input, 'r'),
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            # Print output
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            if result.returncode == 0:
                print("-"*60)
                print(f"✓ Packmol completed successfully!")
                print(f"✓ Output file: {args.output}")

                # Check if output exists
                if Path(args.output).exists():
                    size = Path(args.output).stat().st_size
                    print(f"  File size: {size:,} bytes")
                else:
                    print("⚠ Warning: Output file not found")
            else:
                print("-"*60)
                print("❌ Packmol failed with return code:", result.returncode)

        except subprocess.TimeoutExpired:
            print("❌ Packmol timed out after 1 hour")
        except FileNotFoundError:
            print("❌ Packmol not found. Install with: pip install packmol")
        except Exception as e:
            print(f"❌ Error running Packmol: {e}")

    print("\n" + "="*60)
    print("Next steps:")
    print("="*60)
    print("1. Verify output:")
    print(f"   python scripts/verify_success.py {args.input} {args.output}")
    print("\n2. Check for overlaps:")
    print(f"   python scripts/check_overlaps.py {args.output} --tolerance {args.tolerance}")
    print("\n3. Analyze density:")
    print(f"   python scripts/analyze_density.py {args.output} --target-density {args.density}")
    print("\n4. If everything looks good, proceed with MD simulation!")
    print("="*60)

    sys.exit(0)


if __name__ == "__main__":
    main()
