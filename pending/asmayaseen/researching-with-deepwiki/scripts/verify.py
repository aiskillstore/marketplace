#!/usr/bin/env python3
"""Verify researching-with-deepwiki skill - check MCP server is configured."""
import json
import os
import sys
from pathlib import Path

def main():
    # Check common Claude Code settings locations
    home = Path.home()
    settings_paths = [
        home / ".claude" / "settings.json",
        home / ".config" / "claude" / "settings.json",
        Path.cwd() / ".claude" / "settings.json",
    ]

    for settings_path in settings_paths:
        if settings_path.exists():
            try:
                with open(settings_path) as f:
                    settings = json.load(f)

                mcp_servers = settings.get("mcpServers", {})
                if "deepwiki" in mcp_servers:
                    url = mcp_servers["deepwiki"].get("url", "")
                    if "deepwiki" in url or "devin.ai" in url:
                        print("✓ DeepWiki MCP server configured")
                        sys.exit(0)
            except (json.JSONDecodeError, KeyError):
                continue

    # If not found in settings, check if skill files exist
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_md = os.path.join(skill_dir, "SKILL.md")

    if os.path.isfile(skill_md):
        print("✓ researching-with-deepwiki skill ready (configure MCP for full use)")
        sys.exit(0)

    print("✗ SKILL.md missing")
    sys.exit(1)

if __name__ == "__main__":
    main()