# Interface Examples

Examples for creating liquid-liquid and liquid-vapor interfaces using plane constraints.

## Examples

### liquid_liquid.inp

**Purpose**: Create a water/chloroform liquid-liquid interface

**Description**: Builds two immiscible liquid phases with a planar interface, commonly used to study partitioning, solvation, and interfacial phenomena.

**Use case**:
- Partition coefficient calculations
- Interfacial tension studies
- Surfactant behavior at interfaces
- Solvent extraction systems

**System setup**:
- Water phase: 1000 molecules (z < 0)
- Chloroform phase: 200 molecules (z > 0)
- Interface: Horizontal plane at z = 0
- Periodic boundaries: 40 × 40 × 60 Å box

**Requirements**:
- `water.pdb` - Single water molecule
- `chloroform.pdb` - Single chloroform molecule

**To run**:
```bash
packmol < liquid_liquid.inp
```

**Expected output**:
- `interface.pdb` with ~3600 atoms
- Clear interface at z = 0
- Water below, chloroform above

**Modifications**:

1. **Different solvent pairs**:
   ```text
   # Water/hexane
   structure water.pdb
     number 1000
     below plane 0. 0. 1. 0.
   end structure

   structure hexane.pdb
     number 200
     above plane 0. 0. 1. 0.
   end structure
   ```

2. **Add salt to aqueous phase**:
   ```text
   # Add below interface with water
   structure SOD.pdb
     number 10
     below plane 0. 0. 1. 0.
   end structure

   structure CLA.pdb
     number 10
     below plane 0. 0. 1. 0.
   end structure
   ```

3. **Adjust interface position**:
   ```text
   # Interface at z = 30 (in 60 Å box)
   structure water.pdb
     number 1000
     below plane 0. 0. 1. 30.
   end structure

   structure chloroform.pdb
     number 200
     above plane 0. 0. 1. 30.
   end structure
   ```

4. **Inclined interface**:
   ```text
   # 45° angle: plane z = -x
   structure water.pdb
     number 1000
     below plane 1. 0. 1. 0.
   end structure
   ```

**Tips**:
- Use periodic boundaries in all directions
- Make z-dimension 1.5-2× larger than x,y for stability
- Test with small systems first
- Verify interfacial area matches your needs

---

### benzene_water.inp

**Purpose**: Create a water/benzene liquid-liquid interface

**Description**: Builds an interface between water and benzene, a classic aromatic solvent system. Benzene is planar and non-polar, making it ideal for studying π-interactions, solvation of aromatic compounds, and interfacial behavior of non-polar solvents.

**Use case**:
- Aromatic solvent extraction studies
- Partitioning of organic compounds
- Interfacial tension of aromatic systems
- Benchmark for non-polar solvent simulations
- Studies of π-π interactions at interfaces

**System setup**:
- Water phase: 1000 molecules (z < 0)
- Benzene phase: 220 molecules (z > 0)
- Interface: Horizontal plane at z = 0
- Periodic boundaries: 40 × 40 × 60 Å box

**Requirements**:
- `water.pdb` - Single water molecule
- `benzene.pdb` - Single benzene molecule (C₆H₆)

**To run**:
```bash
packmol < benzene_water.inp
```

**Expected output**:
- `benzene_water.pdb` with ~5,640 atoms
- Clear interface at z = 0
- Water below, benzene above
- Planar benzene molecules randomly oriented

**Special considerations**:
- Benzene is planar - molecules may align parallel to interface
- Lower density than water (0.88 vs 1.0 g/cm³)
- All atoms coplanar in each benzene molecule
- Volume per benzene molecule: ~148 Å³

**Modifications**:

1. **Different aromatic solvents**:
   ```text
   # Water/toluene
   structure water.pdb
     number 1000
     below plane 0. 0. 1. 0.
   end structure

   structure toluene.pdb
     number 180
     above plane 0. 0. 1. 0.
   end structure
   ```

2. **Benzene orientation control** (for alignment studies):
   ```text
   # Keep benzene planar with interface
   structure benzene.pdb
     number 220
     above plane 0. 0. 1. 0.
     constrain rotation x 0. 10.
     constrain rotation y 0. 10.
   end structure
   ```

3. **Add solute at interface**:
   ```text
   # Place aromatic solute at interface
   structure phenol.pdb
     number 10
     inside box -10. -10. -2. 10. 10. 2.
   end structure
   ```

---

## Interface Theory

### Plane Equation

Plane constraints use the equation: `ax + by + cz = d`

