# CLI Configuration Patterns

Configuration file and environment variable handling.

## Environment Variables

```python
import os
import typer

app = typer.Typer()

@app.command()
def connect(
    # Read from env var with fallback
    host: str = typer.Option(
        "localhost",
        envvar="DB_HOST",
        help="Database host",
    ),
    port: int = typer.Option(
        5432,
        envvar="DB_PORT",
        help="Database port",
    ),
    # Multiple envvars (first found wins)
    password: str = typer.Option(
        ...,  # Required
        envvar=["DB_PASSWORD", "DATABASE_PASSWORD", "PGPASSWORD"],
        help="Database password",
    ),
):
    """Connect to database."""
    typer.echo(f"Connecting to {host}:{port}")
```

## Configuration File with TOML

```python
import tomllib  # Python 3.11+
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    log_level: str = "INFO"

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        """Load config from TOML file."""
        if path is None:
            # Search default locations
            for p in [
                Path("config.toml"),
                Path.home() / ".config" / "myapp" / "config.toml",
            ]:
                if p.exists():
                    path = p
                    break

        if path and path.exists():
            with open(path, "rb") as f:
                data = tomllib.load(f)
                return cls(**data)

        return cls()


# Usage in CLI
@app.callback()
def main(
    ctx: typer.Context,
    config: Path = typer.Option(
        None,
        "--config", "-c",
        exists=True,
        help="Config file path",
    ),
):
    ctx.obj = Config.load(config)


@app.command()
def serve(ctx: typer.Context):
    config = ctx.obj
    typer.echo(f"Starting on {config.host}:{config.port}")
```

## Config with Pydantic Settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    """Application settings from env vars and config file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="MYAPP_",  # MYAPP_HOST, MYAPP_PORT
        case_sensitive=False,
    )

    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    database_url: str = Field(
        default="sqlite:///app.db",
        validation_alias="DATABASE_URL",  # Also check DATABASE_URL without prefix
    )
    api_key: str = Field(default="")


# Load once
settings = Settings()

@app.command()
def serve():
    typer.echo(f"Host: {settings.host}")
    typer.echo(f"Debug: {settings.debug}")
```

## XDG Config Directories

```python
from pathlib import Path
import os

def get_config_dir(app_name: str) -> Path:
    """Get XDG-compliant config directory."""
    if os.name == "nt":  # Windows
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:  # Linux/macOS
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    config_dir = base / app_name
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_data_dir(app_name: str) -> Path:
    """Get XDG-compliant data directory."""
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    data_dir = base / app_name
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_cache_dir(app_name: str) -> Path:
    """Get XDG-compliant cache directory."""
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "cache"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))

    cache_dir = base / app_name
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
```

## Config Init Command

```python
import typer
from pathlib import Path

@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """Initialize configuration file."""
    config_dir = get_config_dir("myapp")
    config_file = config_dir / "config.toml"

    if config_file.exists() and not force:
        typer.echo(f"Config already exists: {config_file}")
        if not typer.confirm("Overwrite?"):
            raise typer.Abort()

    default_config = """
# MyApp Configuration

[server]
host = "localhost"
port = 8080

[logging]
level = "INFO"
format = "json"

[database]
url = "sqlite:///app.db"
""".strip()

    config_file.write_text(default_config)
    typer.echo(f"Created config: {config_file}")
```

## Layered Configuration

```python
from dataclasses import dataclass, field, asdict
import tomllib
from pathlib import Path
import os

@dataclass
class Config:
    """Config with layered loading: defaults < file < env vars < CLI."""

    host: str = "localhost"
    port: int = 8080
    debug: bool = False

    @classmethod
    def load(
        cls,
        config_file: Path | None = None,
        **cli_overrides,
    ) -> "Config":
        # Start with defaults
        config = cls()

        # Layer 2: Config file
        if config_file and config_file.exists():
            with open(config_file, "rb") as f:
                file_config = tomllib.load(f)
                for key, value in file_config.items():
                    if hasattr(config, key):
                        setattr(config, key, value)

        # Layer 3: Environment variables
        env_mapping = {
            "MYAPP_HOST": "host",
            "MYAPP_PORT": "port",
            "MYAPP_DEBUG": "debug",
        }
        for env_var, attr in env_mapping.items():
            if value := os.environ.get(env_var):
                if attr == "port":
                    value = int(value)
                elif attr == "debug":
                    value = value.lower() in ("true", "1", "yes")
                setattr(config, attr, value)

        # Layer 4: CLI overrides (highest priority)
        for key, value in cli_overrides.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)

        return config


@app.command()
def serve(
    config: Path = typer.Option(None, "--config", "-c"),
    host: str = typer.Option(None, "--host", "-h"),
    port: int = typer.Option(None, "--port", "-p"),
    debug: bool = typer.Option(None, "--debug", "-d"),
):
    """Start server with layered config."""
    cfg = Config.load(
        config_file=config,
        host=host,
        port=port,
        debug=debug,
    )
    typer.echo(f"Starting on {cfg.host}:{cfg.port}")
```

## Quick Reference

| Source | Priority | Example |
|--------|----------|---------|
| Defaults | Lowest | `host="localhost"` |
| Config file | Low | `config.toml` |
| Env vars | Medium | `MYAPP_HOST=0.0.0.0` |
| CLI args | Highest | `--host 0.0.0.0` |

| XDG Directory | Purpose | Default |
|---------------|---------|---------|
| `XDG_CONFIG_HOME` | Config files | `~/.config` |
| `XDG_DATA_HOME` | Persistent data | `~/.local/share` |
| `XDG_CACHE_HOME` | Cache | `~/.cache` |
