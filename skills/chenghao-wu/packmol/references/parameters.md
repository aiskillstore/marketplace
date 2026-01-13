# Packmol Parameters Reference

Complete guide to all input parameters in Packmol for controlling packing behavior and optimization.

## Overview

Packmol input files consist of:
1. **Global parameters** (file-level)
2. **Structure blocks** with per-molecule parameters
3. **Optimization parameters** (optional)

## Required Parameters

Three parameters are required in every Packmol input file:

### tolerance

Minimum allowed distance between atoms of different molecules.

**Syntax**: `tolerance <distance>`

**Units**: Angstroms (Å)

**Default**: None (required)

**Typical values**:
- `2.0` - All-atom models
- `2.5-3.0` - United-atom models
- `3.0-5.0` - Coarse-grained models
- `1.5-1.8` - Precise packing (slower)

**Example**:
```text
tolerance 2.0
```

**Notes**:
- Smaller values = tighter packing but longer optimization
- Larger values = faster but more void space
- Critical for preventing overlaps
- Adjust based on atomic radii in your system

### output

Output filename for the packed structure.

**Syntax**: `output <filename>`

**Default**: None (required)

**Example**:
```text
output system.pdb
```

**Notes**:
- File extension determines format (.pdb, .xyz)
- Overwrites existing files without warning
- Format must match `filetype` parameter

### filetype

Format of input and output structure files.

**Syntax**: `filetype <format>`

**Options**:
- `pdb` - Protein Data Bank format (default)
- `xyz` - XYZ Cartesian coordinates
- `tinker` - TINKER molecular mechanics format

**Example**:
```text
filetype pdb
```

**See**: [file_formats.md](file_formats.md) for format specifications

## Global Optional Parameters

### pbc

Periodic boundary conditions for the system.

**Syntax**:
```text
pbc xmin ymin zmin xmax ymax zmax
```
or
```text
pbc a b c  # for orthorhombic box
```

**Parameters**:
- `xmin ymin zmin`: Minimum box coordinates
- `xmax ymax zmax`: Maximum box coordinates
- OR `a b c`: Box lengths for orthorhombic box starting at origin

**Example**:
```text
pbc 0. 0. 0. 40. 40. 60.
```
or
```text
pbc 40. 40. 60.
```

**Notes**:
- Required for periodic MD simulations
- Molecules can wrap across boundaries
- Constraint `inside box` is typically set to PBC region
- Supported in Packmol 20.15.0 and later

### seed

Random seed for reproducible results.

**Syntax**: `seed <integer>`

**Default**: `12345` (fixed seed)

**Values**:
- Positive integer: Use as seed
- `-1`: Use system time (non-reproducible)

**Example**:
```text
seed 12345
```

**Notes**:
- Critical for reproducibility
- Same seed + same input = identical output
- Use `-1` for different random configurations

### discale

Distance tolerance scaling factor for optimization.

**Syntax**: `discale <factor>`

**Default**: `1.0`

**Range**: `1.0` to `2.0`

**Example**:
```text
discale 1.5
```

**Notes**:
- Increases effective tolerance during optimization
- Helps with difficult convergence
- Higher values = faster convergence but less precise packing
- Try `1.5` if packing fails to converge

### maxit

Maximum number of optimization iterations per loop.

**Syntax**: `maxit <N>`

**Default**: `20`

**Example**:
```text
maxit 50
```

**Notes**:
- Increase for difficult systems
- Trade-off: more iterations vs. computation time
- Convergence typically occurs before `maxit`

### precision

Solution precision for convergence.

**Syntax**: `precision <value>`

**Default**: `0.01`

**Units**: Fraction of tolerance

**Example**:
```text
precision 0.001
```

**Notes**:
- Smaller values = tighter convergence
- Typical range: 0.001 to 0.1
- Too small may prevent convergence

### nloop

Number of optimization loops.

**Syntax**: `nloop <N>`

**Default**: Automatic (varies by system)

**Example**:
```text
nloop 5
```

**Notes**:
- Controls optimization strategy
- Usually automatic is best
- Modify only for special cases

### sidemax

Maximum system size for optimization.

**Syntax**: `sidemax <value>`

**Default**: Automatic

**Units**: Angstroms (Å)

**Example**:
```text
sidemax 100.
```

**Notes**:
- Limits search region during optimization
- Larger values = slower but more thorough
- Usually automatic is sufficient

## Structure Block Parameters

### number

Number of molecules of this type to place.

**Syntax**: `number <N>`

**Required**: Yes (within each structure block)

**Example**:
```text
structure water.pdb
  number 1000
  inside box 0. 0. 0. 40. 40. 40.
end structure
```

### radius

Atomic radius for overlap detection.

**Syntax**: `radius <value>`

