# Rich Terminal Output

Beautiful CLI output with Rich.

## Console Basics

```python
from rich.console import Console
from rich.text import Text

console = Console()

# Basic printing
console.print("Hello, World!")

# With styling
console.print("Hello", style="bold red")
console.print("[bold blue]Bold blue[/bold blue] and [green]green[/green]")

# Print objects (auto-formatting)
console.print({"key": "value", "list": [1, 2, 3]})

# Print to stderr
console.print("Error!", style="red", file=sys.stderr)

# Width control
console.print("Text", width=40, justify="center")
```

## Tables

```python
from rich.table import Table
from rich.console import Console

console = Console()

# Basic table
table = Table(title="Users")
table.add_column("ID", style="cyan", justify="right")
table.add_column("Name", style="green")
table.add_column("Email")
table.add_column("Active", justify="center")

table.add_row("1", "Alice", "alice@example.com", "✓")
table.add_row("2", "Bob", "bob@example.com", "✓")
table.add_row("3", "Charlie", "charlie@example.com", "✗")

console.print(table)


# Table with styling
table = Table(
    title="Report",
    show_header=True,
    header_style="bold magenta",
    border_style="blue",
    box=box.DOUBLE,
)


# Dynamic table from data
def print_users(users: list[dict]):
    table = Table()
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Status")

    for user in users:
        status = "[green]Active[/green]" if user["active"] else "[red]Inactive[/red]"
        table.add_row(str(user["id"]), user["name"], status)

    console.print(table)
```

## Progress Bars

```python
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    track,
)
from rich.console import Console

console = Console()

# Simple progress with track()
for item in track(items, description="Processing..."):
    process(item)


# Customizable progress
with Progress(
    SpinnerColumn(),
    TextColumn("[bold blue]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
    console=console,
) as progress:
    task = progress.add_task("Downloading...", total=100)

    for i in range(100):
        do_work()
        progress.update(task, advance=1)


# Multiple tasks
with Progress() as progress:
    download_task = progress.add_task("Downloading", total=1000)
    process_task = progress.add_task("Processing", total=500)

    while not progress.finished:
        progress.update(download_task, advance=10)
        progress.update(process_task, advance=5)
        time.sleep(0.01)


# Indeterminate spinner
with console.status("[bold green]Working...") as status:
    while not done:
        do_something()
        status.update("[bold green]Still working...")
```

## Panels and Layout

```python
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console

console = Console()

# Basic panel
console.print(Panel("Hello, World!", title="Greeting", border_style="green"))

# Panel with rich content
console.print(Panel(
    "[bold]Important Message[/bold]\n\n"
    "This is a [red]warning[/red] message.",
    title="Alert",
    subtitle="Action Required",
    border_style="red",
))


# Layout for complex UIs
layout = Layout()
layout.split(
    Layout(name="header", size=3),
    Layout(name="main"),
    Layout(name="footer", size=3),
)

layout["header"].update(Panel("My CLI App", style="bold"))
layout["main"].split_row(
    Layout(name="left"),
    Layout(name="right"),
)
layout["footer"].update(Panel("Press Ctrl+C to exit"))

console.print(layout)
```

## Markdown and Syntax

```python
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.console import Console

console = Console()

# Render markdown
md = Markdown("""
# Title

This is **bold** and *italic*.

- Item 1
- Item 2

```python
print("Hello")
```
""")
console.print(md)


# Syntax highlighting
code = '''
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"
'''

syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
console.print(syntax)


# From file
syntax = Syntax.from_path("script.py", line_numbers=True)
console.print(syntax)
```

## Trees

```python
from rich.tree import Tree
from rich.console import Console

console = Console()

tree = Tree("[bold]Project Structure")
src = tree.add("[blue]src/")
src.add("main.py")
src.add("utils.py")
src.add("[blue]models/").add("user.py")

tests = tree.add("[blue]tests/")
tests.add("test_main.py")

console.print(tree)
```

## Live Display

```python
from rich.live import Live
from rich.table import Table
from rich.console import Console
import time

console = Console()

def generate_table(count: int) -> Table:
    table = Table()
    table.add_column("Count")
    table.add_column("Status")
    table.add_row(str(count), "Processing...")
    return table

with Live(generate_table(0), console=console, refresh_per_second=4) as live:
    for i in range(100):
        time.sleep(0.1)
        live.update(generate_table(i))
```

## Logging Integration

```python
from rich.logging import RichHandler
import logging

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("my_app")
logger.info("Hello, World!")
logger.warning("This is a warning")
logger.error("Something went wrong")
```

## Quick Reference

| Component | Usage |
|-----------|-------|
| `console.print()` | Print with styling |
| `Table()` | Tabular data |
| `track()` | Simple progress bar |
| `Progress()` | Custom progress |
| `Panel()` | Bordered content |
| `Syntax()` | Code highlighting |
| `Markdown()` | Render markdown |
| `Tree()` | Hierarchical data |
| `Live()` | Dynamic updates |

| Markup | Effect |
|--------|--------|
| `[bold]text[/bold]` | Bold |
| `[red]text[/red]` | Red color |
| `[link=url]text[/link]` | Hyperlink |
| `[dim]text[/dim]` | Dimmed |
