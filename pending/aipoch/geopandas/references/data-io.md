# Reading and Writing Spatial Data

## Reading Files

Use `geopandas.read_file()` to import vector spatial data:

```python
import geopandas as gpd

# Read from file
gdf = gpd.read_file("data.shp")
gdf = gpd.read_file("data.geojson")
gdf = gpd.read_file("data.gpkg")

# Read from URL
gdf = gpd.read_file("https://example.com/data.geojson")

# Read from ZIP archive
gdf = gpd.read_file("data.zip")
```

### Performance: Arrow Acceleration

For 2-4x faster reading speeds, you can use Arrow:

```python
gdf = gpd.read_file("data.gpkg", use_arrow=True)
```

PyArrow needs to be installed: `uv pip install pyarrow`

### Filtering During Reading

Pre-filter data to load only what is needed:

```python
# Load specific rows
gdf = gpd.read_file("data.gpkg", rows=100)  # First 100 rows
gdf = gpd.read_file("data.gpkg", rows=slice(10, 20))  # Rows 10-20

# Load specific columns
gdf = gpd.read_file("data.gpkg", columns=['name', 'population'])

# Spatial filtering using a bounding box
gdf = gpd.read_file("data.gpkg", bbox=(xmin, ymin, xmax, ymax))

# Spatial filtering using a geometry mask
gdf = gpd.read_file("data.gpkg", mask=polygon_geometry)

# SQL WHERE clause (requires Fiona 1.9+ or Pyogrio)
gdf = gpd.read_file("data.gpkg", where="population > 1000000")

# Ignore geometry (returns a pandas DataFrame)
df = gpd.read_file("data.gpkg", ignore_geometry=True)
```

## Writing Files

Use `to_file()` for exporting:

```python
# Write to Shapefile
gdf.to_file("output.shp")

# Write to GeoJSON
gdf.to_file("output.geojson", driver='GeoJSON')

# Write to GeoPackage (supports multiple layers)
gdf.to_file("output.gpkg", layer='layer1', driver="GPKG")

# Use Arrow acceleration for faster writing
gdf.to_file("output.gpkg", use_arrow=True)
```

### Supported Formats

List all available drivers:

```python
import pyogrio
pyogrio.list_drivers()
```

Common formats: Shapefile, GeoJSON, GeoPackage (GPKG), KML, MapInfo File, CSV (with WKT geometry)

## Parquet and Feather

Columnar storage formats that support multiple geometry columns and preserve spatial information:

```python
# Write
gdf.to_parquet("data.parquet")
gdf.to_feather("data.feather")

# Read
gdf = gpd.read_parquet("data.parquet")
gdf = gpd.read_feather("data.feather")
```

Advantages:
- Faster I/O speeds than traditional formats
- Better compression ratios
- Support for preserving multiple geometry columns
- Support for schema versioning

## PostGIS Database

### Reading from PostGIS

```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:password@host:port/database')

# Read the entire table
gdf = gpd.read_postgis("SELECT * FROM table_name", con=engine, geom_col='geometry')

# Read using a SQL query
gdf = gpd.read_postgis("SELECT * FROM table WHERE population > 100000", con=engine, geom_col='geometry')
```

### Writing to PostGIS

```python
# Create or replace the table
gdf.to_postgis("table_name", con=engine, if_exists='replace')

# Append to an existing table
gdf.to_postgis("table_name", con=engine, if_exists='append')

# Raise an error if the table already exists
gdf.to_postgis("table_name", con=engine, if_exists='fail')
```

Dependencies: `uv pip install psycopg2` or `uv pip install psycopg` and `uv pip install geoalchemy2`

## File-like Objects

Read from file handles or memory buffers:

```python
# Read from a file handle
with open('data.geojson', 'r') as f:
    gdf = gpd.read_file(f)

# Read from StringIO
from io import StringIO
geojson_string = '{"type": "FeatureCollection", ...}'
gdf = gpd.read_file(StringIO(geojson_string))
```

## Remote Storage (fsspec)

Access data in cloud storage:

```python
# S3
gdf = gpd.read_file("s3://bucket/data.gpkg")

# Azure Blob Storage
gdf = gpd.read_file("az://container/data.gpkg")

# HTTP/HTTPS
gdf = gpd.read_file("https://example.com/data.geojson")
```