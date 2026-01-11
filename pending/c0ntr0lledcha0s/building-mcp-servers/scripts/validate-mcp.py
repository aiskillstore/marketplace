#!/usr/bin/env python3
"""
MCP Configuration Validator

Validates MCP server configurations for Claude Code plugins.
Checks JSON syntax, required fields, security practices, and best practices.

Usage:
    python3 validate-mcp.py <mcp-config-file>
    python3 validate-mcp.py plugin-name/.mcp.json
    python3 validate-mcp.py plugin-name/.claude-plugin/plugin.json
"""

import json
import sys
import re
from pathlib import Path

# ANSI colors
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

VALID_SERVER_TYPES = ['stdio', 'sse', 'http', 'websocket']

# Patterns that suggest hardcoded secrets
SECRET_PATTERNS = [
    r'sk-[a-zA-Z0-9]{20,}',  # OpenAI-style keys
    r'[a-zA-Z0-9]{32,}',     # Long alphanumeric strings (potential keys)
    r'Bearer [^${\s]+',       # Bearer tokens without variable
    r'api[_-]?key["\s:]+["\'][^${\s]+',  # Hardcoded API keys
]

def print_error(msg):
    print(f"{RED}❌ Error:{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  Warning:{RESET} {msg}")

def print_success(msg):
    print(f"{GREEN}✅{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ️{RESET}  {msg}")

def validate_server_config(name, config, errors, warnings, recommendations):
    """Validate a single MCP server configuration."""

    # Check server type
    if 'type' not in config:
        errors.append(f"Server '{name}': Missing required field 'type'")
        return

    server_type = config['type']
    if server_type not in VALID_SERVER_TYPES:
        errors.append(f"Server '{name}': Invalid type '{server_type}'. Valid types: {', '.join(VALID_SERVER_TYPES)}")
        return

    # Type-specific validation
    if server_type == 'stdio':
        if 'command' not in config:
            errors.append(f"Server '{name}' (stdio): Missing required field 'command'")

        # Check for portable paths
        args = config.get('args', [])
        for i, arg in enumerate(args):
            if isinstance(arg, str) and ('/' in arg or '\\' in arg):
                if '${CLAUDE_PLUGIN_ROOT}' not in arg and '${' not in arg:
                    warnings.append(f"Server '{name}': args[{i}] contains hardcoded path. Use ${{CLAUDE_PLUGIN_ROOT}} for portability")

    elif server_type in ['http', 'sse', 'websocket']:
        if 'url' not in config:
            errors.append(f"Server '{name}' ({server_type}): Missing required field 'url'")
        else:
            url = config['url']
            # Check for secure protocols
            if server_type == 'websocket':
                if not url.startswith('wss://') and not url.startswith('${'):
                    warnings.append(f"Server '{name}': WebSocket URL should use 'wss://' for security")
            else:
                if url.startswith('http://') and 'localhost' not in url and '127.0.0.1' not in url:
                    warnings.append(f"Server '{name}': URL should use 'https://' for security")

    # Check for hardcoded secrets in all string values
    config_str = json.dumps(config)
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, config_str, re.IGNORECASE):
            # Check if it's actually a variable reference
            if '${' not in config_str or re.search(pattern, config_str.replace('${', '').replace('}', '')):
                warnings.append(f"Server '{name}': Possible hardcoded secret detected. Use environment variables (${{VAR_NAME}})")
                break

    # Check env variables use proper syntax
    if 'env' in config:
        for env_key, env_val in config['env'].items():
            if isinstance(env_val, str) and not env_val.startswith('${') and len(env_val) > 20:
                warnings.append(f"Server '{name}': env.{env_key} may contain hardcoded value. Consider using ${{VAR_NAME}}")

    # Check headers for secrets
    if 'headers' in config:
        for header_key, header_val in config['headers'].items():
            if isinstance(header_val, str):
                if 'authorization' in header_key.lower() or 'api' in header_key.lower():
                    if not header_val.startswith('${') and 'Bearer ${' not in header_val:
                        warnings.append(f"Server '{name}': headers.{header_key} should use environment variable for secrets")


def validate_mcp_config(file_path):
    """Validate an MCP configuration file."""

    errors = []
    warnings = []
    recommendations = []

    path = Path(file_path)

    if not path.exists():
        print_error(f"File not found: {file_path}")
        return 1

    # Read and parse JSON
    try:
        with open(path, 'r') as f:
            content = f.read()
            config = json.loads(content)
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}")
        return 1

    # Determine if this is a standalone .mcp.json or a plugin.json
    is_plugin_json = path.name == 'plugin.json'

    # Extract mcpServers section
    if 'mcpServers' not in config:
        if is_plugin_json:
            print_info("No mcpServers section found in plugin.json (this is OK if MCP not needed)")
            return 0
        else:
            errors.append("Missing 'mcpServers' section in MCP config file")
    else:
        mcp_servers = config['mcpServers']

        if not isinstance(mcp_servers, dict):
            errors.append("'mcpServers' must be an object/dictionary")
        elif len(mcp_servers) == 0:
            warnings.append("'mcpServers' is empty - no servers configured")
        else:
            # Validate each server
            for server_name, server_config in mcp_servers.items():
                # Validate server name
                if not re.match(r'^[a-z][a-z0-9-]*$', server_name):
                    warnings.append(f"Server name '{server_name}' should be lowercase with hyphens only")

                if not isinstance(server_config, dict):
                    errors.append(f"Server '{server_name}': Configuration must be an object")
                    continue

                validate_server_config(server_name, server_config, errors, warnings, recommendations)

    # Print results
    print(f"\n{BLUE}MCP Configuration Validation Results{RESET}")
    print(f"File: {file_path}\n")

    if errors:
        print(f"{RED}Errors ({len(errors)}):{RESET}")
        for error in errors:
            print(f"  • {error}")
        print()

    if warnings:
        print(f"{YELLOW}Warnings ({len(warnings)}):{RESET}")
        for warning in warnings:
            print(f"  • {warning}")
        print()

    if recommendations:
        print(f"{BLUE}Recommendations ({len(recommendations)}):{RESET}")
        for rec in recommendations:
            print(f"  • {rec}")
        print()

    if not errors and not warnings:
        print_success("MCP configuration is valid!")
    elif not errors:
        print_success("MCP configuration is valid (with warnings)")
    else:
        print_error("MCP configuration has errors that must be fixed")

    # Return exit code
    return 1 if errors else 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate-mcp.py <mcp-config-file>")
        print("\nExamples:")
        print("  python3 validate-mcp.py .mcp.json")
        print("  python3 validate-mcp.py plugin-name/.mcp.json")
        print("  python3 validate-mcp.py plugin-name/.claude-plugin/plugin.json")
        sys.exit(1)

    file_path = sys.argv[1]
    exit_code = validate_mcp_config(file_path)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
