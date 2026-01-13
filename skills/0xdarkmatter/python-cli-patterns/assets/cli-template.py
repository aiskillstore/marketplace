"""
CLI Application Template

A production-ready CLI application structure.

Usage:
    python cli.py --help
    python cli.py greet "World"
    python cli.py config init
"""

import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

# =============================================================================
# App Setup
# =============================================================================

app = typer.Typer(
    name="myapp",
    help="My awesome CLI application",
    no_args_is_help=True,
    add_completion=True,
    rich_markup_mode="rich",
)

console = Console()
err_console = Console(stderr=True)

# Sub-applications
config_app = typer.Typer(help="Configuration commands")
app.add_typer(config_app, name="config")


# =============================================================================
# State and Configuration
# =============================================================================

class AppState:
    """Application state shared across commands."""

    def __init__(self):
        self.verbose: bool = False
        self.config_dir: Path = Path.home() / ".config" / "myapp"
        self.config_file: Path = self.config_dir / "config.toml"


state = AppState()


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Config file path"
    ),
):
    """
    [bold blue]MyApp[/bold blue] - A sample CLI application.

    Use [green]--help[/green] on any command for more info.
    """
    state.verbose = verbose
    if config:
        state.config_file = config


# =============================================================================
# Utility Functions
# =============================================================================

def log(message: str, style: str = ""):
    """Log message if verbose mode is enabled."""
    if state.verbose:
        console.print(f"[dim]{message}[/dim]", style=style)


def error(message: str, code: int = 1) -> None:
    """Print error and exit."""
    err_console.print(f"[red]Error:[/red] {message}")
    raise typer.Exit(code)


def success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


# =============================================================================
# Commands
# =============================================================================

@app.command()
def greet(
    name: Annotated[str, typer.Argument(help="Name to greet")],
    count: Annotated[int, typer.Option("--count", "-n", help="Times to greet")] = 1,
    loud: Annotated[bool, typer.Option("--loud", "-l", help="Uppercase")] = False,
):
    """
    Say hello to someone.

    Example:
        myapp greet World
        myapp greet World --count 3 --loud
    """
    message = f"Hello, {name}!"
    if loud:
        message = message.upper()

    for _ in range(count):
        console.print(message)


@app.command()
def process(
    files: Annotated[
        list[Path],
        typer.Argument(
            help="Files to process",
            exists=True,
            readable=True,
        ),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output file"),
    ] = None,
):
    """
    Process one or more files.

    Example:
        myapp process file1.txt file2.txt -o output.txt
    """
    log(f"Processing {len(files)} files")

    results = []
    for file in track(files, description="Processing..."):
        log(f"Processing: {file}")
        # Simulate processing
        results.append(f"Processed: {file.name}")

    if output:
        output.write_text("\n".join(results))
        success(f"Results written to {output}")
    else:
        for result in results:
            console.print(result)


@app.command()
def status():
    """Show application status."""
    table = Table(title="Application Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Config Dir", str(state.config_dir))
    table.add_row("Config File", str(state.config_file))
    table.add_row("Verbose", str(state.verbose))
    table.add_row(
        "Config Exists",
        "✓" if state.config_file.exists() else "✗"
    )

    console.print(table)


# =============================================================================
# Config Subcommands
# =============================================================================

@config_app.command("init")
def config_init(
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing"),
    ] = False,
):
    """Initialize configuration file."""
    if state.config_file.exists() and not force:
        if not typer.confirm(f"Config exists at {state.config_file}. Overwrite?"):
            raise typer.Abort()

    state.config_dir.mkdir(parents=True, exist_ok=True)

    default_config = """
# MyApp Configuration
# See documentation for all options

[general]
verbose = false

[server]
host = "localhost"
port = 8080
""".strip()

    state.config_file.write_text(default_config)
    success(f"Created config: {state.config_file}")


@config_app.command("show")
def config_show():
    """Show current configuration."""
    if not state.config_file.exists():
        error(f"Config not found: {state.config_file}")

    content = state.config_file.read_text()
    console.print(Panel(content, title=str(state.config_file), border_style="blue"))


@config_app.command("path")
def config_path():
    """Print config file path."""
    typer.echo(state.config_file)


# =============================================================================
# Version
# =============================================================================

def version_callback(value: bool):
    if value:
        console.print("myapp version [bold]1.0.0[/bold]")
        raise typer.Exit()


@app.callback()
def version_option(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version",
        ),
    ] = False,
):
    pass


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    app()
