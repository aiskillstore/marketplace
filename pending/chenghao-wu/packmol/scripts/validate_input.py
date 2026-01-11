#!/usr/bin/env python3
"""
Validate Packmol input file syntax.

This script checks Packmol input files for common errors before running Packmol,
saving time by catching syntax issues early.

Usage:
    python validate_input.py input.inp

Example:
    python validate_input.py solvation.inp
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict


class PackmolValidator:
    """Validate Packmol input file syntax."""

    def __init__(self, filename: str):
        """Initialize validator with input file."""
        self.filename = Path(filename)
        self.errors = []
        self.warnings = []
        self.content = None
        self.lines = []

    def read_file(self) -> bool:
        """Read the input file."""
        if not self.filename.exists():
            self.errors.append(f"File not found: {self.filename}")
            return False

        try:
            with open(self.filename, 'r') as f:
                self.content = f.read()
                self.lines = self.content.splitlines()
            return True
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False

    def validate(self) -> Tuple[List[str], List[str]]:
        """
        Validate the input file.

        Returns:
            (errors, warnings): Lists of error and warning messages
        """
        if not self.read_file():
            return self.errors, self.warnings

        # Check for empty file
        if not self.content.strip():
            self.errors.append("File is empty")
            return self.errors, self.warnings

        # Parse the file
        self._parse_and_validate()

        return self.errors, self.warnings

    def _parse_and_validate(self):
        """Parse and validate the input file."""
        # Check required parameters
        self._check_required_parameters()

        # Parse structure blocks
        self._validate_structure_blocks()

        # Check parameter values
        self._validate_parameters()

    def _check_required_parameters(self):
        """Check for required global parameters."""
        required = ['tolerance', 'output', 'filetype']
        found = {param: False for param in required}

        # Extract parameter names from content
        for line in self.lines:
            line = line.strip()
            # Skip comments
            if line.startswith('#'):
                continue
            # Check for required parameters
            for param in required:
                if re.match(rf'^{param}\b', line, re.IGNORECASE):
                    found[param] = True

        # Report missing parameters
        for param, present in found.items():
            if not present:
                self.errors.append(f"Missing required parameter: {param}")

    def _validate_structure_blocks(self):
        """Validate structure block syntax."""
        in_structure = False
        structure_count = 0
        structure_start_line = 0

        for i, line in enumerate(self.lines, 1):
            # Remove comments
            line_clean = re.sub(r'#.*$', '', line).strip()
            if not line_clean:
                continue

            # Check for structure start
            if re.match(r'^structure\b', line_clean, re.IGNORECASE):
                if in_structure:
                    self.errors.append(
                        f"Line {i}: Nested structure blocks found. "
                        f"Previous structure started at line {structure_start_line}"
                    )
                in_structure = True
                structure_start_line = i
                structure_count += 1

                # Check structure syntax
                match = re.match(r'^structure\s+(\S+)', line_clean, re.IGNORECASE)
                if not match:
                    self.errors.append(
                        f"Line {i}: Invalid structure syntax. "
                        f"Expected: structure <filename>"
                    )
                else:
                    filename = match.group(1)
                    self._check_structure_file(filename, i)

            # Check for structure end
            elif re.match(r'^end\s+structure\b', line_clean, re.IGNORECASE):
                if not in_structure:
                    self.errors.append(
                        f"Line {i}: 'end structure' without matching 'structure'"
                    )
                in_structure = False

        # Check for unclosed structure block
        if in_structure:
            self.errors.append(
                f"Unclosed structure block starting at line {structure_start_line}"
            )

        # Check for at least one structure
        if structure_count == 0:
            self.errors.append("No structure blocks found")

    def _check_structure_file(self, filename: str, line: int):
        """Check if structure file exists."""
        structure_path = Path(filename)

        # Try relative to input file directory
        if not structure_path.exists():
            # Try in same directory as input file
            in_input_dir = self.filename.parent / filename
            if not in_input_dir.exists():
                self.warnings.append(
                    f"Line {line}: Structure file '{filename}' not found. "
                    f"This will cause an error when running Packmol."
                )

    def _validate_parameters(self):
        """Validate parameter values."""
        for i, line in enumerate(self.lines, 1):
            # Remove comments
            line_clean = re.sub(r'#.*$', '', line).strip()
            if not line_clean:
                continue

            # Validate tolerance
            if re.match(r'^tolerance\b', line_clean, re.IGNORECASE):
                match = re.match(r'^tolerance\s+(\d+\.?\d*)', line_clean, re.IGNORECASE)
                if match:
                    tolerance = float(match.group(1))
                    if tolerance <= 0:
                        self.errors.append(f"Line {i}: tolerance must be positive")
                    if tolerance > 10:
                        self.warnings.append(
                            f"Line {i}: tolerance={tolerance} is unusually large. "
                            f"Typical values are 1.5-3.0 Å"
                        )
                    if tolerance < 0.5:
                        self.warnings.append(
                            f"Line {i}: tolerance={tolerance} is very small. "
                            f"This may cause slow convergence or failure."
                        )
                else:
                    self.errors.append(f"Line {i}: Invalid tolerance value")

            # Validate filetype
            if re.match(r'^filetype\b', line_clean, re.IGNORECASE):
                match = re.match(r'^filetype\s+(\w+)', line_clean, re.IGNORECASE)
                if match:
                    filetype = match.group(1).lower()
                    if filetype not in ['pdb', 'xyz', 'tinker']:
                        self.errors.append(
                            f"Line {i}: Invalid filetype '{filetype}'. "
                            f"Must be pdb, xyz, or tinker"
                        )
                else:
                    self.errors.append(f"Line {i}: Invalid filetype specification")

            # Validate pbc (if present)
            if re.match(r'^pbc\b', line_clean, re.IGNORECASE):
                parts = line_clean.split()
                if len(parts) not in [4, 7]:
                    self.errors.append(
                        f"Line {i}: pbc requires 3 (orthorhombic) or 6 (box) parameters"
                    )
                else:
                    # Try to parse as floats
                    try:
                        values = [float(p) for p in parts[1:]]
                        if len(values) == 6 and values[3] <= values[0]:
                            self.errors.append(
                                f"Line {i}: Invalid pbc box (xmax <= xmin)"
                            )
                        if len(values) == 6 and values[4] <= values[1]:
                            self.errors.append(
                                f"Line {i}: Invalid pbc box (ymax <= ymin)"
                            )
                        if len(values) == 6 and values[5] <= values[2]:
                            self.errors.append(
                                f"Line {i}: Invalid pbc box (zmax <= zmin)"
                            )
                    except ValueError:
                        self.errors.append(f"Line {i}: pbc parameters must be numeric")

            # Validate number parameter in structure blocks
            if re.match(r'^number\b', line_clean, re.IGNORECASE):
                match = re.match(r'^number\s+(\d+)', line_clean, re.IGNORECASE)
                if match:
                    number = int(match.group(1))
                    if number <= 0:
                        self.errors.append(f"Line {i}: number must be positive")
                    if number > 1000000:
                        self.warnings.append(
                            f"Line {i}: number={number} is very large. "
                            f"This may require significant memory and time."
                        )
                else:
                    self.errors.append(f"Line {i}: Invalid number value")

            # Validate constraint syntax
            self._validate_constraint(line_clean, i)

    def _validate_constraint(self, line: str, line_num: int):
        """Validate constraint syntax."""
        # Box constraint
        if re.search(r'\binside\s+box\b', line, re.IGNORECASE):
            match = re.search(
                r'inside\s+box\s+'
                r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+'
                r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)',
                line, re.IGNORECASE
            )
            if not match:
                self.errors.append(
                    f"Line {line_num}: Invalid box constraint syntax. "
                    f"Expected: inside box xmin ymin zmin xmax ymax zmax"
                )
            else:
                coords = [float(match.group(i)) for i in range(1, 7)]
                if coords[3] <= coords[0]:
                    self.errors.append(f"Line {line_num}: box xmax <= xmin")
                if coords[4] <= coords[1]:
                    self.errors.append(f"Line {line_num}: box ymax <= ymin")
                if coords[5] <= coords[2]:
                    self.errors.append(f"Line {line_num}: box zmax <= zmin")

        # Sphere constraint
        elif re.search(r'\binside\s+sphere\b', line, re.IGNORECASE):
            match = re.search(
                r'inside\s+sphere\s+'
                r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+'
                r'(\d+\.?\d*)',
                line, re.IGNORECASE
            )
            if not match:
                self.errors.append(
                    f"Line {line_num}: Invalid sphere constraint syntax. "
                    f"Expected: inside sphere xc yc zc radius"
                )
            else:
                radius = float(match.group(4))
                if radius <= 0:
                    self.errors.append(f"Line {line_num}: sphere radius must be positive")

        # Cylinder constraint
        elif re.search(r'\binside\s+cylinder\b', line, re.IGNORECASE):
            match = re.search(
                r'inside\s+cylinder\s+'
                r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+'
                r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+'
                r'(\d+\.?\d*)\s+(\d+\.?\d*)',
                line, re.IGNORECASE
            )
            if not match:
                self.errors.append(
                    f"Line {line_num}: Invalid cylinder constraint syntax. "
                    f"Expected: inside cylinder x1 y1 z1 dx dy dz radius length"
                )

        # Plane constraint
        elif re.search(r'\b(above|below)\s+plane\b', line, re.IGNORECASE):
            match = re.search(
                r'(above|below)\s+plane\s+'
                r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+'
                r'(-?\d+\.?\d*)',
                line, re.IGNORECASE
            )
            if not match:
                self.errors.append(
                    f"Line {line_num}: Invalid plane constraint syntax. "
                    f"Expected: above/below plane a b c d"
                )
            else:
                a, b, c = [float(match.group(i)) for i in range(2, 5)]
                if a == 0 and b == 0 and c == 0:
                    self.errors.append(
                        f"Line {line_num}: plane normal vector cannot be (0, 0, 0)"
                    )

        # Fixed constraint
        elif re.match(r'^fixed\b', line, re.IGNORECASE):
            parts = line.split()
            if len(parts) != 7:
                self.errors.append(
                    f"Line {line_num}: Invalid fixed syntax. "
                    f"Expected: fixed x y z a b c (6 parameters)"
                )
            else:
                # Try to parse as floats
                try:
                    values = [float(p) for p in parts[1:]]
                except ValueError:
                    self.errors.append(
                        f"Line {line_num}: fixed parameters must be numeric"
                    )


def print_report(errors: List[str], warnings: List[str]):
    """Print validation report."""
    if not errors and not warnings:
        print("✓ Input file is valid!")
        return

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  • {error}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  • {warning}")

    # Summary
    print()
    if errors:
        print("Please fix the errors before running Packmol.")
        sys.exit(1)
    else:
        print("No critical errors found, but warnings should be reviewed.")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python validate_input.py <input_file>")
        print("\nExample:")
        print("  python validate_input.py solvation.inp")
        sys.exit(1)

    filename = sys.argv[1]

    print(f"Validating Packmol input file: {filename}")
    print()

    validator = PackmolValidator(filename)
    errors, warnings = validator.validate()

    print_report(errors, warnings)

    if not errors:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
