#!/usr/bin/env python3
"""
Generate Claude Desktop configuration for rust-browser-mcp.

Usage:
    python generate-claude-config.py [--browser chrome|firefox|edge] [--binary /path/to/binary]
"""

import argparse
import json
import os
import platform
import sys
from pathlib import Path


def get_config_path():
    """Get the Claude Desktop config file path for the current platform."""
    system = platform.system()

    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def find_binary():
    """Find the rust-browser-mcp binary."""
    # Try relative path from this script
    script_dir = Path(__file__).parent.parent.parent
    release_binary = script_dir / "target" / "release" / "rust-browser-mcp"
    debug_binary = script_dir / "target" / "debug" / "rust-browser-mcp"

    if release_binary.exists():
        return str(release_binary.absolute())
    elif debug_binary.exists():
        return str(debug_binary.absolute())

    # Try PATH
    import shutil
    path_binary = shutil.which("rust-browser-mcp")
    if path_binary:
        return path_binary

    return None


def generate_mcp_config(binary_path: str, browser: str, env_vars: dict = None):
    """Generate the MCP server configuration."""
    config = {
        "command": binary_path,
        "args": ["--transport", "stdio", "--browser", browser]
    }

    if env_vars:
        config["env"] = env_vars

    return config


def update_config_file(config_path: Path, mcp_config: dict, server_name: str = "browser"):
    """Update or create the Claude Desktop config file."""
    existing_config = {}

    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Existing config file is invalid JSON, will be overwritten")

    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}

    existing_config["mcpServers"][server_name] = mcp_config

    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as f:
        json.dump(existing_config, f, indent=2)

    return existing_config


def main():
    parser = argparse.ArgumentParser(description="Generate Claude Desktop configuration for rust-browser-mcp")
    parser.add_argument("--browser", choices=["chrome", "firefox", "edge"], default="chrome",
                        help="Preferred browser (default: chrome)")
    parser.add_argument("--binary", type=str, help="Path to rust-browser-mcp binary")
    parser.add_argument("--name", type=str, default="browser", help="MCP server name (default: browser)")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode (default: true)")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Run with visible browser")
    parser.add_argument("--dry-run", action="store_true", help="Print config without writing to file")
    parser.add_argument("--pooling", action="store_true", default=True, help="Enable connection pooling")
    parser.add_argument("--no-pooling", dest="pooling", action="store_false", help="Disable connection pooling")

    args = parser.parse_args()

    # Find binary
    binary_path = args.binary or find_binary()
    if not binary_path:
        print("Error: Could not find rust-browser-mcp binary.")
        print("Please build the project with 'cargo build --release' or specify --binary path")
        sys.exit(1)

    print(f"Using binary: {binary_path}")

    # Build environment variables
    env_vars = {
        "WEBDRIVER_HEADLESS": str(args.headless).lower(),
        "WEBDRIVER_POOL_ENABLED": str(args.pooling).lower()
    }

    # Generate config
    mcp_config = generate_mcp_config(binary_path, args.browser, env_vars)

    if args.dry_run:
        full_config = {
            "mcpServers": {
                args.name: mcp_config
            }
        }
        print("\nGenerated configuration:")
        print(json.dumps(full_config, indent=2))
        print(f"\nConfig file location: {get_config_path()}")
    else:
        config_path = get_config_path()
        updated_config = update_config_file(config_path, mcp_config, args.name)
        print(f"\nConfiguration written to: {config_path}")
        print("\nFull configuration:")
        print(json.dumps(updated_config, indent=2))
        print("\nRestart Claude Desktop to apply changes.")


if __name__ == "__main__":
    main()
