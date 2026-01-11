# Packmol Troubleshooting Guide

Solutions to common issues and errors when using Packmol.

## Overview

This guide helps diagnose and resolve problems with Packmol input files, convergence, and output quality. Issues are organized by error type and symptom.

## Quick Diagnosis

### Check Your Input First

Before troubleshooting, validate your input:

```bash
python scripts/validate_input.py your_input.inp
```

### Test with Minimal System

Create a minimal test case:
- Reduce molecule count to 10-50
- Use simple box constraint
- Remove optional parameters

If minimal case works, scale up gradually.

## Common Errors

### "ERROR: Opening file"

**Symptom**: Packmol cannot read structure file

**Causes**:
1. File doesn't exist
2. Wrong file path
3. Incorrect permissions
4. File format issues

**Solutions**:
```text
# Check file exists in current directory
ls -l water.pdb

# Use relative or absolute paths
structure /path/to/water.pdb
  number 100
  inside box 0. 0. 0. 40. 40. 40.
end structure

# Verify file format
head -20 water.pdb
```

**Prevention**:
- Keep all structure files in same directory as input file
- Use simple filenames (no spaces)
- Verify PDB format compliance

### "Killed" Error

**Symptom**: Process terminates with "Killed" message

**Cause**: System ran out of memory

**Solutions**:

1. **Reduce system size**
   ```text
   # Reduce molecule count
   structure water.pdb
     number 500    # Was 5000
     inside box 0. 0. 0. 40. 40. 40.
   end structure
   ```

2. **Use restart files** - Build system in stages
   ```text
   # Stage 1
   structure water.pdb
     number 2500
     restart_to stage1.pack
   end structure

   # Stage 2 (in separate input file)
   structure water.pdb
     number 2500
     restart_from stage1.pack
     fixed 0. 0. 0. 0. 0. 0.
   end structure

   structure water.pdb
     number 2500
     inside box 0. 0. 0. 40. 40. 40.
   end structure
   ```

3. **Increase system memory** or use machine with more RAM

4. **Reduce molecule complexity** - Use united-atom instead of all-atom

**Prevention**:
- Start with small systems
- Estimate memory: ~1-2 GB per 10,000 atoms
- Use restart files for large systems

### "ERROR: No solution found"

**Symptom**: Packmol cannot place all molecules

**Causes**:
1. Constraint region too small
2. Tolerance too large for region
3. Too many molecules for space
4. Conflicting constraints

**Solutions**:

1. **Reduce molecule count**
   ```text
   structure water.pdb
     number 800    # Was 1000
     inside box 0. 0. 0. 40. 40. 40.
   end structure
   ```

2. **Increase constraint region**
   ```text
   structure water.pdb
     number 1000
     inside box 0. 0. 0. 45. 45. 45.  # Was 40. 40. 40.
   end structure
   ```

3. **Reduce tolerance**
   ```text
   tolerance 1.8    # Was 2.0
   ```

4. **Check constraint conflicts**
   ```text
   # Use check keyword
   structure water.pdb
     number 100
     inside box 0. 0. 0. 30. 30. 30.
     check
   end structure
   ```

5. **Use discale for difficult cases**
   ```text
   discale 1.5
   ```

**Prevention**:
- Test with small systems first
- Calculate approximate density
- Leave room for optimization
- Use `check` keyword to validate constraints

### Convergence Issues

**Symptom**: Optimization runs but doesn't converge

**Causes**:
1. System too crowded
2. Complex constraints
3. Inappropriate tolerance
4. Local minima

**Solutions**:

1. **Increase discale**
   ```text
   discale 1.5    # Allows larger effective tolerance during optimization
   ```

2. **Increase maxit**
   ```text
   maxit 50       # Allow more iterations (default: 20)
   ```

3. **Adjust movefrac**
   ```text
   structure molecule.pdb
     number 100
     inside box 0. 0. 0. 30. 30. 30.
     movefrac 0.1    # Move more molecules per iteration
   end structure
   ```

4. **Reduce system complexity**
   - Remove some constraint types
   - Simplify geometry
   - Reduce molecule count

5. **Change tolerance**
   ```text
   tolerance 2.5    # Larger tolerance = easier convergence
   ```

**Prevention**:
- Start with simple systems
- Use appropriate tolerance for model type
- Build complex systems in stages

### Incorrect Geometry

**Symptom**: Output looks wrong (molecules in wrong positions)

**Causes**:
1. Misunderstood constraint syntax
2. Wrong constraint type
3. Coordinate system confusion
4. Conflicting constraints

**Solutions**:

1. **Visualize constraints** (mentally or with software)
2. **Use check keyword**
   ```text
   structure molecule.pdb
     number 10
     inside box 0. 0. 0. 30. 30. 30.
     check    # Validates constraints without optimization
   end structure
   ```

3. **Test with small system**
   ```text
   structure water.pdb
     number 10    # Small number for testing
     inside box 0. 0. 0. 30. 30. 30.
   end structure
   ```

