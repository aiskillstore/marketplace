---
name: fiftyone-embeddings-visualization
description: Visualize datasets in 2D using embeddings with UMAP or t-SNE dimensionality reduction. Use when users want to explore dataset structure, find clusters in images, identify outliers, color samples by class or metadata, or understand data distribution. Requires FiftyOne MCP server with @voxel51/brain plugin installed.
---

# Embeddings Visualization in FiftyOne

## Overview

Visualize your dataset in 2D using deep learning embeddings and dimensionality reduction (UMAP/t-SNE). Explore clusters, find outliers, and color samples by any field.

**Use this skill when:**
- Visualizing dataset structure in 2D
- Finding natural clusters in images
- Identifying outliers or anomalies
- Exploring data distribution by class or metadata
- Understanding embedding space relationships

## Prerequisites

- FiftyOne MCP server installed and running
- `@voxel51/brain` plugin installed and enabled
- Dataset with image samples loaded in FiftyOne

## Key Directives

**ALWAYS follow these rules:**

### 1. Set context first
```python
set_context(dataset_name="my-dataset")
```

### 2. Launch FiftyOne App
Brain operators are delegated and require the app:
```python
launch_app()
```
Wait 5-10 seconds for initialization.

### 3. Discover operators dynamically
```python
# List all brain operators
list_operators(builtin_only=False)

# Get schema for specific operator
get_operator_schema(operator_uri="@voxel51/brain/compute_visualization")
```

### 4. Compute embeddings before visualization
Embeddings are required for dimensionality reduction:
```python
execute_operator(
    operator_uri="@voxel51/brain/compute_similarity",
    params={
        "brain_key": "img_sim",
        "model": "clip-vit-base32-torch",
        "embeddings": "clip_embeddings",
        "backend": "sklearn",
        "metric": "cosine"
    }
)
```

### 5. Close app when done
```python
close_app()
```

## Complete Workflow

### Step 1: Setup
```python
# Set context
set_context(dataset_name="my-dataset")

# Launch app (required for brain operators)
launch_app()
```

### Step 2: Verify Brain Plugin
```python
# Check if brain plugin is available
list_plugins(enabled=True)

# If not installed:
download_plugin(
    url_or_repo="voxel51/fiftyone-plugins",
    plugin_names=["@voxel51/brain"]
)
enable_plugin(plugin_name="@voxel51/brain")
```

### Step 3: Discover Brain Operators
```python
# List all available operators
list_operators(builtin_only=False)

# Get schema for compute_visualization
get_operator_schema(operator_uri="@voxel51/brain/compute_visualization")
```

### Step 4: Check for Existing Embeddings or Compute New Ones

First, check if the dataset already has embeddings by looking at the operator schema:
```python
get_operator_schema(operator_uri="@voxel51/brain/compute_visualization")
# Look for existing embeddings fields in the "embeddings" choices
# (e.g., "clip_embeddings", "dinov2_embeddings")
```

**If embeddings exist:** Skip to Step 5 and use the existing embeddings field.

**If no embeddings exist:** Compute them:
```python
execute_operator(
    operator_uri="@voxel51/brain/compute_similarity",
    params={
        "brain_key": "img_viz",
        "model": "clip-vit-base32-torch",
        "embeddings": "clip_embeddings",  # Field name to store embeddings
        "backend": "sklearn",
        "metric": "cosine"
    }
)
```

**Required parameters for compute_similarity:**
- `brain_key` - Unique identifier for this brain run
- `model` - Model from FiftyOne Model Zoo to generate embeddings
- `embeddings` - Field name where embeddings will be stored
- `backend` - Similarity backend (use `"sklearn"`)
- `metric` - Distance metric (use `"cosine"` or `"euclidean"`)

**Recommended embedding models:**
- `clip-vit-base32-torch` - Best for general visual + semantic similarity
- `dinov2-vits14-torch` - Best for visual similarity only
- `resnet50-imagenet-torch` - Classic CNN features
- `mobilenet-v2-imagenet-torch` - Fast, lightweight option

### Step 5: Compute 2D Visualization

