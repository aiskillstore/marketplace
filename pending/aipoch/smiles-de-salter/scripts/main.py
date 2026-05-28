#!/usr/bin/env python3
"""SMILES De-salter
Batch process chemical structure strings, remove the salt ion part, and retain only the active core.

Author: OpenClaw Skill Hub
Version: 1.0.0"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List, Tuple

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors
except ImportError:
    print("Error: RDKit is required. Install with: pip install rdkit", file=sys.stderr)
    sys.exit(1)


def get_molecule_size(mol: Chem.Mol) -> int:
    """Get the size of the molecule (in number of heavy atoms)
    
    Args:
        mol: RDKit Mol object
    
    Returns:
        Number of heavy atoms"""
    return mol.GetNumHeavyAtoms()


def is_likely_salt(mol: Chem.Mol) -> bool:
    """Determine whether a molecule is likely to be a salt ion
    
    Based on heuristic rules:
    - Small molecules (<= 3 heavy atoms)
    - Common inorganic ions
    
    Args:
        mol: RDKit Mol object
    
    Returns:
        could it be salt"""
    heavy_atoms = mol.GetNumHeavyAtoms()
    
    # Very small molecules are probably salts
    if heavy_atoms <= 2:
        return True
    
    # Get molecular formula
    formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
    
    # Simple pattern of common salt ions
    common_salts = ['Cl', 'Br', 'F', 'I', 'Na', 'K', 'Ca', 'Mg', 'Zn', 'Fe']
    # If it contains only common salts and a few atoms
    if heavy_atoms <= 3:
        for salt in common_salts:
            if salt in formula:
                return True
    
    return False


def desalt_smiles(smiles: str, keep_largest: bool = True) -> Tuple[str, str]:
    """Remove salt ions from SMILES string
    
    Args:
        smiles: input SMILES string
        keep_largest: Whether to keep the largest component (by number of heavy atoms)
    
    Returns:
        (Processed SMILES, status information)"""
    if not smiles or not smiles.strip():
        return "", "empty_input"
    
    smiles = smiles.strip()
    
    # Parse SMILES
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return smiles, "invalid_smiles"
    
    # Split components by '.'
    # NOTE: Use RDKit's SaltStripper or split manually
    frags = smiles.split('.')
    
    if len(frags) <= 1:
        # no salt structure
        return smiles, "no_salt"
    
    # Parse each component
    valid_frags = []
    for frag in frags:
        frag = frag.strip()
        if not frag:
            continue
        frag_mol = Chem.MolFromSmiles(frag)
        if frag_mol is not None:
            valid_frags.append((frag, frag_mol))
    
    if not valid_frags:
        return smiles, "invalid_smiles"
    
    if len(valid_frags) == 1:
        return valid_frags[0][0], "no_salt"
    
    if keep_largest:
        # Sort by molecular size, keeping the largest
        valid_frags.sort(key=lambda x: get_molecule_size(x[1]), reverse=True)
        
        # Returns the largest component
        largest_frag, largest_mol = valid_frags[0]
        
        # Check if the largest component is also considered salt (unusual case)
        if is_likely_salt(largest_mol) and len(valid_frags) > 1:
            # Find the first non-salt macromolecule
            for frag, frag_mol in valid_frags:
                if not is_likely_salt(frag_mol):
                    return frag, "success"
        
        return largest_frag, "success"
    else:
        # Returns all non-salt components (concatenated with .)
        non_salt_frags = []
        for frag, frag_mol in valid_frags:
            if not is_likely_salt(frag_mol):
                non_salt_frags.append(frag)
        
        if not non_salt_frags:
            # All are salt, return the largest one
            valid_frags.sort(key=lambda x: get_molecule_size(x[1]), reverse=True)
            return valid_frags[0][0], "all_salts"
        
        return '.'.join(non_salt_frags), "success"


def process_file(input_path: str, output_path: str, column: str = "smiles", 
                 keep_largest: bool = True) -> None:
    """Handle SMILES in files
    
    Args:
        input_path: input file path
        output_path: output file path
        column: SMILES column name
        keep_largest: whether to keep the largest component"""
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Detect file type and read
    suffix = input_file.suffix.lower()
    
    try:
        if suffix == '.csv':
            import pandas as pd
            df = pd.read_csv(input_path)
        elif suffix in ['.tsv', '.txt']:
            import pandas as pd
            if suffix == '.tsv':
                df = pd.read_csv(input_path, sep='\t')
            else:
                # Try to detect delimiter
                df = pd.read_csv(input_path, sep=None, engine='python')
        elif suffix == '.smi' or suffix == '.smiles':
            # Pure SMILES files
            import pandas as pd
            with open(input_path, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            df = pd.DataFrame({column: lines})
        else:
            # Default attempts CSV
            import pandas as pd
            df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check if column exists
    if column not in df.columns:
        print(f"Error: Column '{column}' not found in input file.", file=sys.stderr)
        print(f"Available columns: {', '.join(df.columns)}", file=sys.stderr)
        sys.exit(1)
    
    # Process each row
    results = []
    statuses = []
    
    for smiles in df[column]:
        if pd.isna(smiles):
            results.append("")
            statuses.append("empty_input")
        else:
            desalted, status = desalt_smiles(str(smiles), keep_largest)
            results.append(desalted)
            statuses.append(status)
    
    # Add result column
    df['desalted_smiles'] = results
    df['status'] = statuses
    
    # Save results
    try:
        output_suffix = Path(output_path).suffix.lower()
        if output_suffix == '.csv':
            df.to_csv(output_path, index=False)
        elif output_suffix in ['.tsv', '.txt']:
            df.to_csv(output_path, sep='\t', index=False)
        else:
            df.to_csv(output_path, index=False)
        print(f"Results saved to: {output_path}")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Statistics
    total = len(df)
    success = statuses.count('success')
    no_salt = statuses.count('no_salt')
    invalid = statuses.count('invalid_smiles')
    empty = statuses.count('empty_input')
    
    print(f"\nProcessing complete!")
    print(f"Total records: {total}")
    print(f"  - Successfully desalted: {success}")
    print(f"  - No salt found: {no_salt}")
    print(f"  - Invalid SMILES: {invalid}")
    print(f"  - Empty input: {empty}")


def main():
    parser = argparse.ArgumentParser(
        description='SMILES De-salter - Remove salt ions from chemical structures',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Process CSV files
  python main.py -i input.csv -o output.csv -c smiles
  
  # Process pure SMILES files
  python main.py -i compounds.smi -o result.csv
  
  #Single processing
  python main.py -s "CCO.[Na+]"
  
  # Keep all non-salt components (not just the largest ones)
  python main.py -i input.csv --keep-largest false"""
    )
    
    parser.add_argument('-i', '--input', type=str, help='Input file path (CSV/TSV/SMI)')
    parser.add_argument('-o', '--output', type=str, default='desalted_output.csv',
                        help='Output file path (default: desalted_output.csv)')
    parser.add_argument('-c', '--column', type=str, default='smiles',
                        help='Column name containing SMILES (default: smiles)')
    parser.add_argument('-s', '--smiles', type=str, help='Single SMILES string to process')
    parser.add_argument('-k', '--keep-largest', type=bool, default=True,
                        help='Keep the largest fragment (default: True)')
    
    args = parser.parse_args()
    
    # Single processing mode
    if args.smiles:
        result, status = desalt_smiles(args.smiles, args.keep_largest)
        print(f"Input:    {args.smiles}")
        print(f"Output:   {result}")
        print(f"Status:   {status}")
        return
    
    # file processing mode
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    process_file(args.input, args.output, args.column, args.keep_largest)


if __name__ == '__main__':
    main()
