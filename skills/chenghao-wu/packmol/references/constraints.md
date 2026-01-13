# Packmol Constraints Reference

Complete guide to spatial constraints in Packmol for defining molecular placement regions.

## Overview

Constraints define where molecules can be placed in 3D space. Each structure block must have at least one constraint. Constraints can be combined to create complex geometries.

## Constraint Syntax

Constraints are specified within structure blocks:

```text
structure molecule.pdb
  number 100
  <constraint>          # Required: where to place molecules
  [additional constraints]
  [parameters]
end structure
```

## Fixed Constraint

Fix a molecule at a specific position and orientation.

```text
fixed x y z a b c
```

**Parameters**:
- `x y z`: Translation (Å)
- `a b c`: Rotation angles in degrees around x, y, z axes

**Example**:
```text
structure protein.pdb
  number 1
  fixed 0. 0. 0. 0. 0. 0.
  center
end structure
```

**Use with**:
- `center`: Use center of mass for positioning
- Solvated biomolecules
- Multi-stage packing

## Box Constraints

### Inside Box

Place molecules within a rectangular region.

```text
inside box xmin ymin zmin xmax ymax zmax
```

**Parameters**:
- `xmin ymin zmin`: Minimum corner coordinates (Å)
- `xmax ymax zmax`: Maximum corner coordinates (Å)

**Example**:
```text
structure water.pdb
  number 1000
  inside box 0. 0. 0. 40. 40. 40.
end structure
```

### Outside Box

Place molecules outside a rectangular region.

```text
outside box xmin ymin zmin xmax ymax zmax
```

**Use case**: Create shells around solutes

**Example**:
```text
structure water.pdb
  number 1000
  outside box 10. 10. 10. 30. 30. 30.
end structure
```

## Cube Constraint

Shorthand for equal-sized boxes.

```text
inside cube xmin ymin zmin size
```

**Example**:
```text
structure water.pdb
  number 500
  inside cube 0. 0. 0. 40.
end structure
```

Equivalent to `inside box 0. 0. 0. 40. 40. 40.`

## Sphere Constraints

### Inside Sphere

Place molecules within a sphere.

```text
inside sphere xcenter ycenter zcenter radius
```

**Parameters**:
- `xcenter ycenter zcenter`: Sphere center coordinates (Å)
- `radius`: Sphere radius (Å)

**Example**: Create spherical water droplet
```text
structure water.pdb
  number 1000
  inside sphere 0. 0. 0. 20.
end structure
```

### Outside Sphere

Place molecules outside a sphere.

```text
outside sphere xcenter ycenter zcenter radius
```

**Example**: Create spherical shell
```text
structure water.pdb
  number 2000
  inside sphere 0. 0. 0. 30.
  atoms 1
    outside sphere 0. 0. 0. 20.
  end atoms
end structure
```

### Combining Inside/Outside Spheres

Create spherical shells or vesicles:

```text
# Vesicle: lipids in shell, water inside and outside
structure lipid.pdb
  number 500
  inside sphere 0. 0. 0. 30.
  atoms 1 2 3
    outside sphere 0. 0. 0. 25.
  end atoms
end structure

structure water.pdb
  number 500
  inside sphere 0. 0. 0. 25.
end structure
```

## Ellipsoid Constraints

### Inside Ellipsoid

```text
inside ellipsoid xc yc zc xa yb zc scale
```

**Parameters**:
- `xc yc zc`: Ellipsoid center
- `xa yb zc`: Semi-axes (a, b, c) before scaling
- `scale`: Scaling factor

**Equation**: `(x-xc)²/(xa·scale)² + (y-yc)²/(yb·scale)² + (z-zc)²/(zc·scale)² ≤ 1`

**Example**: Prolate ellipsoid
```text
structure water.pdb
  number 1000
  inside ellipsoid 0. 0. 0. 20. 20. 30. 1.0
end structure
```

### Outside Ellipsoid

```text
outside ellipsoid xc yc zc xa yb zc scale
```

## Cylinder Constraints

### Inside Cylinder

Place molecules within a cylinder.

```text
inside cylinder x1 y1 z1 dx dy dz radius length
```

**Parameters**:
- `x1 y1 z1`: Cylinder axis start point
- `dx dy dz`: Cylinder axis direction vector
- `radius`: Cylinder radius (Å)
- `length`: Cylinder length (Å)

**Example**: Vertical cylinder
```text
structure water.pdb
  number 500
  inside cylinder 0. 0. 0. 0. 0. 1. 15. 40.
end structure
```

**Example**: Nanotube/pore
```text
structure water.pdb
  number 1000
  inside cylinder 0. 0. 0. 1. 0. 0. 10. 50.
end structure
```

### Outside Cylinder

```text
outside cylinder x1 y1 z1 dx dy dz radius length
```

**Use case**: Create cylindrical pores or channels

## Plane Constraints

### Above Plane

Place molecules above (positive side of) a plane.

```text
above plane a b c d
```

**Plane equation**: `a·x + b·y + c·z = d`

**Parameters**:
- `a b c`: Normal vector (not necessarily normalized)
- `d`: Distance from origin

**Example**: Horizontal plane at z=0
```text
structure water.pdb
  number 1000
  above plane 0. 0. 1. 0.
end structure
```

**Example**: Inclined plane
```text
structure molecule.pdb
  number 500
  above plane 0. 1. 1. 0.
end structure
```

### Below Plane