Use existing embeddings field OR the brain_key from Step 4:
```python
# Option A: Use existing embeddings field (e.g., clip_embeddings)
execute_operator(
    operator_uri="@voxel51/brain/compute_visualization",
    params={
        "brain_key": "img_viz",
        "embeddings": "clip_embeddings",  # Use existing field
        "method": "umap",
        "num_dims": 2
    }
)

# Option B: Use brain_key from compute_similarity
execute_operator(
    operator_uri="@voxel51/brain/compute_visualization",
    params={
        "brain_key": "img_viz",  # Same key used in compute_similarity
        "method": "umap",
        "num_dims": 2
    }
)
```

**Dimensionality reduction methods:**
- `umap` - (Recommended) Preserves local and global structure, faster. Requires `umap-learn` package.
- `tsne` - Better local structure, slower on large datasets. No extra dependencies.
- `pca` - Linear reduction, fastest but less informative

### Step 6: Direct User to Embeddings Panel

After computing visualization, direct the user to open the FiftyOne App at http://localhost:5151/ and:

1. Click the **Embeddings** panel icon (scatter plot icon, looks like a grid of dots) in the top toolbar
2. Select the brain key (e.g., `img_viz`) from the dropdown
3. Points represent samples in 2D embedding space
4. Use the **"Color by"** dropdown to color points by a field (e.g., `ground_truth`, `predictions`)
5. Click points to select samples, use lasso tool to select groups

**IMPORTANT:** Do NOT use `set_view(exists=["brain_key"])` - this filters samples and is not needed for visualization. The Embeddings panel automatically shows all samples with computed coordinates.

### Step 7: Explore and Filter (Optional)

To filter samples while viewing in the Embeddings panel:
```python
# Filter to specific class
set_view(filters={"ground_truth.label": "dog"})

# Filter by tag
set_view(tags=["validated"])

# Clear filter to show all
clear_view()
```

These filters will update the Embeddings panel to show only matching samples.

### Step 8: Find Outliers

Outliers appear as isolated points far from clusters:

```python
# Compute uniqueness scores (higher = more unique/outlier)
execute_operator(
    operator_uri="@voxel51/brain/compute_uniqueness",
    params={
        "brain_key": "img_viz"
    }
)

# View most unique samples (potential outliers)
set_view(sort_by="uniqueness", reverse=True, limit=50)
```

### Step 9: Find Clusters

Use the App's Embeddings panel to visually identify clusters, then:

**Option A: Lasso selection in App**
1. Use lasso tool to select a cluster
2. Selected samples are highlighted
3. Tag or export selected samples

**Option B: Use similarity to find cluster members**
```python
# Sort by similarity to a representative sample
execute_operator(
    operator_uri="@voxel51/brain/sort_by_similarity",
    params={
        "brain_key": "img_viz",
        "query_id": "sample_id_from_cluster",
        "k": 100
    }
)
```

### Step 10: Clean Up
```python
close_app()
```

## Available Tools

### Session View Tools

| Tool | Description |
|------|-------------|
| `set_view(filters={...})` | Filter samples by field values |
| `set_view(tags=[...])` | Filter samples by tags |
| `set_view(sort_by="...", reverse=True)` | Sort samples by field |
| `set_view(limit=N)` | Limit to N samples |
| `clear_view()` | Clear filters, show all samples |

### Brain Operators for Visualization

Use `list_operators()` to discover and `get_operator_schema()` to see parameters:

| Operator | Description |
|----------|-------------|
| `@voxel51/brain/compute_similarity` | Compute embeddings and similarity index |
| `@voxel51/brain/compute_visualization` | Reduce embeddings to 2D/3D for visualization |
| `@voxel51/brain/compute_uniqueness` | Score samples by uniqueness (outlier detection) |
| `@voxel51/brain/sort_by_similarity` | Sort by similarity to a query sample |

## Common Use Cases

