# Coordinate Reference Systems (CRS)

Coordinate Reference Systems define how coordinates relate to locations on Earth.

## Understanding CRS

CRS information is stored as `pyproj.CRS` objects:

```python
# Check CRS
print(gdf.crs)

# Check if a CRS is set
if gdf.crs is None:
    print("No CRS defined")
```

## Setting and Reprojecting

### Setting a CRS

When coordinates are correct but CRS metadata is missing, use `set_crs()`:

```python
# Set CRS (does not transform coordinates)
gdf = gdf.set_crs("EPSG:4326")
gdf = gdf.set_crs(4326)
```

**Warning**: Use only when CRS metadata is missing. This operation does not transform coordinates.

### Reprojecting

Use `to_crs()` to transform coordinates between coordinate systems:

```python
# Reproject to a different CRS
gdf_projected = gdf.to_crs("EPSG:3857")  # Web Mercator
gdf_projected = gdf.to_crs(3857)

# Reproject to match another GeoDataFrame
gdf1_reprojected = gdf1.to_crs(gdf2.crs)
```

## CRS Formats

GeoPandas accepts multiple formats via `pyproj.CRS.from_user_input()`:

```python
# EPSG code (integer)
gdf.to_crs(4326)

# Authority string
gdf.to_crs("EPSG:4326")
gdf.to_crs("ESRI:102003")

# WKT string (Well-Known Text)
gdf.to_crs("GEOGCS[...]")

# PROJ string
gdf.to_crs("+proj=longlat +datum=WGS84")

# pyproj.CRS object
from pyproj import CRS
crs_obj = CRS.from_epsg(4326)
gdf.to_crs(crs_obj)
```

**Best Practice**: Use WKT2 or authority strings (EPSG) to preserve full CRS information.

## Common EPSG Codes

### Geographic Coordinate Systems

```python
# WGS 84 (longitude/latitude)
gdf.to_crs("EPSG:4326")

# NAD83
gdf.to_crs("EPSG:4269")
```

### Projected Coordinate Systems

```python
# Web Mercator (used for web maps)
gdf.to_crs("EPSG:3857")

# UTM Zone (Example: UTM Zone 33N)
gdf.to_crs("EPSG:32633")

# UTM Zone (Southern Hemisphere, Example: UTM Zone 33S)
gdf.to_crs("EPSG:32733")

# US National Atlas Equal Area
gdf.to_crs("ESRI:102003")

# Albers Equal Area Conic (North America)
gdf.to_crs("EPSG:5070")
```

## CRS Requirements for Operations

### Operations requiring matching CRS

The following operations require CRS to be exactly the same:

```python
# Spatial join
gpd.sjoin(gdf1, gdf2, ...)  # CRS must match

# Overlay operations
gpd.overlay(gdf1, gdf2, ...)  # CRS must match

# Concatenation/Merging
pd.concat([gdf1, gdf2])  # CRS must match

# Reproject first if necessary
gdf2_reprojected = gdf2.to_crs(gdf1.crs)
result = gpd.sjoin(gdf1, gdf2_reprojected)
```

### Operations best performed in a projected CRS

Area and distance calculations should use a projected CRS:

```python
# Wrong way: Area in degrees (meaningless)
areas_degrees = gdf.geometry.area  # If CRS is EPSG:4326

# Correct way: Reproject to a suitable projected CRS first
gdf_projected = gdf.to_crs("EPSG:3857")
areas_meters = gdf_projected.geometry.area  # Square meters

# Better way: Use a suitable local UTM zone for accuracy
gdf_utm = gdf.to_crs("EPSG:32633")  # UTM Zone 33N
accurate_areas = gdf_utm.geometry.area
```

## Choosing the Right CRS

### For area/distance calculations

Use equal-area projections:

```python
# Albers Equal Area Conic (North America)
gdf.to_crs("EPSG:5070")

# Lambert Azimuthal Equal Area
gdf.to_crs("EPSG:3035")  # Europe

# UTM Zone (for local areas)
gdf.to_crs("EPSG:32633")  # Corresponding UTM zone
```

### For preserving distance (navigation)

Use equidistant projections:

```python
# Azimuthal Equidistant
gdf.to_crs("ESRI:54032")
```

### For preserving shape (angles)

Use conformal projections:

```python
# Web Mercator (conformal, but distorts area)
gdf.to_crs("EPSG:3857")

# UTM Zone (conformal projection for local areas)
gdf.to_crs("EPSG:32633")
```

### For web maps

```python
# Web Mercator (standard for web maps)
gdf.to_crs("EPSG:3857")
```

## Estimating UTM Zones

```python
# Estimate a suitable UTM CRS based on the data
utm_crs = gdf.estimate_utm_crs()
gdf_utm = gdf.to_crs(utm_crs)
```

## Multiple Geometry Columns with Different CRS

GeoPandas 0.8+ supports different CRS for each geometry column:

```python
# Set CRS for a specific geometry column
gdf = gdf.set_crs("EPSG:4326", allow_override=True)

# The active geometry column determines operation behavior
gdf = gdf.set_geometry('other_geom_column')

# Check for CRS mismatch
try:
    result = gdf1.overlay(gdf2)
except ValueError as e:
    print("CRS mismatch:", e)
```

## Querying CRS Information

```python
# Get full CRS details
print(gdf.crs)

# Get EPSG code (if available)
print(gdf.crs.to_epsg())

# Get WKT representation
print(gdf.crs.to_wkt())

# Get PROJ string
print(gdf.crs.to_proj4())

# Check if CRS is geographic (lat/lon)
print(gdf.crs.is_geographic)

# Check if CRS is projected
print(gdf.crs.is_projected)
```

## Transforming Individual Geometries

```python
from pyproj import Transformer

# Create a transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

# Transform point coordinates
x_new, y_new = transformer.transform(x, y)
```