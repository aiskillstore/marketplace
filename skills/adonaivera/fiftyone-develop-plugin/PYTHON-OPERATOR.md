# Python Operator Development

## Operator Anatomy

```python
import fiftyone.operators as foo
import fiftyone.operators.types as types


class MyOperator(foo.Operator):
    @property
    def config(self):
        """Operator metadata and configuration"""
        return foo.OperatorConfig(
            name="my_operator",
            label="My Operator",
            description="What this operator does",
            dynamic=False,
            execute_as_generator=False,
            unlisted=False,
            allow_immediate_execution=True,
            allow_delegated_execution=False,
        )

    def resolve_input(self, ctx):
        """Define the input form shown to users"""
        inputs = types.Object()
        # Add input fields
        return types.Property(inputs)

    def resolve_delegation(self, ctx):
        """Decide if this should run in background (optional)"""
        return len(ctx.view) > 1000

    def execute(self, ctx):
        """Main execution logic"""
        # Access parameters: ctx.params["param_name"]
        # Access dataset: ctx.dataset
        # Access view: ctx.view
        return {"result": "value"}

    def resolve_output(self, ctx):
        """Define output display form (optional)"""
        outputs = types.Object()
        outputs.str("result", label="Result")
        return types.Property(outputs)

    def resolve_placement(self, ctx):
        """Add button/menu to App UI (optional)"""
        return types.Placement(
            types.Places.SAMPLES_GRID_ACTIONS,
            types.Button(label="Run", icon="/assets/icon.svg")
        )


def register(p):
    p.register(MyOperator)
```

## OperatorConfig Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | str | Required | Operator URI component (snake_case) |
| `label` | str | Required | Display name in operator browser |
| `description` | str | "" | Description shown in browser |
| `dynamic` | bool | False | Recalculate inputs after changes |
| `execute_as_generator` | bool | False | Yield progress updates |
| `unlisted` | bool | False | Hide from operator browser |
| `allow_immediate_execution` | bool | True | Run synchronously |
| `allow_delegated_execution` | bool | False | Run in background |
| `allow_distributed_execution` | bool | False | Run across workers |

## Execution Context (ctx)

The context object provides access to everything:

```python
def execute(self, ctx):
    # User input parameters
    param = ctx.params["param_name"]

    # Current dataset
    dataset = ctx.dataset

    # Current view (filtered dataset)
    view = ctx.view

    # Selected sample IDs (from App)
    selected = ctx.selected

    # Plugin secrets (from environment)
    api_key = ctx.secrets["API_KEY"]

    # Trigger other operators
    ctx.trigger("@plugin/other_operator", params={})

    # Get target view (respects user selection)
    target = ctx.target_view()

    # Set progress (for generators)
    ctx.set_progress(progress=0.5, label="Processing...")
```

## Input Types Reference

### Basic Types

```python
def resolve_input(self, ctx):
    inputs = types.Object()

    # String input
    inputs.str(
        "text_field",
        label="Text Field",
        description="Enter some text",
        required=True,
        default="default value"
    )

    # Integer input
    inputs.int(
        "number_field",
        label="Number",
        default=10,
        min=0,
        max=100
    )

    # Float input
    inputs.float(
        "float_field",
        label="Decimal",
        default=0.5,
        min=0.0,
        max=1.0
    )

    # Boolean checkbox
    inputs.bool(
        "checkbox_field",
        label="Enable Feature",
        default=True
    )

    return types.Property(inputs)
```

### Selection Types

```python
def resolve_input(self, ctx):
    inputs = types.Object()

    # Dropdown enum
    inputs.enum(
        "choice_field",
        values=["option1", "option2", "option3"],
        label="Select Option",
        default="option1"
    )

    # Radio buttons (enum with radio view)
    inputs.enum(
        "radio_field",
        values=["small", "medium", "large"],
        label="Size",
        view=types.RadioGroup()
    )

    # Multi-select
    inputs.list(
        "multi_select",
        types.String(),
        label="Select Multiple",
        default=[]
    )

    return types.Property(inputs)
```

### Dataset/View Types

```python
def resolve_input(self, ctx):
    inputs = types.Object()

    # Target view selector (current view vs entire dataset)
    inputs.view_target(ctx)

    # Field selector from dataset
    field_choices = types.Dropdown()
    for field in ctx.dataset.get_field_schema():
        field_choices.add_choice(field, label=field)
    inputs.enum(
        "field_name",
        field_choices.values(),
        label="Select Field"
    )

    return types.Property(inputs)
```

### File Types

```python
def resolve_input(self, ctx):
    inputs = types.Object()

    # File upload
    inputs.file(
        "input_file",
        label="Upload File",
        types=[".json", ".csv"]  # Allowed extensions
    )

    # Directory path
    inputs.str(
        "directory",
        label="Directory Path",
        view=types.DirectoryView()
    )

    return types.Property(inputs)
```

### Dynamic Inputs

For inputs that depend on other inputs:

```python
@property
def config(self):
    return foo.OperatorConfig(
        name="dynamic_operator",
        label="Dynamic Operator",
        dynamic=True  # Enable dynamic inputs
    )

def resolve_input(self, ctx):
    inputs = types.Object()

    inputs.enum(
        "operation",
        values=["classify", "detect", "segment"],
        label="Operation Type"
    )

    # Show different inputs based on selection
    operation = ctx.params.get("operation", "classify")

    if operation == "classify":
        inputs.int("num_classes", label="Number of Classes", default=10)
    elif operation == "detect":
        inputs.float("threshold", label="Confidence Threshold", default=0.5)
    elif operation == "segment":
        inputs.bool("include_masks", label="Include Masks", default=True)

    return types.Property(inputs)
```

