#!/usr/bin/env python3
"""
Generate Packmol input files programmatically.

This script provides a Python API for creating Packmol input files,
making it easier to generate complex systems programmatically.

Usage (CLI):
    python generate_input.py --output system.inp

Usage (Python):
    from generate_input import PackmolInput
    inp = PackmolInput()
    inp.add_tolerance(2.0)
    inp.add_structure('water.pdb', 1000, 'inside box 0. 0. 0. 40. 40. 40.')
    inp.write('system.inp')
"""

import sys
import argparse
from typing import List, Dict, Optional


class PackmolInput:
    """Generate Packmol input files programmatically."""

    def __init__(self):
        """Initialize Packmol input generator."""
        self.tolerance = None
        self.output = None
        self.filetype = 'pdb'
        self.pbc = None
        self.seed = None
        self.discale = None
        self.maxit = None
        self.precision = None
        self.structures = []
        self.comments = []

    def add_tolerance(self, value: float):
        """Set tolerance parameter."""
        if value <= 0:
            raise ValueError("Tolerance must be positive")
        self.tolerance = value
        return self

    def add_output(self, filename: str):
        """Set output filename."""
        self.output = filename
        return self

    def add_filetype(self, fmt: str):
        """Set file type (pdb, xyz, or tinker)."""
        fmt = fmt.lower()
        if fmt not in ['pdb', 'xyz', 'tinker']:
            raise ValueError(f"Invalid filetype: {fmt}. Must be pdb, xyz, or tinker")
        self.filetype = fmt
        return self

    def add_pbc(self, *dimensions):
        """Set periodic boundary conditions."""
        if len(dimensions) not in [3, 6]:
            raise ValueError("PBC requires 3 (orthorhombic) or 6 (box) parameters")
        try:
            self.pbc = [float(d) for d in dimensions]
        except ValueError:
            raise ValueError("PBC parameters must be numeric")
        return self

    def add_seed(self, seed: int):
        """Set random seed."""
        self.seed = int(seed)
        return self

    def add_discale(self, value: float):
        """Set distance scaling factor."""
        if value <= 0:
            raise ValueError("Discale must be positive")
        self.discale = float(value)
        return self

    def add_maxit(self, value: int):
        """Set maximum iterations."""
        if value <= 0:
            raise ValueError("Maxit must be positive")
        self.maxit = int(value)
        return self

    def add_precision(self, value: float):
        """Set convergence precision."""
        if value <= 0:
            raise ValueError("Precision must be positive")
        self.precision = float(value)
        return self

    def add_comment(self, comment: str):
        """Add a comment line."""
        self.comments.append(comment)
        return self

    def add_structure(self, filename: str, number: int, constraint: str, **kwargs):
        """
        Add a structure definition.

        Args:
            filename: Path to structure file
            number: Number of molecules
            constraint: Constraint string (e.g., 'inside box 0. 0. 0. 40. 40. 40.')
            **kwargs: Additional parameters (chain, radius, resnumbers, etc.)

        Returns:
            self for method chaining
        """
        if number <= 0:
            raise ValueError("Number of molecules must be positive")

        structure = {
            'filename': filename,
            'number': number,
            'constraint': constraint,
            'chain': kwargs.get('chain'),
            'radius': kwargs.get('radius'),
            'resnumbers': kwargs.get('resnumbers'),
            'fixed': kwargs.get('fixed'),
            'center': kwargs.get('center', False),
            'constrain_rotation': kwargs.get('constrain_rotation'),
            'movefrac': kwargs.get('movefrac'),
            'maxmove': kwargs.get('maxmove'),
            'disable_movebad': kwargs.get('disable_movebad', False),
            'check': kwargs.get('check', False),
            'atoms': kwargs.get('atoms'),
        }

        self.structures.append(structure)
        return self

    def validate(self) -> List[str]:
        """
        Validate input parameters.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Check required parameters
        if self.tolerance is None:
            errors.append("Missing required parameter: tolerance")
        if self.output is None:
            errors.append("Missing required parameter: output")
        if not self.structures:
            errors.append("No structures defined")

        # Validate structures
        for i, struct in enumerate(self.structures, 1):
            if not struct['filename']:
                errors.append(f"Structure {i}: Missing filename")
            if struct['number'] <= 0:
                errors.append(f"Structure {i}: Invalid number")

        return errors

    def generate(self) -> str:
        """
        Generate Packmol input file content.

        Returns:
            Input file content as string
        """
        # Validate first
        errors = self.validate()
        if errors:
            raise ValueError("Invalid input:\n" + "\n".join(errors))

        lines = []

        # Add comments
        if self.comments:
            for comment in self.comments:
                lines.append(f"# {comment}")
            lines.append("")

        # Required parameters
        lines.append(f"tolerance {self.tolerance}")
        lines.append(f"filetype {self.filetype}")
        lines.append(f"output {self.output}")
        lines.append("")

        # Optional parameters
        if self.pbc:
            pbc_str = " ".join(str(v) for v in self.pbc)
            lines.append(f"pbc {pbc_str}")

        if self.seed is not None:
            lines.append(f"seed {self.seed}")

        if self.discale:
            lines.append(f"discale {self.discale}")

        if self.maxit:
            lines.append(f"maxit {self.maxit}")

        if self.precision:
            lines.append(f"precision {self.precision}")

        if self.pbc or self.seed or self.discale or self.maxit or self.precision:
            lines.append("")

        # Structure definitions
        for struct in self.structures:
            lines.append(f"structure {struct['filename']}")
            lines.append(f"  number {struct['number']}")

            # Constraint
            lines.append(f"  {struct['constraint']}")

            # Optional parameters
            if struct['fixed']:
                fixed = struct['fixed']
                if isinstance(fixed, (list, tuple)):
                    fixed_str = " ".join(str(v) for v in fixed)
                    lines.append(f"  fixed {fixed_str}")
                else:
                    lines.append(f"  fixed {fixed}")

            if struct['center']:
                lines.append(f"  center")

            if struct['chain']:
                lines.append(f"  chain {struct['chain']}")

            if struct['radius']:
                lines.append(f"  radius {struct['radius']}")

            if struct['resnumbers']:
                lines.append(f"  resnumbers {struct['resnumbers']}")

            if struct['constrain_rotation']:
                rot = struct['constrain_rotation']
                if isinstance(rot, (list, tuple)) and len(rot) == 3:
                    lines.append(f"  constrain_rotation {rot[0]} {rot[1]} {rot[2]}")

            if struct['movefrac']:
                lines.append(f"  movefrac {struct['movefrac']}")

            if struct['maxmove']:
                lines.append(f"  maxmove {struct['maxmove']}")

            if struct['disable_movebad']:
                lines.append(f"  disable_movebad")

            if struct['check']:
                lines.append(f"  check")

            # Atom selection
            if struct['atoms']:
                atoms = struct['atoms']
                if isinstance(atoms, (list, tuple)):
                    atom_str = " ".join(str(a) for a in atoms)
                    lines.append(f"  atoms {atom_str}")
                    # Check if there are constraints for these atoms
                    # (This is simplified; full implementation would be more complex)

            lines.append("end structure")
            lines.append("")

        return "\n".join(lines)

    def write(self, filename: str):
        """
        Write input file to disk.

        Args:
            filename: Output filename
        """
        content = self.generate()
        with open(filename, 'w') as f:
            f.write(content)
        return self

    def __str__(self):
        """String representation."""
        return self.generate()


# Convenience functions for common systems

def create_simple_box(molecule_file: str, n_molecules: int,
                     box_size: tuple, tolerance: float = 2.0,
                     output_file: str = "system.pdb") -> PackmolInput:
    """Create a simple box system."""
    xmin, ymin, zmin = 0, 0, 0
    xmax, ymax, zmax = box_size

    inp = PackmolInput()
    inp.add_tolerance(tolerance)
    inp.add_output(output_file)
    inp.add_structure(
        molecule_file,
        n_molecules,
        f"inside box {xmin:.1f} {ymin:.1f} {zmin:.1f} {xmax:.1f} {ymax:.1f} {zmax:.1f}"
    )
    return inp


def create_mixture(molecules: list, box_size: tuple,
                   tolerance: float = 2.0,
                   output_file: str = "mixture.pdb") -> PackmolInput:
    """
    Create a mixture of multiple molecule types.

    Args:
        molecules: List of (filename, count) tuples
        box_size: (xmax, ymax, zmax) tuple
        tolerance: Tolerance value
        output_file: Output filename
    """
    xmax, ymax, zmax = box_size

    inp = PackmolInput()
    inp.add_tolerance(tolerance)
    inp.add_output(output_file)

    for mol_file, n_mol in molecules:
        inp.add_structure(
            mol_file,
            n_mol,
            f"inside box 0. 0. 0. {xmax:.1f} {ymax:.1f} {zmax:.1f}"
        )

    return inp


def create_solvation(protein_file: str, box_size: tuple,
                     n_water: int, n_cations: int = 0, n_anions: int = 0,
                     tolerance: float = 2.0,
                     output_file: str = "solvated.pdb") -> PackmolInput:
    """
    Create a solvated protein system.

    Args:
        protein_file: Path to protein PDB file
        box_size: (xmax, ymax, zmax) tuple
        n_water: Number of water molecules
        n_cations: Number of cations (e.g., Na+)
        n_anions: Number of anions (e.g., Cl-)
        tolerance: Tolerance value
        output_file: Output filename
    """
    xmax, ymax, zmax = box_size
    center_x, center_y, center_z = xmax/2, ymax/2, zmax/2

    inp = PackmolInput()
    inp.add_tolerance(tolerance)
    inp.add_output(output_file)
    inp.add_pbc(0., 0., 0., xmax, ymax, zmax)

    # Fixed protein at center
    inp.add_structure(
        protein_file,
        1,
        f"fixed {center_x:.1f} {center_y:.1f} {center_z:.1f} 0. 0. 0.",
        center=True,
        chain='A'
    )

    # Water
    inp.add_structure(
        'water.pdb',
        n_water,
        f"inside box 0. 0. 0. {xmax:.1f} {ymax:.1f} {zmax:.1f}",
        chain='W'
    )

    # Cations (if specified)
    if n_cations > 0:
        inp.add_structure(
            'SOD.pdb',
            n_cations,
            f"inside box 0. 0. 0. {xmax:.1f} {ymax:.1f} {zmax:.1f}",
            chain='NA'
        )

    # Anions (if specified)
    if n_anions > 0:
        inp.add_structure(
            'CLA.pdb',
            n_anions,
            f"inside box 0. 0. 0. {xmax:.1f} {ymax:.1f} {zmax:.1f}",
            chain='CL'
        )

    return inp


def create_interface(phase1_file: str, n_phase1: int,
                     phase2_file: str, n_phase2: int,
                     box_size: tuple, interface_z: float = 0.0,
                     tolerance: float = 2.0,
                     output_file: str = "interface.pdb") -> PackmolInput:
    """
    Create a liquid-liquid interface system.

    Args:
        phase1_file: Molecule file for phase 1 (below interface)
        n_phase1: Number of molecules in phase 1
        phase2_file: Molecule file for phase 2 (above interface)
        n_phase2: Number of molecules in phase 2
        box_size: (xmax, ymax, zmax) tuple
        interface_z: Z-coordinate of interface
        tolerance: Tolerance value
        output_file: Output filename
    """
    xmax, ymax, zmax = box_size

    inp = PackmolInput()
    inp.add_tolerance(tolerance)
    inp.add_output(output_file)
    inp.add_pbc(0., 0., 0., xmax, ymax, zmax)

    # Phase 1 (below interface)
    inp.add_structure(
        phase1_file,
        n_phase1,
        f"below plane 0. 0. 1. {interface_z:.1f}",
        chain='P1'
    )

    # Phase 2 (above interface)
    inp.add_structure(
        phase2_file,
        n_phase2,
        f"above plane 0. 0. 1. {interface_z:.1f}",
        chain='P2'
    )

    return inp


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Generate Packmol input files programmatically',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple water box
  python generate_input.py --molecule water.pdb --number 1000 \\
      --box 40 40 40 --output water_box.inp

  # Mixture
  python generate_input.py --molecule water.pdb --number 800 \\
      --molecule ethanol.pdb --number 200 --box 40 40 40 \\
      --output mixture.inp

  # Solvated protein
  python generate_input.py --protein protein.pdb --water 5000 \\
      --box 60 60 80 --cations 10 --anions 10 --output solvated.inp

  # Interface
  python generate_input.py --interface \\
      --phase1 water.pdb 1000 --phase2 chloroform.pdb 200 \\
      --box 40 40 60 --output interface.inp
        """
    )

    # General options
    parser.add_argument('--output', required=True, help='Output input file name')
    parser.add_argument('--tolerance', type=float, default=2.0,
                       help='Tolerance value [default: 2.0]')

    # Simple box mode
    parser.add_argument('--molecule', help='Molecule file (for simple box)')
    parser.add_argument('--number', type=int, help='Number of molecules')
    parser.add_argument('--box', nargs=3, type=float, metavar=('X', 'Y', 'Z'),
                       help='Box size (Å)')

    # Solvation mode
    parser.add_argument('--protein', help='Protein file (for solvation)')
    parser.add_argument('--water', type=int, help='Number of water molecules')
    parser.add_argument('--cations', type=int, default=0, help='Number of cations')
    parser.add_argument('--anions', type=int, default=0, help='Number of anions')

    # Interface mode
    parser.add_argument('--interface', action='store_true',
                       help='Create interface system')
    parser.add_argument('--phase1', nargs=2, metavar=('FILE', 'N'),
                       help='Phase 1: file and count')
    parser.add_argument('--phase2', nargs=2, metavar=('FILE', 'N'),
                       help='Phase 2: file and count')

    args = parser.parse_args()

    inp = None

    # Determine mode
    if args.interface:
        # Interface mode
        if not args.phase1 or not args.phase2 or not args.box:
            print("Error: Interface mode requires --phase1, --phase2, and --box")
            sys.exit(1)

        phase1_file, n1 = args.phase1
        phase2_file, n2 = args.phase2
        n1, n2 = int(n1), int(n2)

        inp = create_interface(
            phase1_file, n1,
            phase2_file, n2,
            tuple(args.box),
            tolerance=args.tolerance,
            output_file=args.output.replace('.inp', '.pdb')
        )

    elif args.protein:
        # Solvation mode
        if not args.box or not args.water:
            print("Error: Solvation mode requires --box and --water")
            sys.exit(1)

        inp = create_solvation(
            args.protein,
            tuple(args.box),
            args.water,
            args.cations,
            args.anions,
            tolerance=args.tolerance,
            output_file=args.output.replace('.inp', '.pdb')
        )

    elif args.molecule and args.number and args.box:
        # Simple box mode
        inp = create_simple_box(
            args.molecule,
            args.number,
            tuple(args.box),
            tolerance=args.tolerance,
            output_file=args.output.replace('.inp', '.pdb')
        )
    else:
        print("Error: Must specify --molecule/--number/--box, --protein, or --interface")
        parser.print_help()
        sys.exit(1)

    # Write input file
    inp.write(args.output)
    print(f"Generated Packmol input file: {args.output}")
    print(f"Output will be written to: {args.output.replace('.inp', '.pdb')}")


if __name__ == "__main__":
    main()
