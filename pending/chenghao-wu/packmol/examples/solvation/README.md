# Solvation Examples

Examples for solvating biomolecules with water and ions for molecular dynamics simulations.

## Examples

### 1. protein_solvation.inp

**Purpose**: Solvate a protein with water and ions

**Description**: Creates a solvation shell around a protein, with Na⁺ and Cl⁻ ions for neutrality and salt concentration.

**Use case**: Preparing protein systems for MD simulations

**System setup**:
- 1 protein (fixed at box center)
- 5000 water molecules
- 10 Na⁺ ions
- 10 Cl⁻ ions
- Box size: 60 × 60 × 80 Å

**Requirements**:
- `protein.pdb` - Your protein structure
- `water.pdb` - Single water molecule (TIP3P recommended)
- `SOD.pdb` - Sodium ion
- `CLA.pdb` - Chloride ion

**To run**:
```bash
packmol < protein_solvation.inp
```

**Expected output**: `solvated.pdb` with ~25,000 atoms

**Modifications**:
1. **Adjust box size**:
   - Get protein dimensions from `protein.pdb`
   - Add 10-15 Å solvent shell around protein
   - Example: protein spans 0-40 Å → box -10 to 70 Å (80 Å total)

2. **Calculate water molecules**:
   - For 60×60×80 Å box = 288,000 Å³
   - At 1 g/cm³: ~9600 water molecules
   - Subtract protein volume
   - This example uses 5000 (adjust for density)

3. **Adjust ions**:
   - **Neutralization**: Add ions to counter protein charge
     - If protein charge = +4: Add 4 Cl⁻
   - **Salt concentration**: Add equal amounts of Na⁺ and Cl⁻
     - For 0.15 M NaCl in 60×60×80 Å box: ~15 Na⁺ and 15 Cl⁻
     - Formula: `N_ions = concentration × volume(L) × NA`

**Tips**:
- Use `solvate_helper.py` for automatic setup:
  ```bash
  python scripts/solvate_helper.py protein.pdb --shell 15.0 --charge +4 --conc 0.15
  ```
- Verify density with `analyze_density.py`
- Check for overlaps with `check_overlaps.py`
- Add PBC for periodic MD simulations

---

### 2. water_box.inp

**Purpose**: Create a pure water box

**Description**: Simple water box at ~1.0 g/cm³ density, useful as a starting point or for testing.

**Use case**:
- Equilibration runs
- Solvent for adding solutes later
- Testing water models and MD parameters

**System setup**:
- 1200 water molecules
- Box size: 40 × 40 × 40 Å
- Density: ~1.0 g/cm³

**Requirements**:
- `water.pdb` - Single water molecule

**To run**:
```bash
packmol < water_box.inp
```

**Expected output**: `water_box.pdb` with 3600 atoms

**Modifications**:
- Change box dimensions for different sizes
- Adjust molecule count for desired density
- Add salt ions: include SOD.pdb and CLA.pdb structure blocks

**Water models**:
- TIP3P: Most common, recommended
- SPC/E: Slightly better bulk properties
- TIP4P: Better diffusion properties
- TIP5P: Five-site model (more accurate, slower)

**Tips**:
- Verify density with `analyze_density.py`
- 1 water ≈ 30 Å³ at 1 g/cm³
- For NPT equilibration: start with slightly lower density
- Add solutes later using `fixed` constraint

---

## General Solvation Guidelines

### Preparing Structure Files

**Protein PDB**:
- Clean structure: remove waters, ligands, ions
- Add missing hydrogens (use pdb2gmx, reduce, etc.)
- Check for missing residues/atoms
- Verify proper protonation states

**Water Model**:
- Use consistent water model for your MD software
- TIP3P is standard for AMBER, CHARMM
- Download or create single water PDB

**Ions**:
- Use standard ion names for your MD software
- AMBER: SOD (Na⁺), CLA (Cl⁻)
- CHARMM: SOD, CLA (or specific ion types)
- GROMACS: NA, CL (convert with pdb2gmx)

