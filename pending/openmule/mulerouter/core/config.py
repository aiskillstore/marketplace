"""Configuration management for MuleRouter skill."""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv


class Site(Enum):
    """Supported API sites."""

    MULEROUTER = "mulerouter"
    MULERUN = "mulerun"


@dataclass
class Config:
    """Configuration for MuleRouter API client.

    Attributes:
        api_key: API key for authentication
        site: API site (mulerouter or mulerun)
        base_url: Base URL for the API (auto-derived from site)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries for failed requests
    """

    api_key: str
    site: Site = Site.MULEROUTER
    base_url: str = field(init=False)
    timeout: float = 120.0
    max_retries: int = 3

    def __post_init__(self) -> None:
        """Set base_url based on site."""
        if self.site == Site.MULEROUTER:
            self.base_url = "https://api.mulerouter.ai"
        else:
            self.base_url = "https://api.mulerun.com"


def load_env_file(env_file: Path | None = None) -> None:
    """Load .env file if it exists.

    Args:
        env_file: Path to .env file (defaults to current directory)
    """
    if env_file:
        load_dotenv(env_file)
    else:
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)


def get_site_from_env() -> Site | None:
    """Get site from environment variable.

    Returns:
        Site enum if MULEROUTER_SITE is set, None otherwise
    """
    site_str = os.getenv("MULEROUTER_SITE")
    if not site_str:
        return None
    try:
        return Site(site_str.lower())
    except ValueError:
        return None


def load_config(
    api_key: str | None = None,
    site: str | None = None,
    env_file: Path | None = None,
) -> Config:
    """Load configuration from environment or parameters.

    Priority: explicit parameters > environment variables > .env file

    Args:
        api_key: Explicit API key (overrides environment)
        site: Explicit site name (overrides environment)
        env_file: Path to .env file (defaults to current directory)

    Returns:
        Configured Config instance

    Raises:
        ValueError: If API key or site is not found
    """
    # Load .env file if it exists
    load_env_file(env_file)

    # Resolve site first (needed to determine which API key to use)
    site_str = site or os.getenv("MULEROUTER_SITE")
    if not site_str:
        raise ValueError(
            "Site not specified. Please set MULEROUTER_SITE environment variable "
            "to 'mulerouter' or 'mulerun', or provide it via --site argument."
        )

    try:
        resolved_site = Site(site_str.lower())
    except ValueError as err:
        raise ValueError(
            f"Invalid site: {site_str}. Must be 'mulerouter' or 'mulerun'."
        ) from err

    # Resolve API key
    resolved_api_key = api_key or os.getenv("MULEROUTER_API_KEY")
    if not resolved_api_key:
        raise ValueError(
            "API key not found. Please set MULEROUTER_API_KEY environment variable, "
            "or provide it via --api-key argument."
        )

    return Config(api_key=resolved_api_key, site=resolved_site)


def get_config_help() -> str:
    """Get help text for configuration."""
    return """
Configuration Options:
---------------------
Environment Variables (Required):
  MULEROUTER_SITE       API site: 'mulerouter' or 'mulerun' (required)
  MULEROUTER_API_KEY    API key for authentication (required)

.env File:
  Create a .env file in the current directory with the above variables.

  Example .env:
    MULEROUTER_SITE=mulerun
    MULEROUTER_API_KEY=your-api-key-here

Command Line:
  --api-key KEY         Override API key
  --site SITE           Override site (mulerouter/mulerun)
"""