4. **Verify constraint syntax**
   - Box: `inside box xmin ymin zmin xmax ymax zmax`
   - Sphere: `inside sphere xc yc zc radius`
   - Plane: `above plane a b c d` (ax + by + cz = d)

5. **Check plane equation**
   ```text
   # Horizontal plane at z=0
   below plane 0. 0. 1. 0.
   above plane 0. 0. 1. 0.

   # NOT
   below plane 0. 0. 0. 0.    # Wrong: normal vector can't be zero
   ```

**Prevention**:
- Start with box constraints (simplest)
- Test constraints with check keyword
- Visualize output after each run
- Read constraint documentation

### Atoms Too Close

**Symptom**: Output has overlapping atoms

**Causes**:
1. Tolerance too small
2. Radius values inappropriate
3. Input files have issues
4. Wrong atomic radii

**Solutions**:

1. **Check for overlaps**
   ```bash
   python scripts/check_overlaps.py output.pdb --tolerance 2.0
   ```

2. **Increase tolerance**
   ```text
   tolerance 2.5    # Was 2.0
   ```

3. **Set appropriate radii**
   ```text
   structure molecule.pdb
     number 100
     radius 1.5      # Larger atomic radius
     inside box 0. 0. 0. 30. 30. 30.
   end structure
   ```

4. **Verify input files**
   ```bash
   # Check for duplicate atoms
   grep "^ATOM" water.pdb | wc -l

   # Check coordinates
   less water.pdb
   ```

5. **Use verify script**
   ```bash
   python scripts/verify_success.py input.inp output.pdb
   ```

**Prevention**:
- Always check Packmol output for violation values
- Use appropriate tolerance for model type
- Validate input structure files

### Wrong Atom/Molecule Count

**Symptom**: Output has different count than expected

**Causes**:
1. Structure file has multiple molecules
2. CONECT records causing issues
3. Residue numbering problems
4. Misunderstanding of `number` parameter

**Solutions**:

1. **Check structure file**
   ```bash
   # Count molecules in PDB
   grep "^ATOM" molecule.pdb | wc -l

   # Check for multiple TER/END records
   grep -E "^TER|^END" molecule.pdb
   ```

2. **Verify single molecule per file**
   - Structure file should contain one molecule
   - Use one `number` parameter per structure block

3. **Check output statistics**
   ```bash
   # Count atoms in output
   grep "^ATOM" output.pdb | wc -l

   # Count residues
   grep "^ATOM" output.pdb | awk '{print $6}' | sort -u | wc -l
   ```

**Prevention**:
- Keep one molecule per structure file
- Understand `number` parameter means copies
- Verify structure files before use

### Density Issues

**Symptom**: System too dense or too dilute

**Causes**:
1. Wrong number of molecules
2. Incorrect box dimensions
3. Unit confusion

**Solutions**:

1. **Calculate density**
   ```bash
   python scripts/analyze_density.py output.pdb
   ```

2. **Adjust molecule count**
   - For water: 1 molecule ≈ 30 Å³ at 1 g/cm³
   - For 40×40×40 Å box: ~64,000 Å³ → ~2100 water molecules

3. **Calculate required molecules**
   ```
   N = (ρ × V) / (M / NA)
   ρ = density (g/cm³)
   V = volume (cm³)
   M = molecular weight (g/mol)
   NA = Avogadro's number
   ```

4. **Test density with small system**
   ```text
   # Test box
   tolerance 2.0
   output test.pdb
   filetype pdb

   structure water.pdb
     number 100
     inside box 0. 0. 0. 20. 20. 20.
   end structure
   ```

**Prevention**:
- Calculate approximate molecule count first
- Test with small systems
- Use density analysis scripts

### PBC Issues

**Symptom**: Problems with periodic boundary conditions

**Causes**:
1. PBC not set correctly
2. Box size mismatch
3. Wrong Packmol version

**Solutions**:

1. **Check Packmol version** (PBC requires 20.15.0+)
   ```bash
   packmol -h | head -5
   ```

2. **Set PBC correctly**
   ```text
   # Correct
   pbc 0. 0. 0. 40. 40. 60.

   # OR for orthorhombic at origin
   pbc 40. 40. 60.
   ```

3. **Match box constraints to PBC**
   ```text
   pbc 0. 0. 0. 40. 40. 60.

   structure water.pdb
     number 2000
     inside box 0. 0. 0. 40. 40. 60.  # Matches PBC
   end structure
   ```

4. **Update Packmol if needed**
   ```bash
   pip install --upgrade packmol
   ```

**Prevention**:
- Use Packmol 20.15.0 or later for PBC
- Ensure box constraints match PBC region
- Verify output has correct dimensions

### File Format Issues

**Symptom**: Packmol can't read structure files

**Causes**:
1. Wrong format
2. Missing required fields
3. Non-standard PDB format

**Solutions**:

1. **Verify PDB format**
   ```text
   ATOM      1  O   HOH     1       0.000   0.000   0.000  1.00  0.00
   1234567890123456789012345678901234567890123456789012345678901234567890
            ^^  ^   ^      ^^       ^^^^^^^^^^^^^^^^
            |   |   |      |        coordinates
            |   |   |      residue number
            |   |   residue name
            |   atom name
            element (columns 13-14)
   ```

