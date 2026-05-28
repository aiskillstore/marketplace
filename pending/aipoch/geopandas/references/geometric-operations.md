# Geometric Operations

GeoPandas provides extensive geometric processing capabilities by integrating Shapely.

## Constructive Operations

Create new geometries from existing ones:

### Buffer

Create a geometry representing all points within a specific distance:

```python
# Buffer by a fixed distance
buffered = gdf.geometry.buffer(10)

# Negative buffer (erosion)
eroded = gdf.geometry.buffer(-5)

# Buffer with resolution parameter
smooth_buffer = gdf.geometry.buffer(10, resolution=16)
```

### Boundary

Get the lower-dimensional boundary:

```python
# Polygon -> LineString, LineString -> MultiPoint
boundaries = gdf.geometry.boundary
```

### Centroid

Get the center point of each geometry:

```python
centroids = gdf.geometry.centroid
```

### Convex Hull

The smallest convex polygon that contains all points:

```python
hulls = gdf.geometry.convex_hull
```

### Concave Hull

The smallest concave polygon that contains all points:

```python
# The ratio parameter controls concavity (0 = convex hull, 1 = maximum concavity)
concave_hulls = gdf.geometry.concave_hull(ratio=0.5)
```

### Envelope

Minimum axis-aligned rectangle:

```python
envelopes = gdf.geometry.envelope
```

### Simplify

Reduce geometric complexity:

```python
# Use Douglas-Peucker algorithm with a tolerance parameter
simplified = gdf.geometry.simplify(tolerance=10)

# Preserve topology (prevent self-intersection)
simplified = gdf.geometry.simplify(tolerance=10, preserve_topology=True)
```

### Segmentize

Add vertices to existing line segments:

```python
# Add vertices based on maximum segment length
segmented = gdf.geometry.segmentize(max_segment_length=5)
```

### Union All

Combine all geometries into a single geometry:

```python
# Merge all features
unified = gdf.geometry.union_all()
```

## Affine Transformations

Mathematical transformations of coordinates:

### Rotate

```python
# Rotate around the origin (0, 0) in degrees
rotated = gdf.geometry.rotate(angle=45, origin='center')

# Rotate around a custom point
rotated = gdf.geometry.rotate(angle=45, origin=(100, 100))
```

### Scale

```python
# Uniform scaling
scaled = gdf.geometry.scale(xfact=2.0, yfact=2.0)

# Scale specifying an origin
scaled = gdf.geometry.scale(xfact=2.0, yfact=2.0, origin='center')
```

### Translate

```python
# Offset coordinates
translated = gdf.geometry.translate(xoff=100, yoff=50)
```

### Skew

```python
# Shear transformation
skewed = gdf.geometry.skew(xs=15, ys=0, origin='center')
```

### Custom Affine Transform

```python
from shapely import affinity

# Apply a 6-parameter affine transformation matrix
# [a, b, d, e, xoff, yoff]
transformed = gdf.geometry.affine_transform([1, 0, 0, 1, 100, 50])
```

## Geometric Properties

Access geometric properties (returns a pandas Series):

```python
# Area
areas = gdf.geometry.area

# Length/Perimeter
lengths = gdf.geometry.length

# Bounding box coordinates
bounds = gdf.geometry.bounds  # Returns a DataFrame containing minx, miny, maxx, maxy

# Total bounds of the entire GeoSeries
total_bounds = gdf.geometry.total_bounds  # Returns an array [minx, miny, maxx, maxy]

# Check geometry type
geom_types = gdf.geometry.geom_type

# Check if valid
is_valid = gdf.geometry.is_valid

# Check if empty
is_empty = gdf.geometry.is_empty
```

## Geometric Relationships

Binary predicates for testing relationships:

```python
# Within
gdf1.geometry.within(gdf2.geometry)

# Contains
gdf1.geometry.contains(gdf2.geometry)

# Intersects
gdf1.geometry.intersects(gdf2.geometry)

# Touches
gdf1.geometry.touches(gdf2.geometry)

# Crosses
gdf1.geometry.crosses(gdf2.geometry)

# Overlaps
gdf1.geometry.overlaps(gdf2.geometry)

# Covers
gdf1.geometry.covers(gdf2.geometry)

# Covered by
gdf1.geometry.covered_by(gdf2.geometry)
```

## Point Extraction

Extract specific points from geometries:

```python
# Representative point (guaranteed to be inside the geometry)
rep_points = gdf.geometry.representative_point()

# Interpolate points at a specified distance along a line
points = line_gdf.geometry.interpolate(distance=10)

# Interpolate points at a normalized distance (0 to 1)
midpoints = line_gdf.geometry.interpolate(distance=0.5, normalized=True)
```

## Delaunay Triangulation

```python
# Create triangulation
triangles = gdf.geometry.delaunay_triangles()
```