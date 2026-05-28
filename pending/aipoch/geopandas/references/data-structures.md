# GeoPandas Data Structures

## GeoSeries

A GeoSeries is a vector where each entry is a set of shapes corresponding to an observation (similar to a pandas Series, but containing geometric data).

```python
import geopandas as gpd
from shapely.geometry import Point, Polygon

# Create a GeoSeries from geometric objects
points = gpd.GeoSeries([Point(1, 1), Point(2, 2), Point(3, 3)])

# Access geometric properties
points.area
points.length
points.bounds
```

## GeoDataFrame

A GeoDataFrame is a tabular data structure that contains a GeoSeries (similar to a pandas DataFrame, but containing geographic data).

```python
# Create from a dictionary
gdf = gpd.GeoDataFrame({
    'name': ['Point A', 'Point B'],
    'value': [100, 200],
    'geometry': [Point(1, 1), Point(2, 2)]
})

# Create from a pandas DataFrame with coordinates
import pandas as pd
df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3], 'name': ['A', 'B', 'C']})
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
```

## Key Attributes

- **geometry**: The currently active geometry column (can have multiple geometry columns)
- **crs**: Coordinate Reference System
- **bounds**: Bounding boxes of all geometric objects
- **total_bounds**: Overall bounding box

## Setting the Active Geometry Column

When a GeoDataFrame has multiple geometry columns:

```python
# Set the active geometry column
gdf = gdf.set_geometry('other_geom_column')

# Check the name of the currently active geometry column
gdf.geometry.name
```

## Indexing and Selection

Use standard pandas indexing methods for spatial data:

```python
# Select by label
gdf.loc[0]

# Boolean indexing
large_areas = gdf[gdf.area > 100]

# Select columns
gdf[['name', 'geometry']]
```