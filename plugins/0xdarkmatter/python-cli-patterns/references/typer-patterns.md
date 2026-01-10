# Advanced Typer Patterns

Modern CLI development patterns with Typer.

## Application Structure

```python
import typer
from typing import Optional
from enum import Enum

# Create app with metadata
app = typer.Typer(
    name="myapp",
    help="My CLI application",
    add_completion=True,
    no_args_is_help=True,  # Show help if no command given
    rich_markup_mode="rich",  # Enable Rich formatting in help
)

# State object for shared options
class State:
    def __init__(self):
        self.verbose: bool = False
        self.config_path: str = ""

state = State()


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    config: str = typer.Option("config.yaml", "--config", "-c", help="Config file"),
):
    """
    My awesome CLI application.

    Use --help on any command for more info.
    """
    state.verbose = verbose
    state.config_path = config
```

## Type-Safe Arguments

```python
from typing import Annotated
from enum import Enum
from pathlib import Path

class OutputFormat(str, Enum):
    json = "json"
    yaml = "yaml"
    table = "table"

@app.command()
def export(
    # Required argument
    query: Annotated[str, typer.Argument(help="Search query")],

    # Optional argument with default
    limit: Annotated[int, typer.Argument()] = 10,

    # Path validation
    output: Annotated[
        Path,
        typer.Option(
            "--output", "-o",
            help="Output file path",
            exists=False,  # Must not exist
            file_okay=True,
            dir_okay=False,
            writable=True,
            resolve_path=True,
        )
    ] = None,

    # Input file (must exist)
    input_file: Annotated[
        Path,
        typer.Option(
            "--input", "-i",
            exists=True,  # Must exist
            readable=True,
        )
    ] = None,

    # Enum choices
    format: Annotated[
        OutputFormat,
        typer.Option("--format", "-f", case_sensitive=False)
    ] = OutputFormat.table,

    # Multiple values
    tags: Annotated[
        list[str],
        typer.Option("--tag", "-t", help="Tags to filter")
    ] = None,
):
    """Export data with various options."""
    typer.echo(f"Query: {query}, Format: {format.value}")
```

## Interactive Prompts

```python
import typer

@app.command()
def create_user():
    """Create a new user interactively."""
    # Text prompt
    name = typer.prompt("What's your name?")

    # With default
    email = typer.prompt("Email", default=f"{name.lower()}@example.com")

    # Hidden input (password)
    password = typer.prompt("Password", hide_input=True)

    # Confirmation
    password_confirm = typer.prompt("Confirm password", hide_input=True)
    if password != password_confirm:
        typer.echo("Passwords don't match!")
        raise typer.Abort()

    # Yes/No confirmation
    if typer.confirm("Create this user?"):
        typer.echo(f"Creating user: {name}")
    else:
        typer.echo("Cancelled")
        raise typer.Abort()


# Non-interactive with --yes flag
@app.command()
def delete_all(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Delete all items."""
    if not yes:
        yes = typer.confirm("Are you sure?")
    if yes:
        typer.echo("Deleting...")
    else:
        raise typer.Abort()
```

## Context and Dependency Injection

```python
import typer
from typing import Annotated

# Create a context type
class Context:
    def __init__(self, db_url: str, debug: bool):
        self.db_url = db_url
        self.debug = debug
        self.db = None

    def connect(self):
        self.db = create_connection(self.db_url)

# Store in typer context
@app.callback()
def main(
    ctx: typer.Context,
    db_url: str = typer.Option("sqlite:///app.db", envvar="DATABASE_URL"),
    debug: bool = typer.Option(False, "--debug"),
):
    """Initialize application context."""
    ctx.obj = Context(db_url=db_url, debug=debug)
    ctx.obj.connect()


@app.command()
def query(
    ctx: typer.Context,
    sql: str,
):
    """Run a SQL query."""
    result = ctx.obj.db.execute(sql)
    for row in result:
        typer.echo(row)
```

## Subcommands and Nested Apps

```python
import typer

# Main app
app = typer.Typer()

# Sub-applications
db_app = typer.Typer(help="Database operations")
cache_app = typer.Typer(help="Cache operations")

# Register sub-apps
app.add_typer(db_app, name="db")
app.add_typer(cache_app, name="cache")

@db_app.command("migrate")
def db_migrate():
    """Run database migrations."""
    typer.echo("Running migrations...")

@db_app.command("seed")
def db_seed():
    """Seed database with test data."""
    typer.echo("Seeding database...")

@cache_app.command("clear")
def cache_clear():
    """Clear cache."""
    typer.echo("Clearing cache...")

# Usage:
# myapp db migrate
# myapp db seed
# myapp cache clear
```

## Async Commands

```python
import typer
import asyncio

app = typer.Typer()

async def async_operation():
    await asyncio.sleep(1)
    return "Done"

@app.command()
def fetch():
    """Fetch data asynchronously."""
    result = asyncio.run(async_main())
    typer.echo(result)

async def async_main():
    results = await asyncio.gather(
        async_operation(),
        async_operation(),
    )
    return results
```

## Testing CLI Apps

```python
from typer.testing import CliRunner
import pytest

runner = CliRunner()

def test_hello():
    result = runner.invoke(app, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.stdout

def test_hello_with_options():
    result = runner.invoke(app, ["hello", "World", "--count", "3", "--loud"])
    assert result.exit_code == 0
    assert "HELLO, WORLD!" in result.stdout
    assert result.stdout.count("HELLO") == 3

def test_invalid_input():
    result = runner.invoke(app, ["process", "nonexistent.txt"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


# With environment variables
def test_with_env():
    result = runner.invoke(
        app,
        ["connect"],
        env={"DATABASE_URL": "sqlite:///test.db"}
    )
    assert result.exit_code == 0
```

## Quick Reference

| Pattern | Syntax |
|---------|--------|
| App callback | `@app.callback()` for global options |
| Context | `ctx: typer.Context` + `ctx.obj` |
| Envvar | `typer.Option(envvar="VAR_NAME")` |
| Prompt | `typer.prompt("Question")` |
| Confirm | `typer.confirm("Sure?")` |
| Abort | `raise typer.Abort()` |
| Exit | `raise typer.Exit(code=1)` |
| Progress | Use Rich `track()` |

| Decorator | Purpose |
|-----------|---------|
| `@app.command()` | Define a command |
| `@app.callback()` | App initialization |
| `@sub_app.command()` | Subcommand |