### Calculating Box Size

1. **Get protein dimensions**:
   ```bash
   # Use grep to find min/max coordinates
   grep "^ATOM" protein.pdb | awk '{print $7, $8, $9}'
   ```
   Or use visualization software (VMD, PyMOL)

2. **Add solvent shell**:
   - Minimum: 10 Å (may have artifacts)
   - Recommended: 12-15 Å
   - For large proteins: 15-20 Å

3. **Example calculation**:
   ```
   Protein spans: 0 to 45 Å in x, y, z
   Solvent shell: 15 Å
   Box size: 60 × 60 × 60 Å
   ```

### Calculating Water Molecules

**Rough estimation**:
```
V_box = L × W × H (Å³)
V_protein = approximate from molecular weight or software
V_water = V_box - V_protein
N_water = V_water / 30  (at 1.0 g/cm³)
```

**For 60×60×60 Å box**:
```
V_box = 216,000 Å³
V_protein ≈ 30,000 Å³ (typical medium protein)
V_water = 186,000 Å³
N_water ≈ 186,000 / 30 ≈ 6200 molecules
```

**Better approach**: Use `solvate_helper.py` script

### Ion Calculations

**Neutralization**:
```
Charge to neutralize = protein charge / e
N_counterions = |charge|

If protein = +4:
  Add 4 Cl⁻
```

**Salt concentration**:
```
N_ions = concentration × volume × NA

For 0.15 M in 60×60×60 Å box:
V = 216,000 Å³ = 216,000 × 10⁻³⁰ L = 2.16 × 10⁻²² L
N = 0.15 mol/L × 2.16 × 10⁻²² L × 6.022 × 10²³ mol⁻¹
N ≈ 20 ions of each type

Total: 10 Na⁺, 10 Cl⁻ (if neutral)
      14 Na⁺, 10 Cl⁻ (if protein +4 charge)
```

### Common Issues

1. **Low density**:
   - Increase `number` of waters
   - Check box dimensions
   - Verify with `analyze_density.py`

2. **Protein too close to box edge**:
   - Increase box size
   - Add larger solvent shell
   - Use `center` with `fixed` properly

3. **Wrong ion count**:
   - Calculate protein charge first
   - Use `pdb2gmx` or similar to determine charge
   - Verify neutralization

4. **Overlaps**:
   - Check with `check_overlaps.py`
   - May need to increase `tolerance`
   - Ensure protein structure is reasonable

### Workflow

1. **Prepare protein**: Clean, add hydrogens, verify
2. **Calculate box size**: Based on protein + shell
3. **Calculate water count**: For desired density
4. **Calculate ions**: Neutralization + salt
5. **Create input file**: Use template or script
6. **Validate input**: `validate_input.py`
7. **Run Packmol**: `packmol < input.inp`
8. **Verify output**: `verify_success.py`, `check_overlaps.py`
9. **Check density**: `analyze_density.py`

### Next Steps

After solvation:

1. **Energy minimization**: Remove any remaining overlaps
2. **Equilibration**: NVT then NPT to relax solvent
3. **Production MD**: Your actual simulation
4. **Analysis**: As needed for your research

### Automatic Tools

Use `solvate_helper.py` for automation:

```bash
python scripts/solvate_helper.py protein.pdb \
  --shell 15.0 \
  --charge +4 \
  --conc 0.15 \
  --output solvated.pdb
```

This automatically:
- Calculates box size
- Estimates water count
- Calculates ions
- Generates Packmol input
- Optionally runs Packmol

---

## For More Help

- Main skill: [SKILL.md](../../SKILL.md)
- Templates: [../../templates/](../../templates/)
- Scripts: [../../scripts/](../../scripts/)
- Troubleshooting: [../../references/troubleshooting.md](../../references/troubleshooting.md)