**Default**: `1.0` (multiplied by `discale`)

**Units**: Angstroms (Å)

**Example**:
```text
structure molecule.pdb
  number 100
  radius 1.5
  inside box 0. 0. 0. 30. 30. 30.
end structure
```

**Atom-specific radii**:
```text
structure molecule.pdb
  number 100
  atoms 1 2
    radius 1.5
  end atoms
  atoms 3 4 5
    radius 1.0
  end atoms
end structure
```

**Notes**:
- Useful for multiscale models
- Larger radius = more spacing
- Can vary per atom for coarse-graining

### resnumbers

Residue numbering strategy.

**Syntax**: `resnumbers <scheme>`

**Options**:
- `0` - Sequential numbering across all molecules (default)
- `1` - Each molecule gets same residue numbers as input
- `2` - Residue numbers increment per molecule
- `3` - Residue numbers increment by chain

**Example**:
```text
structure protein.pdb
  number 1
  resnumbers 1
  fixed 0. 0. 0. 0. 0. 0.
end structure

structure water.pdb
  number 1000
  resnumbers 2
  inside box 0. 0. 0. 40. 40. 40.
end structure
```

**Notes**:
- Important for MD software compatibility
- Option 0: All waters numbered sequentially
- Option 2: Each water molecule numbered separately

### chain

Chain identifier for molecules.

**Syntax**: `chain <letter>`

**Example**:
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

**Notes**:
- Single character (A-Z, 0-9)
- Useful for organizing output
- Required by some MD packages

### center

Use center of mass for positioning.

**Syntax**: `center`

**Used with**: `fixed` constraint

**Example**:
```text
structure protein.pdb
  number 1
  fixed 20. 20. 20. 0. 0. 0.
  center
end structure
```

**Notes**:
- Places molecule center at specified coordinates
- Without `center`, uses first atom position
- Essential for solvating biomolecules

## Optimization Parameters (Per Structure)

### movefrac

Fraction of molecules to displace during heuristic optimization.

**Syntax**: `movefrac <value>`

**Default**: `0.05` (5% of molecules)

**Range**: `0.0` to `1.0`

**Example**:
```text
structure water.pdb
  number 1000
  inside box 0. 0. 0. 40. 40. 40.
  movefrac 0.1
end structure
```

**Notes**:
- Higher values = more aggressive optimization
- Can help escape local minima
- Too high may slow convergence

### maxmove

Maximum number of molecules to displace.

**Syntax**: `maxmove <N>`

**Default**: Dynamic

**Example**:
```text
structure water.pdb
  number 5000
  inside box 0. 0. 0. 50. 50. 50.
  maxmove 100
end structure
```

**Notes**:
- Limits number of molecules moved per iteration
- Useful for very large systems
- Works with `movefrac`

### disable_movebad

Disable the move-bad heuristic.

**Syntax**: `disable_movebad`

**Default**: Disabled (move-bad heuristic is active)

**Example**:
```text
structure molecule.pdb
  number 100
  inside box 0. 0. 0. 30. 30. 30.
  disable_movebad
end structure
```

**Notes**:
- Move-bad heuristic repositions overlapping molecules
- Disable only if causing problems
- Usually best left enabled

## Rotation Constraints

### constrain_rotation

Limit molecular rotation during packing.

**Syntax**: `constrain_rotation <axis> <range> <increment>`

**Parameters**:
- `axis`: x, y, or z
- `range`: Rotation range in degrees (typically 180)
- `increment`: Sampling step in degrees

**Example**: Constrain rotation around all axes
```text
structure lipid.pdb
  number 100
  inside box 0. 0. 0. 40. 40. 40.
  constrain_rotation x 180. 20.
  constrain_rotation y 180. 20.
  constrain_rotation z 180. 20.
end structure
```

**Example**: Restrict to specific orientation
```text
structure molecule.pdb
  number 50
  inside box 0. 0. 0. 30. 30. 30.
  constrain_rotation z 0. 10.
end structure
```

**Notes**:
- Smaller increment = more orientations tested (slower)
- Useful for anisotropic molecules (lipids, surfactants)
- Range of 180° samples all unique orientations

## Restart Parameters

### restart_to

Save molecular positions to a restart file.

**Syntax**: `restart_to <filename>`

**Example**: Stage 1 - Place lipids
```text
structure lipid.pdb
  number 500
  inside box 0. 0. 0. 50. 50. 50.
  restart_to lipids.pack
end structure
```

### restart_from

Load molecular positions from a restart file.

**Syntax**: `restart_from <filename>`

**Example**: Stage 2 - Add water around fixed lipids
```text
structure lipid.pdb
  number 500
  restart_from lipids.pack
  fixed 0. 0. 0. 0. 0. 0.
end structure

structure water.pdb
  number 5000
  inside box 0. 0. 0. 50. 50. 50.
end structure
```