Place molecules below (negative side of) a plane.

```text
below plane a b c d
```

**Example**: Liquid-liquid interface
```text
structure water.pdb
  number 1000
  below plane 0. 0. 1. 0.
end structure

structure oil.pdb
  number 200
  above plane 0. 0. 1. 0.
end structure
```

### Combining Plane Constraints

Create slabs or layers:

```text
# Water slab between z=-10 and z=10
structure water.pdb
  number 1000
  above plane 0. 0. 1. -10.
  below plane 0. 0. 1. 10.
end structure
```

## Gaussian Surface Constraint

```text
inside xygauss x0 y0 z0 sigma a0 b0 c0
```

Creates a Gaussian surface for density profiles.

**Use case**: Interface modeling with density gradients

## Combining Constraints

Multiple constraints can be combined using atom selection:

### Within Single Molecule

Apply different constraints to different atoms:

```text
structure surfactant.pdb
  number 100
  # Headgroup in water region
  atoms 1 2 3 4
    above plane 0. 0. 1. 0.
  end atoms
  # Tail in oil region
  atoms 5 6 7 8 9 10
    below plane 0. 0. 1. 0.
  end atoms
end structure
```

### Multiple Spatial Constraints

Combine inside/outside constraints:

```text
# Molecules in shell between two spheres
structure water.pdb
  number 1000
  inside sphere 0. 0. 0. 50.
  outside sphere 0. 0. 0. 40.
end structure
```

## Constraint Validation

Validate constraints without running full packing:

```text
structure molecule.pdb
  number 100
  inside box 0. 0. 0. 30. 30. 30.
  check
end structure
```

Output shows constraint validity without optimization.

## Common Constraint Patterns

### Solvation Shell

```text
# Water around protein
structure protein.pdb
  number 1
  fixed 0. 0. 0. 0. 0. 0.
  center
end structure

structure water.pdb
  number 5000
  inside box -15. -15. -15. 65. 65. 65.
end structure
```

### Micelle/Spherical Aggregate

```text
# Surfactants in sphere
structure surfactant.pdb
  number 200
  inside sphere 0. 0. 0. 25.
  atoms 1 2 3
    outside sphere 0. 0. 0. 15.
  end atoms
end structure
```

### Bilayer

```text
# Lipid bilayer with water
structure lipid.pdb
  number 500
  above plane 0. 0. 1. 0.
  below plane 0. 0. 1. 30.
  constrain_rotation x 0. 10.
  constrain_rotation y 0. 10.
end structure

structure water.pdb
  number 5000
  above plane 0. 0. 1. 30.
end structure

structure water.pdb
  number 5000
  below plane 0. 0. 1. -30.
end structure
```

### Nanotube with Solution

```text
# Water inside nanotube
structure water.pdb
  number 500
  inside cylinder 0. 0. 0. 0. 0. 1. 5. 40.
end structure

# Water outside nanotube
structure water.pdb
  number 5000
  outside cylinder 0. 0. 0. 0. 0. 1. 8. 50.
end structure
```

## Tips for Using Constraints

1. **Start simple**: Test with one constraint before combining
2. **Use check keyword**: Validate constraints before running full optimization
3. **Visualize**: Load constraint boundaries in VMD/PyMOL to verify
4. **Avoid conflicts**: Make sure constraint regions overlap properly
5. **Consider periodicity**: Use `pbc` with constraints for periodic systems
6. **Tolerance matters**: Ensure tolerance is smaller than constraint features

## Troubleshooting Constraints

### No Solution Found

- **Cause**: Constraint region too small for number of molecules
- **Solution**: Reduce molecule count or increase constraint region

### Unexpected Placements

- **Cause**: Conflicting or overlapping constraints
- **Solution**: Use `check` keyword to validate constraint geometry
- **Solution**: Visualize constraint boundaries

### Molecules Missing

- **Cause**: `outside` constraint removing molecules
- **Solution**: Ensure sufficient volume in valid region
- **Solution**: Check that `inside` and `outside` regions overlap correctly

## Advanced Constraint Features

### Atom Selection for Constraints

Apply constraints only to specific atoms within molecules:

```text
structure molecule.pdb
  number 100
  inside box 0. 0. 0. 30. 30. 30.
  atoms 1 2 3 4
    inside sphere 15. 15. 15. 10.
  end atoms
end structure
```

### Constrained Rotations

Control molecular orientation:

```text
structure molecule.pdb
  number 100
  inside box 0. 0. 0. 30. 30. 30.
  constrain_rotation x 180. 20.
  constrain_rotation y 180. 20.
end structure
```

Parameters: `constrain_rotation <axis> <range> <increment>`

- `axis`: x, y, or z
- `range`: Rotation range in degrees
- `increment`: Sampling increment

### Fixed Molecules in Multi-Stage Packing

Build complex systems incrementally:

**Stage 1**: Place lipids
```text
structure lipid.pdb
  number 500
  inside box 0. 0. 0. 50. 50. 50.
  restart_to lipids.pack
end structure
```

**Stage 2**: Add water
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

## Related Topics

- [Parameters reference](parameters.md) - Input parameters and optimization
- [File formats](file_formats.md) - Structure file requirements
- [Troubleshooting](troubleshooting.md) - Common constraint issues

For more examples, see:
- [examples/interface/](../examples/interface/) - Plane constraints
- [examples/advanced/](../examples/advanced/) - Complex geometries
