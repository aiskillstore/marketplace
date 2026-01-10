---
name: python-cli-patterns
description: "CLI application patterns for Python. Triggers on: cli, command line, typer, click, argparse, terminal, rich, console, terminal ui."
compatibility: "Python 3.10+. Requires typer and rich for modern CLI development."
allowed-tools: "Read Write Bash"
depends-on: []
related-skills: [python-typing-patterns, python-observability-patterns]
---

# Python CLI Patterns

Modern CLI development with Typer and Rich.

## Basic Typer App

```python
import typer

app = typer.Typer(
    name="myapp",
    help="My awesome CLI application",
    add_completion=True,
)

@app.command()
def hello(
    name: str = typer.Argument(..., help="Name to greet"),
    count: int = typer.Option(1, "--count", "-c", help="Times to greet"),
    loud: bool = typer.Option(False, "--loud", "-l", help="Uppercase"),
):
    """Say hello to someone."""
    message = f"Hello, {name}!"
    if loud:
        message = message.upper()
    for _ in range(count):
        typer.echo(message)

if __name__ == "__main__":
    app()
```

## Command Groups

```python
import typer

app = typer.Typer()
users_app = typer.Typer(help="User management commands")
app.add_typer(users_app, name="users")

@users_app.command("list")
def list_users():
    """List all users."""
    typer.echo("Listing users...")

@users_app.command("create")
def create_user(name: str, email: str):
    """Create a new user."""
    typer.echo(f"Creating user: {name} <{email}>")

@app.command()
def version():
    """Show version."""
    typer.echo("1.0.0")

# Usage: myapp users list
#        myapp users create "John" "john@example.com"
#        myapp version
```

## Rich Output

```python
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
import typer

console = Console()

@app.command()
def show_users():
    """Display users in a table."""
    table = Table(title="Users")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Email")

    users = [
        (1, "Alice", "alice@example.com"),
        (2, "Bob", "bob@example.com"),
    ]
    for id, name, email in users:
        table.add_row(str(id), name, email)

    console.print(table)

@app.command()
def process():
    """Process items with progress bar."""
    items = list(range(100))
    for item in track(items, description="Processing..."):
        do_something(item)
    console.print("[green]Done![/green]")
```

## Error Handling

```python
import typer
from rich.console import Console

console = Console()

def error(message: str, code: int = 1):
    """Print error and exit."""
    console.print(f"[red]Error:[/red] {message}")
    raise typer.Exit(code)

@app.command()
def process(file: str):
    """Process a file."""
    if not os.path.exists(file):
        error(f"File not found: {file}")

    try:
        result = process_file(file)
        console.print(f"[green]Success:[/green] {result}")
    except ValueError as e:
        error(str(e))
```

## Quick Reference

| Feature | Typer Syntax |
|---------|--------------|
| Required arg | `name: str` |
| Optional arg | `name: str = "default"` |
| Option | `typer.Option(default, "--flag", "-f")` |
| Argument | `typer.Argument(..., help="...")` |
| Boolean flag | `verbose: bool = False` |
| Enum choice | `color: Color = Color.red` |

| Rich Feature | Usage |
|--------------|-------|
| Table | `Table()` + `add_column/row` |
| Progress | `track(items)` |
| Colors | `[red]text[/red]` |
| Panel | `Panel("content", title="Title")` |

## Additional Resources

- `./references/typer-patterns.md` - Advanced Typer patterns
- `./references/rich-output.md` - Rich tables, progress, formatting
- `./references/configuration.md` - Config files, environment variables

## Assets

- `./assets/cli-template.py` - Full CLI application template

---

## See Also

**Related Skills:**
- `python-typing-patterns` - Type hints for CLI arguments
- `python-observability-patterns` - Logging for CLI applications

**Complementary Skills:**
- `python-env` - Package CLI for distribution
