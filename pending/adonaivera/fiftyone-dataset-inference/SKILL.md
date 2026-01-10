---
name: fiftyone-dataset-inference
description: Create a FiftyOne dataset from a directory of media files (images, videos, point clouds), optionally import labels in common formats (COCO, YOLO, VOC), run model inference, and store predictions. Use when users want to load local files into FiftyOne, apply ML models for detection, classification, or segmentation, or build end-to-end inference pipelines.
---

# Create Dataset and Run Inference

## Overview

Create FiftyOne datasets from local directories, import labels in standard formats, and run model inference to generate predictions.

**Use this skill when:**
- Loading images, videos, or point clouds from a directory
- Importing labeled datasets (COCO, YOLO, VOC, CVAT, etc.)
- Running model inference on media files
- Building end-to-end ML pipelines

## Prerequisites

- FiftyOne MCP server installed and running
- `@voxel51/io` plugin for importing data
- `@voxel51/zoo` plugin for model inference
- `@voxel51/utils` plugin for dataset management

## Key Directives

**ALWAYS follow these rules:**

### 1. Explore directory first
Scan the user's directory before importing to detect media types and label formats.

### 2. Confirm with user
Present findings and get confirmation before creating datasets or running inference.

### 3. Set context before operations
```python
set_context(dataset_name="my-dataset")
```

### 4. Launch App for inference
```python
launch_app(dataset_name="my-dataset")
```

### 5. User specifies field names
Always ask the user for:
- Dataset name
- Label field for predictions

### 6. Close app when done
```python
close_app()
```

## Workflow

### Step 1: Explore the Directory

Use Bash to scan the user's directory:

```bash
ls -la /path/to/directory
find /path/to/directory -type f | head -20
```

Identify media files and label files. See **Supported Dataset Types** section for format detection.

### Step 2: Present Findings to User

Before creating the dataset, confirm with the user:

```
I found the following in /path/to/directory:
- 150 image files (.jpg, .png)
- Labels: COCO format (annotations.json)

Proposed dataset name: "my-dataset"
Label field: "ground_truth"

Should I proceed with these settings?
```

### Step 3: Create Dataset

```python
execute_operator(
    operator_uri="@voxel51/utils/create_dataset",
    params={
        "name": "my-dataset",
        "persistent": true
    }
)
```

### Step 4: Set Context

Set context to the newly created dataset before importing:

```python
set_context(dataset_name="my-dataset")
```

### Step 5: Import Samples

**For media only (no labels):**
```python
execute_operator(
    operator_uri="@voxel51/io/import_samples",
    params={
        "import_type": "MEDIA_ONLY",
        "style": "DIRECTORY",
        "directory": {"absolute_path": "/path/to/images"}
    }
)
```

**For media with labels:**
```python
execute_operator(
    operator_uri="@voxel51/io/import_samples",
    params={
        "import_type": "MEDIA_AND_LABELS",
        "dataset_type": "COCO",
        "data_path": {"absolute_path": "/path/to/images"},
        "labels_path": {"absolute_path": "/path/to/annotations.json"},
        "label_field": "ground_truth"
    }
)
```

### Step 6: Validate Import

Verify samples imported correctly by comparing with source:

```python
load_dataset(name="my-dataset")
```

Compare `num_samples` with the file count from Step 1. Report any discrepancy to the user.

### Step 7: Launch App

```python
launch_app(dataset_name="my-dataset")
```

### Step 8: Apply Model Inference

Ask user for model name and label field for predictions.

```python
execute_operator(
    operator_uri="@voxel51/zoo/apply_zoo_model",
    params={
        "tab": "BUILTIN",
        "model": "yolov8n-coco-torch",
        "label_field": "predictions"
    }
)
```

### Step 9: View Results

```python
set_view(exists=["predictions"])
```

### Step 10: Clean Up

```python
close_app()
```

## Supported Media Types

| Extensions | Media Type |
|------------|------------|
| `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp` | image |
| `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm` | video |
| `.pcd` | point-cloud |
| `.fo3d` | 3d |

## Supported Dataset Types

| Value | File Pattern | Label Types |
|-------|--------------|-------------|
| `Image Classification Directory Tree` | Folder per class | classification |
| `Video Classification Directory Tree` | Folder per class | classification |
| `COCO` | `*.json` | detections, segmentations, keypoints |
| `VOC` | `*.xml` per image | detections |
| `KITTI` | `*.txt` per image | detections |
| `YOLOv4` | `*.txt` + `classes.txt` | detections |
| `YOLOv5` | `data.yaml` + `labels/*.txt` | detections |
| `CVAT Image` | Single `*.xml` file | classifications, detections, polylines, keypoints |
| `CVAT Video` | XML directory | frame labels |
| `TF Image Classification` | TFRecords | classification |
| `TF Object Detection` | TFRecords | detections |

## Common Zoo Models

Popular models for `apply_zoo_model`. Some models require additional packages - if a model fails with a dependency error, the response includes the `install_command`. Offer to run it for the user.

**Detection (PyTorch only):**
- `faster-rcnn-resnet50-fpn-coco-torch` - Faster R-CNN (no extra deps)
- `retinanet-resnet50-fpn-coco-torch` - RetinaNet (no extra deps)

**Detection (requires ultralytics):**
- `yolov8n-coco-torch` - YOLOv8 nano (fast)
- `yolov8s-coco-torch` - YOLOv8 small
- `yolov8m-coco-torch` - YOLOv8 medium

**Classification:**
- `resnet50-imagenet-torch` - ResNet-50
- `mobilenet-v2-imagenet-torch` - MobileNet v2

