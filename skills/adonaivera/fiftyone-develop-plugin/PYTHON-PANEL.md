# Python Panel Development

## Panel Anatomy

```python
import fiftyone.operators as foo
import fiftyone.operators.types as types


class MyPanel(foo.Panel):
    @property
    def config(self):
        """Panel metadata and configuration"""
        return foo.PanelConfig(
            name="my_panel",
            label="My Panel",
            surfaces="grid",  # "grid", "modal", or "grid modal"
            help_markdown="Panel help documentation"
        )

    def on_load(self, ctx):
        """Initialize panel state when opened"""
        ctx.panel.set_state("counter", 0)
        ctx.panel.set_data("plot_data", None)

    def on_unload(self, ctx):
        """Cleanup when panel is closed (optional)"""
        pass

    def on_change_ctx(self, ctx):
        """React to App context changes (optional)"""
        # Called when dataset, view, or selection changes
        pass

    def on_change_view(self, ctx):
        """React to view changes (optional)"""
        pass

    def on_change_selection(self, ctx):
        """React to selection changes (optional)"""
        pass

    def on_custom_event(self, ctx):
        """Custom event handler"""
        # Define your own events
        pass

    def render(self, ctx):
        """Define panel layout and components"""
        panel = types.Object()

        # Add UI components
        panel.str("message", default="Hello!")

        panel.btn(
            "my_button",
            label="Click Me",
            on_click=self.on_custom_event
        )

        return types.Property(panel)


def register(p):
    p.register(MyPanel)
```

## PanelConfig Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | str | Required | Panel identifier (snake_case) |
| `label` | str | Required | Display name |
| `surfaces` | str | "grid" | Where panel appears: "grid", "modal", "grid modal" |
| `help_markdown` | str | "" | Help documentation for panel |
| `unlisted` | bool | False | Hide from panel list |

### Surface Types

| Surface | Description |
|---------|-------------|
| `"grid"` | Panel appears in grid space alongside samples |
| `"modal"` | Panel opens in modal dialog |
| `"grid modal"` | Panel can appear in either location |

## State vs Data

Panels have two storage mechanisms:

### State (Lightweight)
- Included in every render cycle
- Readable and writable from Python
- Best for small values (counters, flags, selections)

```python
def on_load(self, ctx):
    ctx.panel.set_state("counter", 0)
    ctx.panel.set_state("selected_items", [])

def render(self, ctx):
    panel = types.Object()
    count = ctx.panel.get_state("counter", 0)
    panel.str("display", default=f"Count: {count}")
    return types.Property(panel)
```

