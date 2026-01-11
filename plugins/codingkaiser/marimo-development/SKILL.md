---
name: marimo-development
description: Expert guidance for creating and working with marimo notebooks - reactive Python notebooks that can be executed as scripts and deployed as apps. Use when the user asks to create marimo notebooks, convert Jupyter notebooks to marimo, build interactive dashboards or data apps with marimo, work with marimo's reactive programming model, debug marimo notebooks, or needs help with marimo-specific features (cells, UI elements, reactivity, SQL integration, deploying apps, etc.).
---

# Marimo Development

Create reactive Python notebooks with marimo's interactive programming environment.

## Core Workflow

1. **Start with fundamentals**: Read `references/core-concepts.md` - contains marimo's cell structure, reactivity model, UI elements, and essential examples
2. **Use recipes for common tasks**: Check `references/recipes.md` for code snippets
3. **Refer to API docs**: Navigate `references/api/` for specific function details
4. **Troubleshoot issues**: See `references/faq.md` and `references/troubleshooting.md`

## Key Marimo Concepts

### Cell Structure

Every marimo cell follows this structure:

```python
@app.cell
def _():
    # Your code here
    return
```

When editing cells, only modify the code inside the function - marimo handles parameters and returns automatically.

### Reactivity Rules

1. **Automatic execution**: When a variable changes, cells using it automatically re-run
2. **No redeclaration**: Variables cannot be redeclared across cells
3. **DAG structure**: Cells form a directed acyclic graph (no circular dependencies)
4. **Last expression displays**: The final expression in a cell is automatically shown
5. **UI reactivity**: UI element values accessed via `.value` trigger automatic updates
6. **Local variables**: Variables prefixed with `_` (e.g., `_temp`) are local to the cell

### Import Pattern

Always import marimo in the first cell:

```python
@app.cell
def _():
    import marimo as mo
    # other imports
    return
```

## Common Tasks

### Creating Interactive UIs

```python
# Create UI element in one cell
@app.cell
def _():
    slider = mo.ui.slider(0, 100, value=50, label="Value")
    slider
    return

# Use its value in another cell
@app.cell
def _():
    result = slider.value * 2
    mo.md(f"Double the value: {result}")
    return
```

### Working with Data

```python
# Load and display data
@app.cell
def _():
    import polars as pl
    df = pl.read_csv("data.csv")
    df  # Automatically displays as table
    return

# Interactive data exploration
@app.cell
def _():
    mo.ui.data_explorer(df)
    return
```

### SQL with DuckDB

```python
@app.cell
def _():
    # marimo has built-in DuckDB support
    result = mo.sql(f"""
        SELECT * FROM df WHERE column > 100
    """)
    return
```

### Layouts

```python
@app.cell
def _():
    # Horizontal stack
    mo.hstack([element1, element2, element3])

    # Vertical stack
    mo.vstack([top, middle, bottom])

    # Tabs
    mo.tabs({"Tab 1": content1, "Tab 2": content2})
    return
```

## Visualization Best Practices

- **matplotlib**: Use `plt.gca()` as last expression (not `plt.show()`)
- **plotly**: Return the figure object directly
- **altair**: Return the chart object; add tooltips; accepts polars dataframes directly

## Reference Documentation

Use `references/NAVIGATION.md` to understand the complete documentation structure. Key references:

### Essential Reading
- **core-concepts.md** - Start here for fundamentals and examples
- **recipes.md** - Code snippets for common tasks

### Detailed Guides
- **reactivity.md** - Deep dive into reactive execution
- **interactivity.md** - Building interactive UIs
- **best_practices.md** - Coding standards for marimo

### Working with Data
- **working_with_data/sql.md** - SQL and DuckDB integration
- **working_with_data/dataframes.md** - pandas, polars, etc.
- **working_with_data/plotting.md** - Visualization libraries

### Deployment
- **apps.md** - Deploy as interactive web apps
- **scripts.md** - Run as Python scripts with CLI args

### API Reference
- **api/inputs/** - All UI elements (slider, dropdown, button, table, etc.)
- **api/layouts/** - Layout components (tabs, accordion, sidebar, etc.)
- **api/control_flow.md** - Cell execution control
- **api/state.md** - State management
- **api/caching.md** - Performance optimization

### Troubleshooting
- **faq.md** - Common questions and solutions
- **troubleshooting.md** - Error fixes
- **debugging.md** - Debugging techniques

## Common Pitfalls

1. **Circular dependencies**: Reorganize code to remove cycles
2. **UI value access**: Can't access `.value` in the same cell where UI element is defined
3. **Variable redeclaration**: Each variable can only be defined once across all cells
4. **Visualization not showing**: Ensure visualization object is the last expression
5. **Global keyword**: Never use `global` - violates marimo's execution model

## After Creating a Notebook

Run `marimo check --fix` to automatically catch and fix common formatting issues and detect pitfalls.

## Quick Reference: Most Used UI Elements

```python
mo.ui.slider(start, stop, value=None, label=None)
mo.ui.dropdown(options, value=None, label=None)
mo.ui.text(value='', label=None)
mo.ui.button(value=None, kind='primary')
mo.ui.checkbox(label='', value=False)
mo.ui.table(data, sortable=True, filterable=True)
mo.ui.data_explorer(df)  # Interactive dataframe explorer
mo.ui.dataframe(df)  # Editable dataframe
mo.ui.form(element, label='')  # Wrap elements in a form
mo.ui.array(elements)  # Array of UI elements
```

See `references/api/inputs/index.md` for the complete list.

## Quick Reference: Layout Functions

```python
mo.md(text)  # Display markdown
mo.hstack(elements)  # Horizontal layout
mo.vstack(elements)  # Vertical layout
mo.tabs(dict)  # Tabbed interface
mo.stop(predicate, output=None)  # Conditional execution
mo.output.append(value)  # Append to output
mo.output.replace(value)  # Replace output
```

See `references/api/layouts/index.md` for all layout options.