2. **Check required columns**
   - Columns 1-6: "ATOM"
   - Columns 13-14: Element symbol
   - Columns 31-54: XYZ coordinates

3. **Fix element names**
   ```text
   # Wrong
   ATOM      1  CA  ALA     1       0.000   0.000   0.000

   # Right
   ATOM      1  CA  ALA     1       0.000   0.000   0.000
                      ^^
                   Right-justified element name
   ```

4. **Convert formats if needed**
   - Use Open Babel: `obabel -h input.xyz -opdb`
   - Use MDAnalysis
   - Use VMD/PyMOL

**Prevention**:
- Use standard PDB format
- Verify element columns (13-14)
- Test with simple molecule first

## Performance Issues

### Slow Optimization

**Symptom**: Packmol takes too long

**Causes**:
1. System too large
2. Small tolerance
3. Complex constraints
4. Too many molecule types

**Solutions**:

1. **Reduce system size**
   - Fewer molecules
   - Smaller box

2. **Increase tolerance**
   ```text
   tolerance 2.5    # Faster than 2.0
   ```

3. **Simplify constraints**
   - Use box instead of complex shapes
   - Reduce number of constraint types

4. **Adjust optimization parameters**
   ```text
   discale 1.5      # Faster convergence
   maxit 15         # Fewer iterations
   ```

5. **Use restart files** for very large systems

**Prevention**:
- Test with small systems
- Estimate runtime before large runs
- Use appropriate tolerance

### Memory Issues

**Symptom**: System swaps or becomes unresponsive

**Solutions**:

1. **Close other applications**
2. **Reduce system size**
3. **Use restart files**
4. **Run on machine with more RAM**

## Output Quality Issues

### High Objective Function Value

**Symptom**: Final objective function > 0.1

**Cause**: Packing not optimal

**Solutions**:

1. **Check violations in output**
   ```
   Maximum violation of target distance: X.XXX
   Maximum violation of the constraints: Y.YYY
   ```

2. **Rerun with different seed**
   ```text
   seed 54321    # Different random initial configuration
   ```

3. **Increase optimization effort**
   ```text
   maxit 50
   precision 0.001
   ```

4. **Accept if violations < 0.01**
   - Small violations are acceptable
   - MD equilibration will fix minor overlaps

### Gaps in Structure

**Symptom**: Empty spaces in output

**Causes**:
1. Tolerance too large
2. Not enough molecules
3. Constraint geometry

**Solutions**:

1. **Reduce tolerance**
   ```text
   tolerance 1.8
   ```

2. **Increase molecule count**
   ```text
   number 1200    # Was 1000
   ```

3. **Check density with script**
   ```bash
   python scripts/analyze_density.py output.pdb
   ```

## Getting Help

### Information to Provide

When asking for help, include:

1. **Complete input file**
2. **Error message** (full text)
3. **Packmol version**
   ```bash
   packmol -h | head -5
   ```
4. **System size** (number of atoms/molecules)
5. **What you've tried**

### Useful Commands

```bash
# Validate input
python scripts/validate_input.py input.inp

# Check overlaps
python scripts/check_overlaps.py output.pdb --tolerance 2.0

# Verify success
python scripts/verify_success.py input.inp output.pdb

# Analyze density
python scripts/analyze_density.py output.pdb

# Count atoms
grep "^ATOM" output.pdb | wc -l
```

### Resources

- [Packmol User Guide](https://m3g.github.io/packmol/userguide.shtml)
- [Packmol Examples](https://m3g.github.io/packmol/examples.shtml)
- [Packmol GitHub Issues](https://github.com/m3g/packmol/issues)

## Diagnostic Flowchart

```
System fails?
│
├─ "Killed" error?
│  └─→ Reduce system size or use restart files
│
├─ "No solution found"?
│  └─→ Reduce molecule count or increase region
│
├─ Won't converge?
│  └─→ Increase discale, maxit, or reduce complexity
│
├─ Wrong geometry?
│  └─→ Use check keyword, verify constraint syntax
│
├─ Overlaps in output?
│  └─→ Increase tolerance, check radii
│
└─ Other?
   └─→ Validate input, test with minimal system
```

## Prevention Checklist

Before running large systems:

- [ ] Test with minimal system (10-50 molecules)
- [ ] Validate input file syntax
- [ ] Check constraint geometry with `check` keyword
- [ ] Calculate expected density
- [ ] Estimate memory requirements
- [ ] Set random seed for reproducibility
- [ ] Verify all structure files exist
- [ ] Check PDB format compliance
- [ ] Document your input parameters

## Related Topics

- [Parameters reference](parameters.md) - Parameter details and defaults
- [Constraints reference](constraints.md) - Constraint syntax and examples
- [File formats](file_formats.md) - Input file requirements

For more help:
- Main skill documentation: [SKILL.md](../SKILL.md)
- Example files: [examples/](../examples/)
