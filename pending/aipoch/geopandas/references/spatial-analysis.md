# Spatial Analysis

## Attribute Joins

Use standard pandas merge to combine datasets based on common variables:

```python
# Merge based on a common column
result = gdf.merge(df, on='common_column')

# Left join
result = gdf.merge(df, on='common_column', how='left')

# Important: Call merge on the GeoDataFrame to preserve geometry
# This works: gdf.merge(df, ...)
# This does not work: df.merge(gdf, ...) # Returns a DataFrame, not a GeoDataFrame
```

## Spatial Joins

Combine datasets based on spatial relationships.

### Binary Predicate Joins (sjoin)

Join based on geometric predicates:

```python
# Intersects (default)
joined = gpd.sjoin(gdf1, gdf2, how='inner', predicate='intersects')

# Available predicates
joined = gpd.sjoin(gdf1, gdf2, predicate='contains')
joined = gpd.sjoin(gdf1, gdf2, predicate='within')
joined = gpd.sjoin(gdf1, gdf2, predicate='touches')
joined = gpd.sjoin(gdf1, gdf2, predicate='crosses')
joined = gpd.sjoin(gdf1, gdf2, predicate='overlaps')

# Join types
joined = gpd.sjoin(gdf1, gdf2, how='left')   # Keep all records from the left
joined = gpd.sjoin(gdf1, gdf2, how='right')  # Keep all records from the right
joined = gpd.sjoin(gdf1, gdf2, how='inner')  # Keep only the intersection
```

The `how` parameter determines which geometries are kept:
- **left**: Keep the index and geometry of the left GeoDataFrame
- **right**: Keep the index and geometry of the right GeoDataFrame
- **inner**: Use the intersection of indices, keep the left geometry

### Nearest Neighbor Joins (sjoin_nearest)

Join to the nearest features:

```python
# Find nearest neighbors
nearest = gpd.sjoin_nearest(gdf1, gdf2)

# Add a distance column
nearest = gpd.sjoin_nearest(gdf1, gdf2, distance_col='distance')

# Limit search radius (significantly improves performance)
nearest = gpd.sjoin_nearest(gdf1, gdf2, max_distance=1000)

# Find k nearest neighbors
nearest = gpd.sjoin_nearest(gdf1, gdf2, k=5)
```

## Overlay Operations

Set-theoretic operations combining geometries from two GeoDataFrames:

```python
# Intersection - Keep areas where both overlap
intersection = gpd.overlay(gdf1, gdf2, how='intersection')

# Union - Combine all areas
union = gpd.overlay(gdf1, gdf2, how='union')

# Difference - Areas present in the first but not the second
difference = gpd.overlay(gdf1, gdf2, how='difference')

# Symmetric difference - Areas present in either but not both
sym_diff = gpd.overlay(gdf1, gdf2, how='symmetric_difference')

# Identity - Intersection + Difference
identity = gpd.overlay(gdf1, gdf2, how='identity')
```

Results contain attributes from both input GeoDataFrames.

## Dissolve / Aggregation

Aggregate geometries based on attribute values:

```python
# Dissolve by attribute
dissolved = gdf.dissolve(by='region')

# Dissolve with aggregation functions
dissolved = gdf.dissolve(by='region', aggfunc='sum')
dissolved = gdf.dissolve(by='region', aggfunc={'population': 'sum', 'area': 'mean'})

# Dissolve all shapes into a single geometry
dissolved = gdf.dissolve()

# Keep internal boundaries
dissolved = gdf.dissolve(by='region', as_index=False)
```

## Clipping

Clip geometries to the boundary of another geometry:

```python
# Clip to polygon boundary
clipped = gpd.clip(gdf, boundary_polygon)

# Clip to another GeoDataFrame
clipped = gpd.clip(gdf, boundary_gdf)
```

## Appending

Combine multiple GeoDataFrames:

```python
import pandas as pd

# Concatenate GeoDataFrames (CRS must match)
combined = pd.concat([gdf1, gdf2], ignore_index=True)

# Use keys for identification
combined = pd.concat([gdf1, gdf2], keys=['source1', 'source2'])
```

## Spatial Indexing

Improve performance of spatial operations:

```python
# GeoPandas automatically uses spatial indexing in most operations
# Access spatial index directly
sindex = gdf.sindex

# Query geometries intersecting with a bounding box
possible_matches_index = list(sindex.intersection((xmin, ymin, xmax, ymax)))
possible_matches = gdf.iloc[possible_matches_index]

# Query geometries intersecting with a polygon
possible_matches_index = list(sindex.query(polygon_geometry))
possible_matches = gdf.iloc[possible_matches_index]
```

Spatial indexing can significantly speed up:
- Spatial joins
- Overlay operations
- Queries with geometric predicates

## Distance Calculations

```python
# Distance between geometries
distances = gdf1.geometry.distance(gdf2.geometry)

# Distance to a single geometry
distances = gdf.geometry.distance(single_point)

# Minimum distance to any feature
min_dist = gdf.geometry.distance(point).min()
```

## Area and Length Calculations

To ensure accurate measurements, use an appropriate CRS:

```python
# Reproject to an appropriate projected CRS for area/length calculations
gdf_projected = gdf.to_crs(epsg=3857)  # or a suitable UTM zone

# Calculate area (in CRS units, usually square meters)
areas = gdf_projected.geometry.area

# Calculate length/perimeter (in CRS units)
lengths = gdf_projected.geometry.length
```