**Parameters**:
- `(a, b, c)`: Normal vector to plane (doesn't need normalization)
- `d`: Distance from origin along normal

**Examples**:

1. **Horizontal plane at z = 0**:
   ```
   Plane: 0*x + 0*y + 1*z = 0
   Packmol: plane 0. 0. 1. 0.
   ```

2. **Horizontal plane at z = 10**:
   ```
   Plane: 0*x + 0*y + 1*z = 10
   Packmol: plane 0. 0. 1. 10.
   ```

3. **Vertical plane**:
   ```
   Plane: 1*x + 0*y + 0*z = 0 (yz plane at x=0)
   Packmol: plane 1. 0. 0. 0.
   ```

4. **45° inclined plane**:
   ```
   Plane: 1*x + 0*y + 1*z = 0 (z = -x)
   Packmol: plane 1. 0. 1. 0.
   ```

### Molecule Placement

- **below plane**: `ax + by + cz < d`
- **above plane**: `ax + by + cz > d`

### Periodic Box Setup

For interface centered in box:

```
Box: 40 × 40 × 60 Å
Interface: z = 30 (middle)

PBC: 0. 0. 0. 40. 40. 60.
     or: pbc 0. 0. 0. 40. 40. 60.

Phase 1 (below):  z < 30
Phase 2 (above):  z > 30
```

For symmetric interface at origin:

```
Box: -20 to 20 in x,y, -30 to 30 in z (40×40×60 Å)
Interface: z = 0

PBC: -20. -20. -30. 20. 20. 30.

Phase 1 (below):  z < 0 (30 Å region)
Phase 2 (above):  z > 0 (30 Å region)
```

---

## Common Interface Systems

### Water/Oil Interface

**Typical systems**:
- Water/hexane: Non-polar solvent
- Water/chloroform: Dense organic phase
- Water/octanol: Partition coefficient studies
- **Water/benzene**: Aromatic solvent (see benzene_water.inp example above)
  - Molecular structure: Planar C₆H₆ ring
  - Density: 0.88 g/cm³ (lighter than water)
  - Applications: Aromatic partitioning, π-interaction studies

**Example**: Water/octanol
```text
tolerance 2.0
filetype pdb
output water_octanol.pdb
pbc -20. -20. -30. 20. 20. 30.

structure water.pdb
  number 1000
  below plane 0. 0. 1. 0.
end structure

structure octanol.pdb
  number 150
  above plane 0. 0. 1. 0.
end structure
```

### Liquid/Vapor Interface

**Purpose**: Study surface tension, evaporation

**Setup**: Only one phase, vacuum above

```text
tolerance 2.0
filetype pdb
output liquid_vapor.pdb
pbc 0. 0. 0. 40. 40. 80.

structure water.pdb
  number 1000
  below plane 0. 0. 1. 40.    # All water at z < 40
  above plane 0. 0. 1. 10.    # But above z = 10 (slab)
end structure
```

**Note**: Creates vacuum region for z > 40

### Bilayer Systems

**Purpose**: Membrane simulations

**Setup**: Two interfaces with water on both sides

```text
tolerance 2.0
filetype pdb
output bilayer.pdb
pbc 0. 0. 0. 60. 60. 80.

# Lower leaflet (lipids oriented)
structure lipid.pdb
  number 200
  above plane 0. 0. 1. 25.
  below plane 0. 0. 1. 35.
  constrain_rotation x 0. 10.
  constrain_rotation y 0. 10.
end structure

# Water below membrane
structure water.pdb
  number 2000
  below plane 0. 0. 1. 25.
end structure

# Water above membrane
structure water.pdb
  number 2000
  above plane 0. 0. 1. 55.
end structure
```

---

## Density Calculations

### Estimating Molecule Count

For a liquid phase:

```
V = L × W × H (Å³)
N_molecules = V / V_per_molecule

For water at 1.0 g/cm³:
  V_per_molecule ≈ 30 Å³
  N = V / 30

For chloroform at 1.5 g/cm³:
  V_per_molecule = (MW / density) / NA
  MW = 119.38 g/mol
  density = 1.48 g/cm³
  V_per_molecule ≈ 134 Å³
  N = V / 134
```

**Example calculations**:

For 40×40×30 Å phase (48,000 Å³):
- Water: 48,000 / 30 ≈ 1600 molecules
- Chloroform: 48,000 / 134 ≈ 360 molecules

### Verifying Density

```bash
# Check density after packing
python scripts/analyze_density.py interface.pdb

# Should get ~1.0 g/cm³ for water
# and appropriate density for other solvent
```

---

## Common Issues

### Interface Mixing

**Symptom**: Molecules from different phases mix at interface

**Cause**: Natural - Packmol creates initial configuration, MD will equilibrate

**Solution**:
- Some initial mixing is OK
- MD equilibration will form proper interface
- Or use `constrain_rotation` for surfactants

### Wrong Phase Distribution

**Symptom**: Molecules on wrong side of interface

**Cause**: Plane equation error

**Solution**:
- Verify plane equation: `ax + by + cz = d`
- Test with 1-2 molecules first
- Use `check` keyword to validate

### Poor Interface Definition

**Symptom**: Interface not well-defined

**Cause**: Too few molecules or wrong density

**Solution**:
- Increase molecule count
- Verify densities with `analyze_density.py`
- Ensure adequate phase thickness (~15-20 Å minimum)

### PBC Artifacts

**Symptom**: Molecules interact across periodic boundaries

**Cause**: Box too small

**Solution**:
- Increase lateral dimensions (x, y)
- Keep z-dimension adequate for both phases
- Use vacuum padding if needed

---

## Tips for Interface Systems

1. **Start simple**: Test with small systems first
2. **Use PBC**: Essential for interface simulations
3. **Adequate thickness**: Each phase ≥ 15-20 Å
4. **Verify density**: Use `analyze_density.py`
5. **Consider equilibration**: Interface will form during MD
6. **Plan area**: Larger area = better statistics but slower
7. **Visualization**: Check interface in VMD/PyMOL

---

## Workflow

1. **Choose solvent pair**: Based on research question
2. **Calculate densities**: Estimate molecule counts
3. **Set up PBC box**: Appropriate dimensions
4. **Define plane**: Interface position and orientation
5. **Create input file**: Use template as starting point
6. **Validate**: `validate_input.py`
7. **Run Packmol**: `packmol < interface.inp`
8. **Verify**: Check interface formation, density
9. **Equilibrate**: Run MD to relax interface
10. **Production**: Your actual simulation

---

## For More Help

- Main skill: [SKILL.md](../../SKILL.md)
- Templates: [../../templates/](../../templates/)
- Constraints: [../../references/constraints.md](../../references/constraints.md)
- Troubleshooting: [../../references/troubleshooting.md](../../references/troubleshooting.md)
