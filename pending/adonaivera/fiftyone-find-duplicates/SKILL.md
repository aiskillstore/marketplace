---
name: fiftyone-find-duplicates
description: Find duplicate or near-duplicate images in FiftyOne datasets using brain similarity computation. Use when users want to deduplicate datasets, find similar images, cluster visually similar content, or remove redundant samples. Requires FiftyOne MCP server with @voxel51/brain plugin installed.
---

# Find Duplicates in FiftyOne Datasets

## Overview

Find and remove duplicate or near-duplicate images using FiftyOne's brain similarity operators. Uses deep learning embeddings to identify visually similar images.

**Use this skill when:**
- Removing duplicate images from datasets
- Finding near-duplicate images (similar but not identical)
- Clustering visually similar images
- Cleaning datasets before training

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
get_operator_schema(operator_uri="@voxel51/brain/compute_similarity")
```

### 4. Compute embeddings before finding duplicates
```python
execute_operator(
    operator_uri="@voxel51/brain/compute_similarity",
    params={"brain_key": "img_sim", "model": "mobilenet-v2-imagenet-torch"}
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

# Get schema for compute_similarity
get_operator_schema(operator_uri="@voxel51/brain/compute_similarity")

# Get schema for find_duplicates
get_operator_schema(operator_uri="@voxel51/brain/find_duplicates")
```

### Step 4: Compute Similarity
```python
# Execute operator to compute embeddings
execute_operator(
    operator_uri="@voxel51/brain/compute_similarity",
    params={
        "brain_key": "img_duplicates",
        "model": "mobilenet-v2-imagenet-torch"
    }
)
```

### Step 5: Find Near Duplicates
```python
execute_operator(
    operator_uri="@voxel51/brain/find_near_duplicates",
    params={
        "similarity_index": "img_duplicates",
        "threshold": 0.3
    }
)
```

**Threshold guidelines (distance-based, lower = more similar):**
- `0.1` = Very similar (near-exact duplicates)
- `0.3` = Near duplicates (recommended default)
- `0.5` = Similar images
- `0.7` = Loosely similar

This operator creates two saved views automatically:
- `near duplicates`: all samples that are near duplicates
- `representatives of near duplicates`: one representative from each group

### Step 6: View Duplicates in App

After finding duplicates, use `set_view` to display them in the FiftyOne App:

**Option A: Filter by near_dup_id field**
```python
# Show all samples that have a near_dup_id (all duplicates)
set_view(exists=["near_dup_id"])
```

**Option B: Show specific duplicate group**
```python
# Show samples with a specific duplicate group ID
set_view(filters={"near_dup_id": 1})
```

**Option C: Load saved view (if available)**
```python
# Load the automatically created saved view
set_view(view_name="near duplicates")
```

**Option D: Clear filter to show all samples**
```python
clear_view()
```

The `find_near_duplicates` operator adds a `near_dup_id` field to samples. Samples with the same ID are duplicates of each other.

### Step 7: Delete Duplicates

**Option A: Use deduplicate operator (keeps one representative per group)**
```python
execute_operator(
    operator_uri="@voxel51/brain/deduplicate_near_duplicates",
    params={}
)
```

**Option B: Manual deletion from App UI**
1. Use `set_view(exists=["near_dup_id"])` to show duplicates
2. Review samples in the App at http://localhost:5151/
3. Select samples to delete
4. Use the delete action in the App

### Step 8: Clean Up
```python
close_app()
```

## Available Tools

### Session View Tools

| Tool | Description |
|------|-------------|
| `set_view(exists=[...])` | Filter samples where field(s) have non-None values |
| `set_view(filters={...})` | Filter samples by exact field values |
| `set_view(tags=[...])` | Filter samples by tags |
| `set_view(sample_ids=[...])` | Select specific sample IDs |
| `set_view(view_name="...")` | Load a saved view by name |
| `clear_view()` | Clear filters, show all samples |

### Brain Operators for Duplicates

Use `list_operators()` to discover and `get_operator_schema()` to see parameters:

| Operator | Description |
|----------|-------------|
| `@voxel51/brain/compute_similarity` | Compute embeddings and similarity index |
| `@voxel51/brain/find_near_duplicates` | Find near-duplicate samples |
| `@voxel51/brain/deduplicate_near_duplicates` | Delete duplicates, keep representatives |
| `@voxel51/brain/find_exact_duplicates` | Find exact duplicate media files |
| `@voxel51/brain/deduplicate_exact_duplicates` | Delete exact duplicates |
| `@voxel51/brain/compute_uniqueness` | Compute uniqueness scores |

## Common Use Cases

### Use Case 1: Remove Exact Duplicates
For accidentally duplicated files (identical bytes):
```python
set_context(dataset_name="my-dataset")
launch_app()

execute_operator(
    operator_uri="@voxel51/brain/find_exact_duplicates",
    params={}
)

execute_operator(
    operator_uri="@voxel51/brain/deduplicate_exact_duplicates",
    params={}
)

close_app()
```

### Use Case 2: Find and Review Near Duplicates
For visually similar but not identical images:
```python
set_context(dataset_name="my-dataset")
launch_app()

# Compute embeddings
execute_operator(
    operator_uri="@voxel51/brain/compute_similarity",
    params={"brain_key": "near_dups", "model": "mobilenet-v2-imagenet-torch"}
)

# Find duplicates
execute_operator(
    operator_uri="@voxel51/brain/find_near_duplicates",
    params={"similarity_index": "near_dups", "threshold": 0.3}
)

# View duplicates in the App
set_view(exists=["near_dup_id"])

# After review, deduplicate
execute_operator(
    operator_uri="@voxel51/brain/deduplicate_near_duplicates",
    params={}
)

# Clear view and close
clear_view()
close_app()
```

### Use Case 3: Sort by Similarity
Find images similar to a specific sample:
```python
set_context(dataset_name="my-dataset")
launch_app()

execute_operator(
    operator_uri="@voxel51/brain/compute_similarity",
    params={"brain_key": "search"}
)

execute_operator(
    operator_uri="@voxel51/brain/sort_by_similarity",
    params={
        "brain_key": "search",
        "query_id": "sample_id_here",
        "k": 20
    }
)

close_app()
```

## Troubleshooting

**Error: "No executor available"**
- Cause: Delegated operators require the App executor for UI triggers
- Solution: Direct user to App UI to view results and complete deletion manually
- Affected operators: `find_near_duplicates`, `deduplicate_near_duplicates`

**Error: "Brain key not found"**
- Cause: Embeddings not computed
- Solution: Run `compute_similarity` first with a `brain_key`

**Error: "Operator not found"**
- Cause: Brain plugin not installed
- Solution: Install with `download_plugin()` and `enable_plugin()`

**Error: "Missing dependency" (e.g., torch, tensorflow)**
- The MCP server detects missing dependencies automatically
- Response includes `missing_package` and `install_command`
- Example response:
  ```json
  {
    "error_type": "missing_dependency",
    "missing_package": "torch",
    "install_command": "pip install torch"
  }
  ```
- Offer to run the install command for the user
- After installation, restart MCP server and retry

**Similarity computation is slow**
- Use faster model: `mobilenet-v2-imagenet-torch`
- Use GPU if available
- Process large datasets in batches

## Best Practices

1. **Discover dynamically** - Use `list_operators()` and `get_operator_schema()` to get current operator names and parameters
2. **Start with default threshold** (0.3) and adjust as needed
3. **Review before deleting** - Direct user to App to inspect duplicates
4. **Store embeddings** - Reuse for multiple operations via `brain_key`
5. **Handle executor errors gracefully** - Guide user to App UI when needed

## Performance Notes

**Embedding computation time:**
- 1,000 images: ~1-2 minutes
- 10,000 images: ~10-15 minutes
- 100,000 images: ~1-2 hours

**Memory requirements:**
- ~2KB per image for embeddings
- ~4-8KB per image for similarity index

## Resources

- [FiftyOne Brain Documentation](https://docs.voxel51.com/user_guide/brain.html)
- [Brain Plugin Source](https://github.com/voxel51/fiftyone-plugins/tree/main/plugins/brain)

## License

Copyright 2017-2025, Voxel51, Inc.
Apache 2.0 License
