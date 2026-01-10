# Packmol File Formats Reference

Complete guide to file format specifications and requirements for Packmol input and output.

## Overview

Packmol supports three structure file formats:
- **PDB** (Protein Data Bank) - Most common, recommended
- **XYZ** - Simple Cartesian coordinate format
- **TINKER** - TINKER molecular mechanics format

Format is specified with the `filetype` parameter:

```text
filetype pdb    # or xyz or tinker
```

## PDB Format (Recommended)

### Format Specification

Packmol reads and writes standard PDB format (as defined by the Protein Data Bank, version 3.3).

### Required Fields

Each atom record must have:

```
ATOM      serial  atom  res  chain  resseq  x      y      z      occ    temp
1234567890123456789012345678901234567890123456789012345678901234567890
          1-7    13-16 17-20 22     23-26   31-38  39-46  47-54  55-60  61-66
```

**Critical columns**:
- **1-6**: Record type ("ATOM" or "HETATM")
- **13-16**: Atom name
- **17-20**: Residue name
- **23-26**: Residue sequence number
- **31-38**: X coordinate (Å, right-justified, 8.3f format)
- **39-46**: Y coordinate (Å, right-justified, 8.3f format)
- **47-54**: Z coordinate (Å, right-justified, 8.3f format)

**Element identification** (columns 13-16):
```
Correct:
ATOM      1  O   HOH     1       0.000   0.000   0.000  1.00  0.00
ATOM      2  H1  HOH     1       0.959   0.000  -0.243  1.00  0.00
ATOM      3  H2  HOH     1      -0.240   0.000  -0.927  1.00  0.00

Incorrect (missing space):
ATOM     11OG   HOH     1       0.000   0.000   0.000  1.00  0.00
```

### Example: Water Molecule

```text
ATOM      1  O   HOH     1       0.000   0.000   0.000  1.00  0.00
ATOM      2  H1  HOH     1       0.959   0.000  -0.243  1.00  0.00
ATOM      3  H2  HOH     1      -0.240   0.000  -0.927  1.00  0.00
END
```

### Example: Protein Fragment

```text
ATOM      1  N   MET     1      10.204  20.157  30.281  1.00  0.00
ATOM      2  CA  MET     1      11.523  20.853  30.673  1.00  0.00
ATOM      3  C   MET     1      12.498  19.758  31.210  1.00  0.00
ATOM      4  O   MET     1      12.134  18.588  31.059  1.00  0.00
ATOM      5  CB  MET     1      11.345  21.892  31.770  1.00  0.00
ATOM      6  CG  MET     1      12.754  22.534  31.923  1.00  0.00
ATOM      7  SD  MET     1      13.058  23.743  30.889  1.00  0.00
ATOM      8  CE  MET     1      14.642  23.412  30.630  1.00  0.00
TER
END
```

### Optional Features

#### CONECT Records

Define connectivity between atoms:

```text
ATOM      1  O   HOH     1       0.000   0.000   0.000  1.00  0.00
ATOM      2  H1  HOH     1       0.959   0.000  -0.243  1.00  0.00
ATOM      3  H2  HOH     1      -0.240   0.000  -0.927  1.00  0.00
CONECT    1    2    3
END
```

Note: Packmol doesn't use CONECT records for packing, but preserves them in output.

#### TER Records

Indicate chain/terminus:

```text
ATOM      1  N   ALA     1       0.000   0.000   0.000  1.00  0.00
ATOM      2  CA  ALA     1       1.458   0.000   0.000  1.00  0.00
TER
ATOM      3  N   GLY     2       3.102   0.000   0.000  1.00  0.00
END
```

#### Chain Identifiers

Specify chain with column 22:

```text
ATOM      1  N   MET A   1      10.204  20.157  30.281  1.00  0.00
ATOM      2  N   MET B   1      15.204  20.157  30.281  1.00  0.00
```

