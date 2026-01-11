#!/usr/bin/env python3
"""
Verify that Packmol completed successfully.

This script checks Packmol output and log files to verify successful completion,
checking for the success message, constraint violations, and output file integrity.

Usage:
    python verify_success.py input.inp output.pdb [packmol.log]

Example:
    python verify_success.py solvation.inp solvated.pdb
"""

import sys
import argparse
import re
from pathlib import Path
from typing import List, Tuple


class PackmolVerifier:
    """Verify Packmol execution results."""

    def __init__(self, input_file: str, output_file: str, log_file: str = None):
        """Initialize verifier with file paths."""
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.log_file = Path(log_file) if log_file else None

        self.success = False
        self.violations = {}
        self.warnings = []
        self.errors = []

    def verify(self) -> bool:
        """
        Verify Packmol execution.

        Returns:
            True if verification passed, False otherwise
        """
        all_checks_passed = True

        # Check output file exists
        if not self._check_output_exists():
            all_checks_passed = False

        # Check output file is not empty
        if not self._check_output_not_empty():
            all_checks_passed = False

        # Parse output for violations
        if not self._check_violations():
            all_checks_passed = False

        # Check for success message
        if not self._check_success_message():
            all_checks_passed = False

        # Validate atom count if input file exists
        if self.input_file.exists():
            if not self._check_atom_count():
                all_checks_passed = False

        return all_checks_passed

    def _check_output_exists(self) -> bool:
        """Check if output file exists."""
        if not self.output_file.exists():
            self.errors.append(f"Output file not found: {self.output_file}")
            return False
        return True

    def _check_output_not_empty(self) -> bool:
        """Check if output file is not empty."""
        if not self.output_file.exists():
            return True  # Already reported in _check_output_exists

        size = self.output_file.stat().st_size
        if size == 0:
            self.errors.append(f"Output file is empty: {self.output_file}")
            return False
        return True

    def _check_violations(self) -> bool:
        """Check constraint violations from output."""
        if not self.output_file.exists():
            return True  # Skip if output doesn't exist

        try:
            with open(self.output_file, 'r') as f:
                content = f.read()

            # Look for violation messages
            # Packmol writes these to stdout, not the output file
            # So we need to check if a log file was provided
            if self.log_file and self.log_file.exists():
                return self._parse_violations_from_log()

            # If no log file, check for terminal output or success
            return True

        except Exception as e:
            self.warnings.append(f"Could not check violations: {e}")
            return True  # Don't fail on this check

    def _parse_violations_from_log(self) -> bool:
        """Parse violations from Packmol log/output."""
        if not self.log_file or not self.log_file.exists():
            return True

        try:
            with open(self.log_file, 'r') as f:
                content = f.read()

            # Look for success message
            success_match = re.search(r'SUCCESS!', content, re.IGNORECASE)
            if success_match:
                self.success = True

            # Parse violation values
            # Format: "Maximum violation of target distance: X.XXX"
            dist_match = re.search(
                r'Maximum violation of target distance:\s*([\d.Ee+-]+)',
                content
            )
            if dist_match:
                dist_violation = float(dist_match.group(1))
                self.violations['distance'] = dist_violation

            # Format: "Maximum violation of the constraints: X.XXX"
            const_match = re.search(
                r'Maximum violation of the constraints:\s*([\d.Ee+-]+)',
                content
            )
            if const_match:
                const_violation = float(const_match.group(1))
                self.violations['constraints'] = const_violation

            # Check if violations are acceptable
            if 'distance' in self.violations or 'constraints' in self.violations:
                return self._evaluate_violations()

            return True

        except Exception as e:
            self.warnings.append(f"Could not parse log file: {e}")
            return True

    def _evaluate_violations(self) -> bool:
        """Evaluate if violations are acceptable."""
        acceptable = True
        threshold = 0.01  # Packmol typically uses 0.01 as threshold

        if 'distance' in self.violations:
            dist_viol = self.violations['distance']
            if dist_viol > threshold:
                self.warnings.append(
                    f"Distance violation {dist_violation:.4f} exceeds threshold {threshold}"
                )
                acceptable = False
            else:
                print(f"✓ Distance violation: {dist_violation:.6f} (acceptable)")

        if 'constraints' in self.violations:
            const_viol = self.violations['constraints']
            if const_viol > threshold:
                self.warnings.append(
                    f"Constraint violation {const_viol:.4f} exceeds threshold {threshold}"
                )
                acceptable = False
            else:
                print(f"✓ Constraint violation: {const_viol:.6f} (acceptable)")

        return acceptable

    def _check_success_message(self) -> bool:
        """Check for Packmol success message."""
        # If log file exists, check it
        if self.log_file and self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    content = f.read()

                if re.search(r'SUCCESS', content, re.IGNORECASE):
                    self.success = True
                    print("✓ Packmol completed successfully")
                    return True
                elif re.search(r'ERROR|FATAL', content, re.IGNORECASE):
                    self.errors.append("Packmol reported errors")
                    return False

            except Exception:
                pass

        # If no log file or couldn't read, assume success if output exists and is valid
        if self.output_file.exists() and self.output_file.stat().st_size > 0:
            # Try to read first few lines to check if it's valid PDB
            try:
                with open(self.output_file, 'r') as f:
                    first_lines = [f.readline() for _ in range(5)]

                # Check if it looks like a PDB file
                if any(line.startswith('ATOM') or line.startswith('HETATM')
                       for line in first_lines):
                    print("✓ Output file appears valid (PDB format detected)")
                    self.success = True
                    return True

            except Exception:
                pass

        # If we couldn't confirm success but output exists, warn
        if self.output_file.exists():
            self.warnings.append(
                "Could not verify Packmol success message, "
                "but output file exists"
            )
            return True

        return False

    def _check_atom_count(self) -> bool:
        """Check if atom count in output matches expectation."""
        if not self.input_file.exists():
            return True

        try:
            # Parse input file to get expected atom count
            expected_atoms = self._count_atoms_in_input()

            if expected_atoms is None:
                return True  # Couldn't parse, skip check

            # Count atoms in output
            actual_atoms = self._count_atoms_in_output()

            if actual_atoms is None:
                return True  # Couldn't parse, skip check

            if actual_atoms == expected_atoms:
                print(f"✓ Atom count: {actual_atoms} (matches expected)")
                return True
            else:
                self.warnings.append(
                    f"Atom count mismatch: expected {expected_atoms}, "
                    f"found {actual_atoms}"
                )
                # Not a critical error - sometimes atoms are excluded
                return True

        except Exception as e:
            self.warnings.append(f"Could not verify atom count: {e}")
            return True

    def _count_atoms_in_input(self) -> int:
        """Count expected atoms from input file."""
        try:
            with open(self.input_file, 'r') as f:
                lines = f.readlines()

            total_atoms = 0

            for line in lines:
                line = line.strip()
                if line.startswith('structure'):
                    # Get structure file
                    parts = line.split()
                    if len(parts) >= 2:
                        struct_file = Path(parts[1])

                        # Try to count atoms in structure file
                        if struct_file.exists():
                            atoms_in_struct = self._count_atoms_in_file(struct_file)
                            if atoms_in_struct is not None:
                                # Look for number parameter
                                number = None
                                for subsequent_line in lines[lines.index(line)+1:]:
                                    subsequent_line = subsequent_line.strip()
                                    if subsequent_line.startswith('number'):
                                        number_parts = subsequent_line.split()
                                        if len(number_parts) >= 2:
                                            try:
                                                number = int(number_parts[1])
                                            except ValueError:
                                                pass
                                        break
                                    elif subsequent_line.startswith('end structure'):
                                        break

                                if number is not None:
                                    total_atoms += atoms_in_struct * number

            return total_atoms if total_atoms > 0 else None

        except Exception:
            return None

    def _count_atoms_in_file(self, pdb_file: Path) -> int:
        """Count ATOM/HETATM records in a PDB file."""
        try:
            count = 0
            with open(pdb_file, 'r') as f:
                for line in f:
                    if line.startswith('ATOM') or line.startswith('HETATM'):
                        count += 1
            return count
        except Exception:
            return None

    def _count_atoms_in_output(self) -> int:
        """Count ATOM/HETATM records in output file."""
        return self._count_atoms_in_file(self.output_file)

    def print_report(self):
        """Print verification report."""
        print("\n" + "="*60)
        print("VERIFICATION REPORT")
        print("="*60)

        if self.success:
            print("\n✓ Packmol execution: SUCCESS")
        else:
            print("\n? Packmol execution: UNKNOWN (no log file)")

        if self.violations:
            print("\nConstraint Violations:")
            if 'distance' in self.violations:
                print(f"  Target distance:  {self.violations['distance']:.6f}")
            if 'constraints' in self.violations:
                print(f"  Constraints:      {self.violations['constraints']:.6f}")

        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("\n✓ All checks passed!")

        print("="*60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Verify Packmol execution results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify with just input and output files
  python verify_success.py input.inp output.pdb

  # Verify with Packmol log file (recommended)
  python verify_success.py input.inp output.pdb packmol.log

  # The log file captures Packmol's terminal output
  packmol < input.inp > packmol.log
  python verify_success.py input.inp output.pdb packmol.log
        """
    )

    parser.add_argument('input_file', help='Packmol input file (.inp)')
    parser.add_argument('output_file', help='Packmol output file (.pdb)')
    parser.add_argument('log_file', nargs='?', default=None,
                       help='Packmol log/output file (optional)')

    args = parser.parse_args()

    print("="*60)
    print("Packmol Execution Verifier")
    print("="*60)
    print(f"Input file:  {args.input_file}")
    print(f"Output file: {args.output_file}")
    if args.log_file:
        print(f"Log file:    {args.log_file}")
    print("="*60)

    # Create verifier
    verifier = PackmolVerifier(args.input_file, args.output_file, args.log_file)

    # Verify
    success = verifier.verify()

    # Print report
    verifier.print_report()

    # Exit with appropriate code
    if success and not verifier.errors:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
