#!/usr/bin/env python3
"""
Home Assistant YAML Validator

Validates YAML files for syntax errors and common Home Assistant issues.
Usage: python3 validate_yaml.py <file_path> [--strict]
"""

import sys
import re
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    print(json.dumps({
        "valid": False,
        "error": "PyYAML not installed. Run: pip install pyyaml"
    }))
    sys.exit(1)


class HAYamlValidator:
    """Validator for Home Assistant YAML configuration files."""

    # Common issues to check
    DEPRECATED_KEYS = {
        "service": "action",  # 2024+ syntax
        "trigger": "triggers",  # plural form preferred
        "action": "actions",  # plural form in sequences
    }

    BOOLEAN_STRINGS = {"on", "off", "yes", "no", "true", "false"}

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.errors = []
        self.warnings = []

    def validate_file(self, file_path: str) -> dict:
        """Validate a YAML file and return results."""
        path = Path(file_path)

        if not path.exists():
            return {"valid": False, "error": f"File not found: {file_path}"}

        if not path.suffix.lower() in ('.yaml', '.yml'):
            self.warnings.append(f"File extension '{path.suffix}' is not .yaml or .yml")

        try:
            content = path.read_text(encoding='utf-8')
        except Exception as e:
            return {"valid": False, "error": f"Cannot read file: {e}"}

        # Check for tabs
        self._check_tabs(content)

        # Check for unquoted booleans
        self._check_unquoted_booleans(content)

        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            error_msg = str(e)
            line_match = re.search(r'line (\d+)', error_msg)
            line_num = int(line_match.group(1)) if line_match else None

            return {
                "valid": False,
                "error": "YAML syntax error",
                "details": error_msg,
                "line": line_num,
                "errors": self.errors,
                "warnings": self.warnings
            }

        # Validate HA-specific structure
        if data:
            self._validate_ha_structure(data)

        is_valid = len(self.errors) == 0
        if self.strict:
            is_valid = is_valid and len(self.warnings) == 0

        return {
            "valid": is_valid,
            "file": str(path.absolute()),
            "errors": self.errors,
            "warnings": self.warnings,
            "keys": list(data.keys()) if isinstance(data, dict) else None
        }

    def _check_tabs(self, content: str):
        """Check for tab characters in YAML."""
        for i, line in enumerate(content.split('\n'), 1):
            if '\t' in line:
                self.errors.append(f"Line {i}: Tab character found (use 2 spaces)")

    def _check_unquoted_booleans(self, content: str):
        """Check for unquoted boolean-like values."""
        pattern = r':\s*(on|off|yes|no)\s*$'
        for i, line in enumerate(content.split('\n'), 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                value = match.group(1)
                self.warnings.append(
                    f"Line {i}: Unquoted boolean '{value}' - consider quoting: \"{value}\""
                )

    def _validate_ha_structure(self, data: dict, path: str = ""):
        """Validate Home Assistant specific structure."""
        if not isinstance(data, dict):
            return

        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            # Check for deprecated keys (warning only)
            if key in self.DEPRECATED_KEYS:
                new_key = self.DEPRECATED_KEYS[key]
                self.warnings.append(
                    f"'{current_path}': Consider using '{new_key}' instead of '{key}' (2024+ syntax)"
                )

            # Validate entity_id patterns
            if key == "entity_id" and isinstance(value, str):
                if not re.match(r'^[a-z_]+\.[a-z0-9_]+$', value):
                    self.warnings.append(
                        f"'{current_path}': Entity ID '{value}' may have invalid format"
                    )

            # Recurse into nested structures
            if isinstance(value, dict):
                self._validate_ha_structure(value, current_path)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._validate_ha_structure(item, f"{current_path}[{i}]")


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: validate_yaml.py <file_path> [--strict]",
            "example": "python3 validate_yaml.py configuration.yaml"
        }, indent=2))
        sys.exit(1)

    file_path = sys.argv[1]
    strict = "--strict" in sys.argv

    validator = HAYamlValidator(strict=strict)
    result = validator.validate_file(file_path)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("valid", False) else 1)


if __name__ == "__main__":
    main()