Or use `chain` parameter in input:

```text
structure protein.pdb
  number 1
  chain A
  fixed 0. 0. 0. 0. 0. 0.
end structure
```

### Residue Numbering

Control with `resnumbers` parameter:

```text
structure water.pdb
  number 100
  resnumbers 2    # Number each water separately
  inside box 0. 0. 0. 40. 40. 40.
end structure
```

Output numbering:
- `resnumbers 0`: Sequential across all molecules (default)
- `resnumbers 1`: Same as input file
- `resnumbers 2`: Increment per molecule
- `resnumbers 3`: Increment by chain

### PDB Format Requirements Summary

✓ **Must have**:
- ATOM or HETATM records
- Element symbol correctly positioned (columns 13-14)
- XYZ coordinates in columns 31-54 (8.3f format)

✓ **Recommended**:
- TER records between molecules
- Unique atom serial numbers
- Proper residue names

✗ **Common issues**:
- Element not in columns 13-14
- Coordinates not 8.3f format
- Missing spaces in atom names (e.g., "OG" instead of " OG")
- Missing END record

## XYZ Format

### Format Specification

Simple Cartesian coordinate format:

```
N_atoms
comment_line
element x y z
element x y z
...
```

### Example: Ethanol

```text
9
Ethanol molecule
C      1.2000    0.0000    0.0000
C      0.0000    0.0000    0.0000
O     -1.2000    0.0000    0.0000
H      1.6000    1.0000    0.0000
H      1.6000   -0.5000    0.8660
H      1.6000   -0.5000   -0.8660
H     -0.4000    0.9400    0.0000
H     -0.4000   -0.4700    0.8140
H     -1.6000   -0.4700   -0.8140
```

### Requirements

- First line: number of atoms
- Second line: comment (ignored by Packmol)
- Subsequent lines: element symbol and coordinates (in Å)
- Coordinates can be free format or fixed

### Advantages

- Simple and human-readable
- Easy to generate programmatically
- No specific column requirements

### Disadvantages

- No residue or chain information
- Limited metadata
- Not suitable for biomolecules

## TINKER Format

### Format Specification

TINKER Cartesian coordinate format:

```
N_atoms  # comment
atom_num  atom_type  x  y  z  [bond_connectivity]
...
```

### Example: Water

```text
3
  1   8    0.000000    0.000000    0.000000    2  2  3
  2   1    0.959000    0.000000   -0.243000    1  1
  3   1   -0.240000    0.000000   -0.927000    1  1
```

### Requirements

- First line: number of atoms
- Atom types must match TINKER force field
- Coordinates in Angstroms
- Bond connectivity (optional but recommended)

### Advantages

- Includes bond connectivity
- Force field atom types
- Suitable for molecular mechanics

### Disadvantages

- Requires TINKER atom types
- Less common than PDB
- More complex format

## Converting Between Formats

### Using Open Babel

```bash
# PDB to XYZ
obabel -ipdb input.pdb -oxyz output.xyz

# XYZ to PDB
obabel -ixyz input.xyz -opdb output.pdb

# PDB to TINKER
obabel -ipdb input.pdb -xtinker output.xyz
```

### Using Python (MDAnalysis)

```python
import MDAnalysis as mda

# Read any format
u = mda.Universe('input.pdb')

# Write to any format
u.atoms.write('output.xyz')
u.atoms.write('output.pdb')
```

### Using VMD

```tcl
# Load and save
set mol [molinfo top]
set sel [atomselect $mol all]
$sel writepdb "output.pdb"
```

## Format-Specific Considerations

### For Biomolecular Systems

**Use PDB format** because:
- Residue and chain information preserved
- Standard in structural biology
- Compatible with MD software (GROMACS, AMBER, CHARMM, NAMD)
- Supports secondary structure metadata

### For Small Molecules

**Options**:
- **PDB**: Most compatible, use for consistency
- **XYZ**: Simpler, easier to generate programmatically
- **TINKER**: Use if working with TINKER force field

