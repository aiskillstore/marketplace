# Basic Packmol Examples

This directory contains simple Packmol input files demonstrating basic molecular packing.

## Examples

### 1. simple_box.inp

**Purpose**: Create a box containing a single type of molecule

**Description**: This is the minimal Packmol input file. It packs 1000 water molecules into a 40 × 40 × 40 Å box.

**Use case**: Starting point for creating pure solvent boxes, understanding basic Packmol syntax

**Requirements**:
- `water.pdb` - PDB file with a single water molecule

**To run**:
```bash
packmol < simple_box.inp
```

**Expected output**: `water_box.pdb` with 3000 atoms (1000 water molecules)

**Modifications**:
- Change `number 1000` to adjust molecule count
- Change box dimensions (`0. 0. 0. 40. 40. 40.`) for different box sizes
- Replace `water.pdb` with any other molecule file

**Tips**:
- For 1.0 g/cm³ water density, use ~1200 water molecules in this box size
- Adjust `tolerance` based on your model (2.0 Å for all-atom)

---

### 2. mixture.inp

**Purpose**: Create a box with multiple molecule types

**Description**: Demonstrates packing two different molecule types (water and urea) in the same box with an 8:2 molar ratio.

**Use case**: Mixed solvent systems, cosolvents, additive solutions

**Requirements**:
- `water.pdb` - PDB file with a single water molecule
- `urea.pdb` - PDB file with a single urea molecule

**To run**:
```bash
packmol < mixture.inp
```

**Expected output**: `mixture.pdb` with 1000 total molecules (800 water + 200 urea)

**Modifications**:
- Adjust molar ratios by changing `number` values
- Replace molecule types for different mixtures
- Common mixtures: water/ethanol, water/glycerol, water/DMSO

**Tips**:
- Maintain total number appropriate for desired density
- Use same tolerance for all components
- Test with small systems first

---

## General Notes

### Preparing Molecule Files

Each `.pdb` file should contain:
- A single molecule (or repeat unit)
- Proper atom coordinates
- Correct element names in columns 13-14
- Optional: CONECT records for bonds

### Common Issues

1. **"ERROR: Opening file"**: Ensure all `.pdb` files exist in current directory
2. **Low density**: Increase `number` values to add more molecules
3. **High density**: Decrease `number` values or increase box size
4. **No convergence**: Try increasing `tolerance` or reducing molecule count

### Typical Densities

For 40 × 40 × 40 Å box (64,000 Å³ volume):
- Water (1.0 g/cm³): ~1200 molecules
- Water/urea mixtures: ~1000-1100 total molecules
- Pure organic solvents: Varies by molecular weight

### Next Steps

After mastering these basic examples, explore:
- **Solvation examples**: Add biomolecules to solvent boxes
- **Interface examples**: Create liquid-liquid interfaces
- **Advanced examples**: Complex geometries like vesicles and cylinders

---

## Testing Your Setup

To verify Packmol is working correctly:

1. Create a minimal `water.pdb` file with coordinates:
   ```
   ATOM      1  O   HOH     1       0.000   0.000   0.000  1.00  0.00
   ATOM      2  H1  HOH     1       0.959   0.000  -0.243  1.00  0.00
   ATOM      3  H2  HOH     1      -0.240   0.000  -0.927  1.00  0.00
   END
   ```

2. Run `packmol < simple_box.inp`

3. Check for success message in output

4. Verify output file `water_box.pdb` was created

For more help, see the main [SKILL.md](../../SKILL.md) or [references](../../references/).
