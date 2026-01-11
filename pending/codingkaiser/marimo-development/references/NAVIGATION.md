# References Navigation Guide

This guide helps you navigate the marimo documentation references and know when to read each file.

## Quick Start

- **core-concepts.md** - ALWAYS READ THIS FIRST. Contains marimo fundamentals, cell structure, reactivity basics, UI elements, and examples.

## Core Guides

Read these for understanding marimo's key concepts:

- **reactivity.md** - Deep dive into marimo's reactive execution model, how cells re-run automatically, and lazy evaluation
- **interactivity.md** - How to create interactive UIs with sliders, dropdowns, forms, and other UI elements
- **best_practices.md** - Coding best practices for marimo notebooks

## Common Tasks & Recipes

- **recipes.md** - Code snippets for common tasks (control flow, working with data, layouts, state management, etc.)
- **faq.md** - Frequently asked questions about marimo vs Jupyter, common issues, and solutions

## Working with Data

See `working_with_data/` directory:
- **working_with_data/sql.md** - Using SQL with DuckDB and other databases
- **working_with_data/dataframes.md** - Working with pandas, polars, and other dataframe libraries
- **working_with_data/plotting.md** - Creating visualizations with matplotlib, plotly, altair, etc.

## Deploying & Running

- **apps.md** - Deploy marimo notebooks as interactive web apps
- **scripts.md** - Run marimo notebooks as Python scripts with CLI arguments

## Troubleshooting

- **debugging.md** - Debugging techniques for marimo notebooks
- **troubleshooting.md** - Common errors and how to fix them

## API Reference

See `api/` directory for detailed API documentation:

### Most Used APIs

- **api/inputs/** - All UI input elements (sliders, dropdowns, buttons, tables, etc.)
  - See `api/inputs/index.md` for complete list
  - Each input has its own file (e.g., `api/inputs/slider.md`, `api/inputs/dropdown.md`)

- **api/layouts/** - Layout components (tabs, accordions, grids, sidebars, etc.)
  - See `api/layouts/index.md` for complete list

- **api/control_flow.md** - Cell execution control (mo.stop, mo.output.replace, etc.)
- **api/html.md** - HTML manipulation and display
- **api/markdown.md** - Markdown rendering with mo.md()
- **api/state.md** - State management for complex interactions
- **api/caching.md** - Caching expensive computations

### Other APIs

- **api/media/** - Images, audio, video, PDFs
- **api/diagrams.md** - Flow charts, graphs, cards
- **api/plotting.md** - Interactive plotting utilities
- **api/app.md** - Embedding notebooks in notebooks
- **api/cli_args.md** - Accessing command-line arguments
- **api/query_params.md** - URL query parameter handling

## Reading Strategy

1. Start with **core-concepts.md** for fundamentals
2. Use **recipes.md** for quick code snippets for common tasks
3. Refer to specific API docs in `api/` when you need details about a specific function
4. Check **faq.md** and **troubleshooting.md** for common issues
5. Read domain-specific guides (reactivity, interactivity, data handling) as needed