### For Coarse-Grained Models

**Use PDB format**:
- Create custom residue names for beads
- Set appropriate atomic radii with `radius` parameter
- Example: MARTINI beads

```text
ATOM      1  BB  ALA     1       0.000   0.000   0.000  1.00  0.00
ATOM      2  SC1 ALA     1       1.000   0.000   0.000  1.00  0.00
```

## File Preparation Checklist

### Before Running Packmol

- [ ] Verify file format matches `filetype` parameter
- [ ] Check element symbols in correct columns (PDB)
- [ ] Ensure coordinates are in Angstroms
- [ ] Verify no missing atoms in structure
- [ ] Test file can be read by visualization software
- [ ] Check for duplicate atoms
- [ ] Verify molecule is complete and reasonable geometry

### Validation Commands

```bash
# Count atoms (PDB)
grep "^ATOM\|^HETATM" file.pdb | wc -l

# Check for END record (PDB)
tail -1 file.pdb

# Visualize in VMD
vmd file.pdb

# Convert formats
obabel -ipdb file.pdb -oxyz file.xyz
```

## Common Format Issues

### Issue: Element Not Recognized

**Symptom**: Packmol ignores atoms or gives errors

**Cause**: Element symbol not in columns 13-14 (PDB)

**Solution**:
```text
# Wrong
ATOM     11OG   HOH     1       0.000   0.000   0.000

# Right
ATOM      1  O   HOH     1       0.000   0.000   0.000
         ^^  ^^
         |   |
       space element
```

### Issue: Wrong Coordinates

**Symptom**: Molecules deformed or in wrong positions

**Cause**: Coordinates not in correct format or units

**Solution**:
- Ensure 8.3f format (PDB columns 31-54)
- Verify units are Angstroms (not nanometers or picometers)
- Check coordinate signs

### Issue: Missing Atoms

**Symptom**: Fewer atoms in output than expected

**Cause**: Format reading errors or skipped records

**Solution**:
- Verify all records are ATOM or HETATM
- Check for non-standard characters
- Validate file format specification

## Format Recommendations by Use Case

### Protein Solvation
```text
filetype pdb
# Use PDB for protein and solvent
```

### Liquid Mixtures
```text
filetype pdb
# PDB or XYZ both work
```

### Coarse-Grained
```text
filetype pdb
# Create custom residue names for beads
```

### Interface Systems
```text
filetype pdb
# PDB recommended for compatibility
```

### Gas Phase Clusters
```text
filetype xyz
# XYZ is simpler for small molecules
```

## Output Format Features

### Packmol PDB Output

Packmol writes standard PDB with:

- All input atoms with new positions
- Original atom serial numbers (or renumbered)
- Original residue names and numbers (unless `resnumbers` specified)
- Chain identifiers (if specified)
- TER records between molecules
- END record at file end
- CONECT records (if present in input)

### Atom Numbering in Output

Atom serial numbers are renumbered sequentially:
1. First molecule, atom 1
2. First molecule, atom 2
3. ...
4. Second molecule, atom 1
5. ...

To control numbering, use `resnumbers` parameter.

### Chain Identifiers in Output

Set chains with `chain` parameter:
```text
structure protein.pdb
  number 1
  chain A
  fixed 0. 0. 0. 0. 0. 0.
end structure

structure water.pdb
  number 1000
  chain W
  inside box 0. 0. 0. 40. 40. 40.
end structure
```

## Related Topics

- [Parameters reference](parameters.md) - filetype parameter, chain, resnumbers
- [Constraints reference](constraints.md) - Spatial constraints for molecules
- [Troubleshooting](troubleshooting.md) - File format issues

For format examples in context, see:
- [examples/basic/](../examples/basic/) - Simple PDB files
- [examples/solvation/](../examples/solvation/) - Protein and solvent PDB
