---
name: geopandas
description: A Python library for reading, writing, and analyzing geospatial vector data; use it when you need spatial operations (buffer/overlay/join), CRS reprojection, or map visualization on formats like Shapefile/GeoJSON/GeoPackage or PostGIS.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to **load and export vector geospatial data** (Shapefile, GeoJSON, GeoPackage, Parquet) and keep attributes + geometry together.
- You want to run **geometric operations** such as buffer, simplify, centroid, convex hull, or distance/area calculations.
- You need **spatial analysis** like spatial joins (intersects/within/nearest), overlay (intersection/union/difference), dissolve, or clipping.
- You must **manage coordinate reference systems (CRS)**: inspect CRS, set missing CRS metadata, or reproject between EPSG codes.
- You want to **visualize geospatial data** as static plots (matplotlib) or interactive maps (folium-backed `explore()`).

## Key Features

- **GeoDataFrame / GeoSeries**: pandas-like tabular structures with a geometry column and vectorized spatial methods.
- **Multi-format I/O**: read/write common GIS formats and integrate with PostGIS.
- **CRS-aware transformations**: `set_crs()` for metadata, `to_crs()` for coordinate transformation.
- **Spatial operations**: buffer/simplify/centroid and higher-level analysis (sjoin, overlay, dissolve).
- **Mapping**: quick plotting and choropleths; optional interactive exploration.

(Additional conceptual references: `references/data-structures.md`, `references/data-io.md`, `references/crs-management.md`, `references/geometric-operations.md`, `references/spatial-analysis.md`, `references/visualization.md`.)

## Dependencies

Core:
- `geopandas` (latest)
- `pandas` (transitive)
- `shapely` (transitive)

Optional (install as needed):
- `folium` (interactive maps via `GeoDataFrame.explore()`)
- `mapclassify` (classification schemes for choropleths)
- `pyarrow` (faster I/O; enables `use_arrow=True` in some writers)
- `psycopg2` and `geoalchemy2` (PostGIS connectivity)
- `contextily` (basemaps)
- `cartopy` (map projections / advanced cartographic plotting)

## Example Usage

```python
import geopandas as gpd

def main():
    # 1) Read vector data (GeoJSON/Shapefile/GeoPackage/etc.)
    gdf = gpd.read_file("data.geojson")

    # 2) Inspect CRS and geometry types
    print("CRS:", gdf.crs)
    print("Geometry types:", gdf.geometry.geom_type.unique())

    # 3) Reproject for metric calculations (area/distance)
    #    Use a projected CRS appropriate for your region; EPSG:3857 is common but not always ideal.
    gdf_m = gdf.to_crs("EPSG:3857")

    # 4) Compute area and create a buffer (units are CRS units; meters in many projected CRSs)
    gdf_m["area_m2"] = gdf_m.geometry.area
    gdf_m["geometry"] = gdf_m.geometry.buffer(100)

    # 5) Plot a quick choropleth (static)
    ax = gdf_m.plot(column="area_m2", cmap="YlOrRd", legend=True)
    ax.set_title("Buffered features colored by area (m²)")

    # 6) Write results to GeoPackage
    gdf_m.to_file("output.gpkg", layer="buffered", driver="GPKG")

if __name__ == "__main__":
    main()
```

## Implementation Details

- **Data model**
  - `GeoSeries`: a 1D array of geometries with vectorized spatial methods.
  - `GeoDataFrame`: a pandas DataFrame with a designated geometry column (commonly named `geometry`).

- **CRS rules**
  - `set_crs("EPSG:4326")` sets CRS metadata **without transforming coordinates** (use only when CRS is missing/unknown but you are sure of it).
  - `to_crs("EPSG:3857")` **transforms coordinates** into a new CRS.
  - **Area/distance** should be computed in a **projected CRS** (units typically meters/feet). Geographic CRS (lat/lon) is not suitable for metric area/distance.

- **Spatial joins**
  - `gpd.sjoin(left, right, predicate="intersects"|"within"|"contains"|...)` matches features using a spatial predicate.
  - `gpd.sjoin_nearest(..., max_distance=...)` performs nearest-neighbor matching; setting `max_distance` can reduce work and avoid unexpected far matches.

- **Overlay operations**
  - `gpd.overlay(gdf1, gdf2, how="intersection"|"union"|"difference"|...)` computes polygon overlays; complexity grows with geometry vertex count, so simplifying geometries can improve performance when high precision is not required.

- **I/O performance**
  - When supported, enabling Arrow-backed paths (e.g., `use_arrow=True`) can speed up read/write operations; `pyarrow` is typically required.
  - Use read-time filters like `bbox=` (and format-specific filters) to avoid loading unnecessary features.

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `geopandas_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: geopandas_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: A Python library for reading, writing, and analyzing geospatial vector data; use it when you need spatial operations (buffer/overlay/join), CRS reprojection, or map visualization on formats like Shapefile/GeoJSON/GeoPackage or PostGIS.