### Data (Large Content)
- Stored client-side only
- Write-only from Python (can't read back)
- Best for large data like plots

```python
def on_load(self, ctx):
    # Create a plotly figure
    plot_data = {
        "data": [{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}],
        "layout": {"title": "My Plot"}
    }
    ctx.panel.set_data("my_plot", plot_data)

def render(self, ctx):
    panel = types.Object()
    # Use view() with PlotlyView to display charts
    panel.view("my_plot", types.PlotlyView(data_key="my_plot"))
    return types.Property(panel)
```

## UI Components Reference

### Text Display

```python
def render(self, ctx):
    panel = types.Object()

    # Simple text
    panel.str("label", default="Static text")

    # Markdown
    panel.str(
        "markdown_content",
        view=types.MarkdownView(),
        default="**Bold** and *italic* text"
    )

    # Header
    panel.str(
        "header",
        view=types.Header(),
        default="Section Header"
    )

    return types.Property(panel)
```

### Input Components

```python
def render(self, ctx):
    panel = types.Object()

    # Text input
    panel.str(
        "text_input",
        label="Enter text",
        on_change=self.on_text_change
    )

    # Number input
    panel.int(
        "number_input",
        label="Enter number",
        default=10,
        on_change=self.on_number_change
    )

    # Checkbox
    panel.bool(
        "checkbox",
        label="Enable feature",
        default=False,
        on_change=self.on_checkbox_change
    )

    # Dropdown
    panel.enum(
        "dropdown",
        values=["option1", "option2", "option3"],
        label="Select option",
        on_change=self.on_dropdown_change
    )

    return types.Property(panel)
```

### Buttons

```python
def render(self, ctx):
    panel = types.Object()

    # Standard button
    panel.btn(
        "action_button",
        label="Run Action",
        on_click=self.on_action_click
    )

    # Button with icon
    panel.btn(
        "icon_button",
        label="Download",
        icon="download",
        on_click=self.on_download
    )

    # Disabled button
    is_ready = ctx.panel.get_state("ready", False)
    panel.btn(
        "conditional_button",
        label="Process",
        disabled=not is_ready,
        on_click=self.on_process
    )

    return types.Property(panel)
```

### Layout Containers

```python
def render(self, ctx):
    panel = types.Object()

    # Horizontal layout
    row = panel.h_stack("row1")
    row.str("left", default="Left")
    row.str("right", default="Right")

    # Vertical layout
    col = panel.v_stack("col1")
    col.str("top", default="Top")
    col.str("bottom", default="Bottom")

    # Grid layout
    grid = panel.grid("grid1", columns=2)
    grid.str("cell1", default="Cell 1")
    grid.str("cell2", default="Cell 2")
    grid.str("cell3", default="Cell 3")
    grid.str("cell4", default="Cell 4")

    return types.Property(panel)
```

### Data Visualization

**Note:** Python panels have limited visualization capabilities. For rich media display (images, videos, thumbnails), use JavaScript panels instead.

```python
def render(self, ctx):
    panel = types.Object()

    # Plotly chart (requires data set via set_data)
    # Use panel.view() with PlotlyView for charts
    panel.view(
        "chart",
        types.PlotlyView(data_key="chart_data")
    )

    # For displaying file paths or sample info, use markdown
    filepath = ctx.panel.get_state("filepath", "")
    if filepath:
        import os
        panel.str(
            "file_info",
            view=types.MarkdownView(),
            default=f"**File:** `{os.path.basename(filepath)}`"
        )

    return types.Property(panel)
```

**Limitations:**
- `panel.media()`, `panel.image()`, `panel.table()` do NOT exist
- For image thumbnails or media preview, use JavaScript panels
- For tables, format data as markdown or use PlotlyView with table trace

## Event Handlers

### Built-in Events

```python
def on_load(self, ctx):
    """Called when panel opens"""
    ctx.panel.set_state("initialized", True)

def on_unload(self, ctx):
    """Called when panel closes"""
    pass

def on_change_ctx(self, ctx):
    """Called when App context changes (dataset, view, selection)"""
    ctx.panel.set_state("dataset_name", ctx.dataset.name)

def on_change_view(self, ctx):
    """Called when view changes"""
    ctx.panel.set_state("view_count", len(ctx.view))

def on_change_selection(self, ctx):
    """Called when sample selection changes"""
    ctx.panel.set_state("selected_count", len(ctx.selected))
```

### Custom Events

```python
def on_button_click(self, ctx):
    """Custom click handler"""
    count = ctx.panel.get_state("counter", 0)
    ctx.panel.set_state("counter", count + 1)

def on_input_change(self, ctx):
    """Custom change handler"""
    # Get the new value from the event
    value = ctx.params.get("value")
    ctx.panel.set_state("input_value", value)

def on_select_sample(self, ctx):
    """Handle sample selection"""
    sample_id = ctx.params.get("sample_id")
    if sample_id:
        ctx.ops.set_selected([sample_id])
```

## Triggering Operators

Panels can trigger operators:

```python
def on_run_operator(self, ctx):
    """Trigger an operator from panel"""
    ctx.trigger(
        "@voxel51/brain/compute_similarity",
        params={
            "brain_key": "my_similarity",
            "model": "clip-vit-base32-torch"
        }
    )
```

## Using Execution Store

Store data beyond panel lifetime:

```python
def on_load(self, ctx):
    store = ctx.store("my_panel_store")

    # Retrieve previous state
    saved_config = store.get("config")
    if saved_config:
        ctx.panel.set_state("config", saved_config)

def on_save_config(self, ctx):
    store = ctx.store("my_panel_store")
    config = ctx.panel.get_state("config", {})

    # Save with TTL (60 seconds)
    store.set("config", config, ttl=60)
```

## Complete Example: Sample Statistics Panel

```python
import fiftyone.operators as foo
import fiftyone.operators.types as types


class StatisticsPanel(foo.Panel):
    @property
    def config(self):
        return foo.PanelConfig(
            name="statistics_panel",
            label="Sample Statistics",
            surfaces="grid",
            help_markdown="View dataset statistics"
        )

    def on_load(self, ctx):
        """Initialize panel"""
        self._update_stats(ctx)

    def on_change_view(self, ctx):
        """Update stats when view changes"""
        self._update_stats(ctx)

    def _update_stats(self, ctx):
        """Calculate and store statistics"""
        view = ctx.view

        # Basic counts
        total_samples = len(view)
        ctx.panel.set_state("total_samples", total_samples)

        # Get label field stats if available
        label_counts = {}
        schema = ctx.dataset.get_field_schema()

        for field_name, field in schema.items():
            if hasattr(field, "document_type"):
                if "Detection" in str(field.document_type):
                    counts = view.count_values(f"{field_name}.detections.label")
                    label_counts[field_name] = dict(counts)

        ctx.panel.set_state("label_counts", label_counts)

        # Create plot data
        if label_counts:
            first_field = list(label_counts.keys())[0]
            counts = label_counts[first_field]
            plot_data = {
                "data": [{
                    "x": list(counts.keys()),
                    "y": list(counts.values()),
                    "type": "bar"
                }],
                "layout": {
                    "title": f"Label Distribution ({first_field})",
                    "xaxis": {"title": "Label"},
                    "yaxis": {"title": "Count"}
                }
            }
            ctx.panel.set_data("label_plot", plot_data)

    def on_refresh(self, ctx):
        """Manual refresh button"""
        self._update_stats(ctx)

    def on_field_change(self, ctx):
        """Handle field selection change"""
        selected_field = ctx.params.get("value")
        label_counts = ctx.panel.get_state("label_counts", {})

        if selected_field in label_counts:
            counts = label_counts[selected_field]
            plot_data = {
                "data": [{
                    "x": list(counts.keys()),
                    "y": list(counts.values()),
                    "type": "bar"
                }],
                "layout": {
                    "title": f"Label Distribution ({selected_field})",
                    "xaxis": {"title": "Label"},
                    "yaxis": {"title": "Count"}
                }
            }
            ctx.panel.set_data("label_plot", plot_data)

    def render(self, ctx):
        panel = types.Object()

        # Header
        panel.str(
            "header",
            view=types.Header(),
            default="Dataset Statistics"
        )

        # Sample count
        total = ctx.panel.get_state("total_samples", 0)
        panel.str(
            "count_display",
            view=types.MarkdownView(),
            default=f"**Total Samples:** {total}"
        )

        # Field selector
        label_counts = ctx.panel.get_state("label_counts", {})
        if label_counts:
            panel.enum(
                "field_selector",
                values=list(label_counts.keys()),
                label="Label Field",
                on_change=self.on_field_change
            )

            # Plot (using view with PlotlyView)
            panel.view("label_plot", types.PlotlyView(data_key="label_plot"))

        # Refresh button
        panel.btn(
            "refresh_btn",
            label="Refresh Statistics",
            icon="refresh",
            on_click=self.on_refresh
        )

        return types.Property(panel)


def register(p):
    p.register(StatisticsPanel)
```