**Segmentation:**
- `sam-vit-base-hq-torch` - Segment Anything
- `deeplabv3-resnet101-coco-torch` - DeepLabV3

**Embeddings:**
- `clip-vit-base32-torch` - CLIP embeddings
- `dinov2-vits14-torch` - DINOv2 embeddings

## Common Use Cases

### Use Case 1: Load Images and Run Detection

```python
execute_operator(
    operator_uri="@voxel51/utils/create_dataset",
    params={"name": "my-images", "persistent": true}
)

set_context(dataset_name="my-images")

execute_operator(
    operator_uri="@voxel51/io/import_samples",
    params={
        "import_type": "MEDIA_ONLY",
        "style": "DIRECTORY",
        "directory": {"absolute_path": "/path/to/images"}
    }
)

load_dataset(name="my-images")  # Validate import

launch_app(dataset_name="my-images")

execute_operator(
    operator_uri="@voxel51/zoo/apply_zoo_model",
    params={
        "tab": "BUILTIN",
        "model": "faster-rcnn-resnet50-fpn-coco-torch",
        "label_field": "predictions"
    }
)

set_view(exists=["predictions"]) 
```

### Use Case 2: Import COCO Dataset and Add Predictions

```python
execute_operator(
    operator_uri="@voxel51/utils/create_dataset",
    params={"name": "coco-dataset", "persistent": true}
)

set_context(dataset_name="coco-dataset")

execute_operator(
    operator_uri="@voxel51/io/import_samples",
    params={
        "import_type": "MEDIA_AND_LABELS",
        "dataset_type": "COCO",
        "data_path": {"absolute_path": "/path/to/images"},
        "labels_path": {"absolute_path": "/path/to/annotations.json"},
        "label_field": "ground_truth"
    }
)

load_dataset(name="coco-dataset")  # Validate import

launch_app(dataset_name="coco-dataset")

execute_operator(
    operator_uri="@voxel51/zoo/apply_zoo_model",
    params={
        "tab": "BUILTIN",
        "model": "faster-rcnn-resnet50-fpn-coco-torch",
        "label_field": "predictions"
    }
)

set_view(exists=["predictions"]) 
```

### Use Case 3: Import YOLO Dataset

```python
execute_operator(
    operator_uri="@voxel51/utils/create_dataset",
    params={"name": "yolo-dataset", "persistent": true}
)

set_context(dataset_name="yolo-dataset")

execute_operator(
    operator_uri="@voxel51/io/import_samples",
    params={
        "import_type": "MEDIA_AND_LABELS",
        "dataset_type": "YOLOv5",
        "dataset_dir": {"absolute_path": "/path/to/yolo/dataset"},
        "label_field": "ground_truth"
    }
)

load_dataset(name="yolo-dataset")  

launch_app(dataset_name="yolo-dataset")
```

### Use Case 4: Classification with Directory Tree

For a folder structure like:
```
/dataset/
  /cats/
    cat1.jpg
    cat2.jpg
  /dogs/
    dog1.jpg
    dog2.jpg
```

```python
execute_operator(
    operator_uri="@voxel51/utils/create_dataset",
    params={"name": "classification-dataset", "persistent": true}
)

set_context(dataset_name="classification-dataset")

execute_operator(
    operator_uri="@voxel51/io/import_samples",
    params={
        "import_type": "MEDIA_AND_LABELS",
        "dataset_type": "Image Classification Directory Tree",
        "dataset_dir": {"absolute_path": "/path/to/dataset"},
        "label_field": "ground_truth"
    }
)

load_dataset(name="classification-dataset")  

launch_app(dataset_name="classification-dataset")
```

## Troubleshooting

**Error: "Dataset already exists"**
- Use a different dataset name
- Or delete existing dataset first with `@voxel51/utils/delete_dataset`

**Error: "No samples found"**
- Verify the directory path is correct
- Check file extensions are supported
- Ensure files are not in nested subdirectories (use `recursive=true` if needed)

**Error: "Labels path not found"**
- Verify the labels file/directory exists
- Check the path is absolute, not relative

**Error: "Model not found"**
- Check model name spelling
- Verify model exists in FiftyOne Zoo
- Use `list_operators()` and `get_operator_schema()` to discover available models

**Error: "Missing dependency" (e.g., torch, ultralytics)**
- The MCP server detects missing dependencies
- Response includes `missing_package` and `install_command`
- Install the required package and restart MCP server

**Slow inference**
- Use smaller model variant (e.g., `yolov8n` instead of `yolov8x`)
- Reduce batch size
- Consider delegated execution for large datasets

## Best Practices

1. **Explore before importing** - Always scan the directory first to understand the data
2. **Confirm with user** - Present findings and get confirmation before creating datasets
3. **Use descriptive names** - Dataset names and label fields should be meaningful
4. **Separate ground truth from predictions** - Use different field names (e.g., `ground_truth` vs `predictions`)
5. **Start with fast models** - Use lightweight models first, then upgrade if needed
6. **Check operator schemas** - Use `get_operator_schema()` to discover available parameters

## Resources

- [FiftyOne Dataset Zoo](https://docs.voxel51.com/dataset_zoo/index.html)
- [FiftyOne Model Zoo](https://docs.voxel51.com/model_zoo/index.html)
- [Importing Datasets Guide](https://docs.voxel51.com/user_guide/import_datasets.html)
- [Applying Models Guide](https://docs.voxel51.com/user_guide/applying_models.html)

## License

Copyright 2017-2025, Voxel51, Inc.
Apache 2.0 License