### Use Case 1: Basic Dataset Exploration
Visualize dataset structure and explore clusters:
```python
set_context(dataset_name="my-dataset")
launch_app()

# Check for existing embeddings in schema
get_operator_schema(operator_uri="@voxel51/brain/compute_visualization")

# If embeddings exist (e.g., clip_embeddings), use them directly:
execute_operator(
    operator_uri="@voxel51/brain/compute_visualization",
    params={
        "brain_key": "exploration",
        "embeddings": "clip_embeddings",
        "method": "umap",  # or "tsne" if umap-learn not installed
        "num_dims": 2
    }
)

# Direct user to App Embeddings panel at http://localhost:5151/
# 1. Click Embeddings panel icon
# 2. Select "exploration" from dropdown
# 3. Use "Color by" to color by ground_truth or predictions
```

### Use Case 2: Find Outliers in Dataset
Identify anomalous or mislabeled samples:
```python
set_context(dataset_name="my-dataset")
launch_app()

# Check for existing embeddings in schema
get_operator_schema(operator_uri="@voxel51/brain/compute_visualization")

# If no embeddings exist, compute them:
execute_operator(
    operator_uri="@voxel51/brain/compute_similarity",
    params={
        "brain_key": "outliers",
        "model": "clip-vit-base32-torch",
        "embeddings": "clip_embeddings",
        "backend": "sklearn",
        "metric": "cosine"
    }
)

# Compute uniqueness scores
execute_operator(
    operator_uri="@voxel51/brain/compute_uniqueness",
    params={"brain_key": "outliers"}
)

# Generate visualization (use existing embeddings field or brain_key)
execute_operator(
    operator_uri="@voxel51/brain/compute_visualization",
    params={
        "brain_key": "outliers",
        "embeddings": "clip_embeddings",  # Use existing field if available
        "method": "umap",  # or "tsne" if umap-learn not installed
        "num_dims": 2
    }
)

# Direct user to App at http://localhost:5151/
# 1. Click Embeddings panel icon
# 2. Select "outliers" from dropdown
# 3. Outliers appear as isolated points far from clusters
# 4. Optionally sort by uniqueness field in the App sidebar
```

### Use Case 3: Compare Classes in Embedding Space
See how different classes cluster:
```python
set_context(dataset_name="my-dataset")
launch_app()

# Check for existing embeddings in schema
get_operator_schema(operator_uri="@voxel51/brain/compute_visualization")

# If no embeddings exist, compute them:
execute_operator(
    operator_uri="@voxel51/brain/compute_similarity",
    params={
        "brain_key": "class_viz",
        "model": "clip-vit-base32-torch",
        "embeddings": "clip_embeddings",
        "backend": "sklearn",
        "metric": "cosine"
    }
)

# Generate visualization (use existing embeddings field or brain_key)
execute_operator(
    operator_uri="@voxel51/brain/compute_visualization",
    params={
        "brain_key": "class_viz",
        "embeddings": "clip_embeddings",  # Use existing field if available
        "method": "umap",  # or "tsne" if umap-learn not installed
        "num_dims": 2
    }
)

# Direct user to App at http://localhost:5151/
# 1. Click Embeddings panel icon
# 2. Select "class_viz" from dropdown
# 3. Use "Color by" dropdown to color by ground_truth or predictions
# Look for:
# - Well-separated clusters = good class distinction
# - Overlapping clusters = similar classes or confusion
# - Scattered points = high variance within class
```

### Use Case 4: Analyze Model Predictions
Compare ground truth vs predictions in embedding space:
```python
set_context(dataset_name="my-dataset")
launch_app()

# Check for existing embeddings in schema
get_operator_schema(operator_uri="@voxel51/brain/compute_visualization")

# If no embeddings exist, compute them:
execute_operator(
    operator_uri="@voxel51/brain/compute_similarity",
    params={
        "brain_key": "pred_analysis",
        "model": "clip-vit-base32-torch",
        "embeddings": "clip_embeddings",
        "backend": "sklearn",
        "metric": "cosine"
    }
)

# Generate visualization (use existing embeddings field or brain_key)
execute_operator(
    operator_uri="@voxel51/brain/compute_visualization",
    params={
        "brain_key": "pred_analysis",
        "embeddings": "clip_embeddings",  # Use existing field if available
        "method": "umap",  # or "tsne" if umap-learn not installed
        "num_dims": 2
    }
)

# Direct user to App at http://localhost:5151/
# 1. Click Embeddings panel icon
# 2. Select "pred_analysis" from dropdown
# 3. Color by ground_truth - see true class distribution
# 4. Color by predictions - see model's view
# 5. Look for mismatches to find errors
```