## Execution Patterns

### Simple Execution

```python
def execute(self, ctx):
    field = ctx.params["field_name"]

    for sample in ctx.view:
        sample[field] = compute_something(sample)
        sample.save()

    return {"processed": len(ctx.view)}
```

### Generator Execution (Progress Updates)

```python
@property
def config(self):
    return foo.OperatorConfig(
        name="progress_operator",
        execute_as_generator=True
    )

def execute(self, ctx):
    total = len(ctx.view)

    for i, sample in enumerate(ctx.view):
        # Process sample
        process(sample)
        sample.save()

        # Yield progress
        yield ctx.set_progress(
            progress=(i + 1) / total,
            label=f"Processing {i + 1}/{total}"
        )

    yield {"status": "complete", "processed": total}
```

### Delegated Execution (Background)

```python
@property
def config(self):
    return foo.OperatorConfig(
        name="background_operator",
        allow_delegated_execution=True,
        allow_immediate_execution=True
    )

def resolve_delegation(self, ctx):
    # Delegate for large datasets
    return len(ctx.view) > 1000

def execute(self, ctx):
    # Same execution logic - runs in background automatically
    for sample in ctx.view:
        process(sample)
        sample.save()
    return {}
```

### Using External APIs

```python
def execute(self, ctx):
    import requests

    # Get API key from secrets
    api_key = ctx.secrets["MY_API_KEY"]

    results = []
    for sample in ctx.view:
        # Call external API
        response = requests.post(
            "https://api.example.com/analyze",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"image_url": sample.filepath}
        )

        # Store results
        sample["api_result"] = response.json()
        sample.save()
        results.append(response.json())

    return {"results": results}
```

## Output Display

```python
def resolve_output(self, ctx):
    outputs = types.Object()

    # Display results from execute()
    result = ctx.results  # Contains return value from execute()

    outputs.str(
        "status",
        label="Status",
        default=result.get("status", "complete")
    )

    outputs.int(
        "count",
        label="Processed Count",
        default=result.get("processed", 0)
    )

    # Markdown for rich output
    outputs.str(
        "summary",
        label="Summary",
        view=types.MarkdownView(),
        default=f"**Processed:** {result.get('processed', 0)} samples"
    )

    return types.Property(outputs)
```

## Placement (UI Buttons)

Add buttons to specific locations in the App:

```python
def resolve_placement(self, ctx):
    return types.Placement(
        types.Places.SAMPLES_GRID_ACTIONS,
        types.Button(
            label="Run My Operator",
            icon="/assets/icon.svg",
            prompt=True  # Show input form
        )
    )
```

### Available Placements

| Placement | Location |
|-----------|----------|
| `SAMPLES_GRID_ACTIONS` | Grid view action bar |
| `SAMPLES_GRID_SECONDARY_ACTIONS` | Grid view secondary actions |
| `SAMPLES_VIEWER_ACTIONS` | Sample viewer actions |
| `EMBEDDINGS_ACTIONS` | Embeddings panel actions |
| `HISTOGRAM_ACTIONS` | Histogram panel actions |
| `MAP_ACTIONS` | Map panel actions |

## Complete Example: Label Exporter

```python
import fiftyone.operators as foo
import fiftyone.operators.types as types
import json
import os


class ExportLabels(foo.Operator):
    @property
    def config(self):
        return foo.OperatorConfig(
            name="export_labels",
            label="Export Labels",
            description="Export labels to JSON file",
            dynamic=True,
            execute_as_generator=True
        )

    def resolve_input(self, ctx):
        inputs = types.Object()

        # Target view selector
        inputs.view_target(ctx)

        # Label field selector
        label_fields = []
        schema = ctx.dataset.get_field_schema()
        for field_name, field in schema.items():
            if hasattr(field, "document_type"):
                label_fields.append(field_name)

        inputs.enum(
            "label_field",
            values=label_fields,
            label="Label Field",
            required=True
        )

        # Output path
        inputs.str(
            "output_path",
            label="Output File Path",
            description="Path to save JSON file",
            required=True,
            default="./labels_export.json"
        )

        # Format options
        inputs.bool(
            "include_filepath",
            label="Include File Paths",
            default=True
        )

        return types.Property(inputs)

    def execute(self, ctx):
        label_field = ctx.params["label_field"]
        output_path = ctx.params["output_path"]
        include_filepath = ctx.params["include_filepath"]

        view = ctx.target_view()
        total = len(view)

        export_data = []

        for i, sample in enumerate(view):
            entry = {
                "id": sample.id,
                "labels": sample[label_field].to_dict() if sample[label_field] else None
            }

            if include_filepath:
                entry["filepath"] = sample.filepath

            export_data.append(entry)

            yield ctx.set_progress(
                progress=(i + 1) / total,
                label=f"Exporting {i + 1}/{total}"
            )

        # Write to file
        output_path = os.path.expanduser(output_path)
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        yield {
            "status": "success",
            "exported": len(export_data),
            "output_path": output_path
        }

    def resolve_output(self, ctx):
        outputs = types.Object()

        result = ctx.results or {}

        outputs.str(
            "message",
            label="Result",
            view=types.MarkdownView(),
            default=f"**Exported {result.get('exported', 0)} samples** to `{result.get('output_path', 'unknown')}`"
        )

        return types.Property(outputs)


def register(p):
    p.register(ExportLabels)
```
