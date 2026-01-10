#!/usr/bin/env python3
"""Verify Playwright MCP server is running and accessible."""
import subprocess
import sys

def main():
    # Check if server process is running
    result = subprocess.run(
        ["pgrep", "-f", "@playwright/mcp"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✓ Playwright MCP server running")
        sys.exit(0)
    else:
        print("✗ Server not running. Run: bash scripts/start-server.sh")
        sys.exit(1)

if __name__ == "__main__":
    main()