**Notes**:
- Build large systems incrementally
- Saves time by reusing previous results
- Critical for multi-stage packing

## Output Options

### writecrd

Write additional coordinate file in CHARMM format.

**Syntax**: `writecrd <filename>`

**Example**:
```text
writecrd system.crd
```

### add_amber_ter

Add TER cards for AMBER compatibility.

**Syntax**: `add_amber_ter`

**Example**:
```text
structure protein.pdb
  number 1
  fixed 0. 0. 0. 0. 0. 0.
  add_amber_ter
end structure
```

### add_box_sides

Add box vectors for GROMACS compatibility.

**Syntax**: `add_box_sides`

**Example**: Automatically adds CRYST1 record

## Advanced Parameters

### fbins

Number of bins for finite-distance calculation.

**Syntax**: `fbins <N>`

**Default**: Automatic

**Example**:
```text
fbins 100
```

**Notes**:
- Affects optimization algorithm
- Usually automatic is best
- Modify only for special cases

### short_tol

Short-distance tolerance.

**Syntax**: `short_tol <value>`

**Default**: Automatic

**Example**:
```text
short_tol 0.1
```

**Notes**:
- Used for overlap detection
- Affects optimization precision
- Usually automatic is sufficient

## Parameter Combinations

### Basic System

```text
tolerance 2.0
filetype pdb
output system.pdb

structure water.pdb
  number 1000
  inside box 0. 0. 0. 40. 40. 40.
end structure
```

### Solvated Protein

```text
tolerance 2.0
filetype pdb
output solvated.pdb
seed 12345

structure protein.pdb
  number 1
  fixed 20. 20. 20. 0. 0. 0.
  center
  chain A
  resnumbers 1
end structure

structure water.pdb
  number 5000
  inside box 0. 0. 0. 50. 50. 50.
  chain W
  resnumbers 2
end structure
```

### Difficult Convergence

```text
tolerance 2.0
filetype pdb
output system.pdb
discale 1.5
maxit 50
precision 0.001

structure molecule.pdb
  number 100
  inside box 0. 0. 0. 30. 30. 30.
  movefrac 0.1
end structure
```

### Periodic System

```text
tolerance 2.0
filetype pdb
output periodic.pdb
pbc 0. 0. 0. 40. 40. 60.

structure water.pdb
  number 2000
  inside box 0. 0. 0. 40. 40. 60.
end structure
```

### Multi-Stage Packing

**Stage 1**:
```text
tolerance 2.0
filetype pdb
output stage1.pdb

structure lipid.pdb
  number 500
  inside box 0. 0. 0. 50. 50. 50.
  restart_to lipids.pack
end structure
```

**Stage 2**:
```text
tolerance 2.0
filetype pdb
output stage2.pdb

structure lipid.pdb
  number 500
  restart_from lipids.pack
  fixed 0. 0. 0. 0. 0. 0.
end structure

structure water.pdb
  number 5000
  inside box 0. 0. 0. 50. 50. 50.
end structure
```

## Parameter Selection Guide

### For Quick Tests
- `tolerance`: 2.5-3.0
- `maxit`: 10
- Small system sizes

### For Production Runs
- `tolerance`: 2.0 (all-atom) or 2.5 (united-atom)
- `seed`: Fixed value for reproducibility
- `maxit`: Default (20)
- Add `pbc` for periodic systems

### For Difficult Systems
- `discale`: 1.5
- `maxit`: 50
- `movefrac`: 0.1
- Consider restart files

### For Coarse-Grained Models
- `tolerance`: 3.0-5.0
- `radius`: Larger values per bead type
- Fewer molecules due to larger effective size

## Troubleshooting Parameters

### System Won't Converge

1. Increase `discale` to 1.5
2. Increase `maxit` to 50
3. Reduce `number` of molecules
4. Increase `tolerance` slightly

### Too Many Overlaps

1. Check `tolerance` is appropriate
2. Verify `radius` values
3. Reduce system size
4. Use `check` keyword

### Wrong Density

1. Adjust `number` of molecules
2. Verify box dimensions
3. Check structure file integrity

### Non-Reproducible Results

1. Set fixed `seed` value
2. Ensure identical input files
3. Check for randomness in other tools

## Related Topics

- [Constraints reference](constraints.md) - Spatial constraint syntax
- [File formats](file_formats.md) - Input/output format specifications
- [Troubleshooting](troubleshooting.md) - Common parameter issues

For parameter examples in context, see:
- [examples/basic/](../examples/basic/) - Simple parameter sets
- [examples/solvation/](../examples/solvation/) - Solvation parameters
- [examples/advanced/](../examples/advanced/) - Advanced parameter usage