### Use Case 5: t-SNE for Publication-Quality Plots
Use t-SNE for better local structure (no extra dependencies):
```python
set_context(dataset_name="my-dataset")
launch_app()

# Check for existing embeddings in schema
get_operator_schema(operator_uri="@voxel51/brain/compute_visualization")

# If no embeddings exist, compute them (DINOv2 for visual similarity):
execute_operator(
    operator_uri="@voxel51/brain/compute_similarity",
    params={
        "brain_key": "tsne_viz",
        "model": "dinov2-vits14-torch",
        "embeddings": "dinov2_embeddings",
        "backend": "sklearn",
        "metric": "cosine"
    }
)

# Generate t-SNE visualization (no umap-learn dependency needed)
execute_operator(
    operator_uri="@voxel51/brain/compute_visualization",
    params={
        "brain_key": "tsne_viz",
        "embeddings": "dinov2_embeddings",  # Use existing field if available
        "method": "tsne",
        "num_dims": 2
    }
)

# Direct user to App at http://localhost:5151/
# 1. Click Embeddings panel icon
# 2. Select "tsne_viz" from dropdown
# 3. t-SNE provides better local cluster structure than UMAP
```

## Troubleshooting

**Error: "No executor available"**
- Cause: Delegated operators require the App executor
- Solution: Ensure `launch_app()` was called and wait 5-10 seconds

**Error: "Brain key not found"**
- Cause: Embeddings not computed
- Solution: Run `compute_similarity` first with a `brain_key`

**Error: "Operator not found"**
- Cause: Brain plugin not installed
- Solution: Install with `download_plugin()` and `enable_plugin()`

**Error: "You must install the `umap-learn>=0.5` package"**
- Cause: UMAP method requires the `umap-learn` package
- Solutions:
  1. **Install umap-learn**: Ask user if they want to run `pip install umap-learn`
  2. **Use t-SNE instead**: Change `method` to `"tsne"` (no extra dependencies)
  3. **Use PCA instead**: Change `method` to `"pca"` (fastest, no extra dependencies)
- After installing umap-learn, restart Claude Code/MCP server and retry

**Visualization is slow**
- Use UMAP instead of t-SNE for large datasets
- Use faster embedding model: `mobilenet-v2-imagenet-torch`
- Process subset first: `set_view(limit=1000)`

**Embeddings panel not showing**
- Ensure visualization was computed (not just embeddings)
- Check brain_key matches in both compute_similarity and compute_visualization
- Refresh the App page

**Points not colored correctly**
- Verify the field exists on samples
- Check field type is compatible (Classification, Detections, or string)

## Best Practices

1. **Discover dynamically** - Use `list_operators()` and `get_operator_schema()` to get current operator names and parameters
2. **Choose the right model** - CLIP for semantic similarity, DINOv2 for visual similarity
3. **Start with UMAP** - Faster and often better than t-SNE for exploration
4. **Use uniqueness for outliers** - More reliable than visual inspection alone
5. **Store embeddings** - Reuse for multiple visualizations via `brain_key`
6. **Subset large datasets** - Compute on subset first, then full dataset

## Performance Notes

**Embedding computation time:**
- 1,000 images: ~1-2 minutes
- 10,000 images: ~10-15 minutes
- 100,000 images: ~1-2 hours

**Visualization computation time:**
- UMAP: ~30 seconds for 10,000 samples
- t-SNE: ~5-10 minutes for 10,000 samples
- PCA: ~5 seconds for 10,000 samples

**Memory requirements:**
- ~2KB per image for embeddings
- ~16 bytes per image for 2D coordinates

## Resources

- [FiftyOne Brain Documentation](https://docs.voxel51.com/user_guide/brain.html)
- [Visualizing Embeddings Guide](https://docs.voxel51.com/user_guide/embeddings.html)
- [Brain Plugin Source](https://github.com/voxel51/fiftyone-plugins/tree/main/plugins/brain)

## License

Copyright 2017-2025, Voxel51, Inc.
Apache 2.0 License
