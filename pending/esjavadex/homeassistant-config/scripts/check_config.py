#!/usr/bin/env python3
"""
Home Assistant Configuration Checker

Analyzes HA configuration files for structure, dependencies, and best practices.
Usage: python3 check_config.py <directory_or_file> [--verbose]
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Optional

try:
    import yaml
except ImportError:
    print(json.dumps({
        "error": "PyYAML not installed. Run: pip install pyyaml"
    }))
    sys.exit(1)


class HAConfigChecker:
    """Analyzes Home Assistant configuration structure and dependencies."""

    HA_DOMAINS = {
        "automation", "script", "scene", "group", "input_boolean",
        "input_number", "input_text", "input_select", "input_datetime",
        "input_button", "counter", "timer", "schedule", "template",
        "sensor", "binary_sensor", "switch", "light", "cover", "fan",
        "climate", "media_player", "camera", "notify", "tts", "mqtt",
        "rest", "command_line", "shell_command", "homeassistant",
        "frontend", "lovelace", "logger", "recorder", "history",
        "logbook", "person", "zone", "device_tracker", "geo_location"
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.files_checked: List[str] = []
        self.entities_found: Dict[str, Set[str]] = {}
        self.secrets_used: Set[str] = set()
        self.includes_found: List[dict] = []
        self.issues: List[dict] = []
        self.suggestions: List[str] = []

    def check_path(self, path: str) -> dict:
        """Check a file or directory."""
        p = Path(path)

        if not p.exists():
            return {"error": f"Path not found: {path}"}

        if p.is_file():
            return self._check_single_file(p)
        elif p.is_dir():
            return self._check_directory(p)

        return {"error": f"Invalid path: {path}"}

    def _check_directory(self, directory: Path) -> dict:
        """Check all YAML files in a directory."""
        yaml_files = list(directory.glob("**/*.yaml")) + list(directory.glob("**/*.yml"))

        if not yaml_files:
            return {"error": f"No YAML files found in {directory}"}

        # Check for main configuration file
        main_config = directory / "configuration.yaml"
        has_main_config = main_config.exists()

        for yaml_file in yaml_files:
            self._analyze_file(yaml_file)

        return self._generate_report(directory, has_main_config)

    def _check_single_file(self, file_path: Path) -> dict:
        """Check a single YAML file."""
        self._analyze_file(file_path)
        return self._generate_report(file_path.parent, False)

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single YAML file."""
        self.files_checked.append(str(file_path))

        try:
            content = file_path.read_text(encoding='utf-8')
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            self.issues.append({
                "file": str(file_path),
                "type": "syntax_error",
                "message": str(e)
            })
            return
        except Exception as e:
            self.issues.append({
                "file": str(file_path),
                "type": "read_error",
                "message": str(e)
            })
            return

        if not data:
            return

        # Check for !include directives in raw content
        self._find_includes(content, file_path)

        # Check for !secret references
        self._find_secrets(content, file_path)

        # Analyze structure
        if isinstance(data, dict):
            self._analyze_structure(data, file_path)

    def _find_includes(self, content: str, file_path: Path) -> None:
        """Find !include directives."""
        patterns = [
            (r'!include\s+(\S+)', 'include'),
            (r'!include_dir_list\s+(\S+)', 'include_dir_list'),
            (r'!include_dir_named\s+(\S+)', 'include_dir_named'),
            (r'!include_dir_merge_list\s+(\S+)', 'include_dir_merge_list'),
            (r'!include_dir_merge_named\s+(\S+)', 'include_dir_merge_named'),
        ]

        for pattern, include_type in patterns:
            for match in re.finditer(pattern, content):
                self.includes_found.append({
                    "file": str(file_path),
                    "type": include_type,
                    "target": match.group(1)
                })

    def _find_secrets(self, content: str, file_path: Path) -> None:
        """Find !secret references."""
        for match in re.finditer(r'!secret\s+(\S+)', content):
            self.secrets_used.add(match.group(1))

    def _analyze_structure(self, data: dict, file_path: Path) -> None:
        """Analyze configuration structure."""
        for key, value in data.items():
            # Track known domains
            if key in self.HA_DOMAINS:
                if key not in self.entities_found:
                    self.entities_found[key] = set()

                # Extract entity IDs
                self._extract_entities(value, key)

            # Check for automation structure
            if key == "automation":
                self._check_automations(value, file_path)

            # Check for script structure
            if key == "script":
                self._check_scripts(value, file_path)

    def _extract_entities(self, value, domain: str) -> None:
        """Extract entity identifiers from configuration."""
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    # Check for alias or id
                    entity_id = item.get("id") or item.get("alias") or item.get("name")
                    if entity_id:
                        self.entities_found[domain].add(str(entity_id))
        elif isinstance(value, dict):
            for entity_name in value.keys():
                self.entities_found[domain].add(entity_name)

    def _check_automations(self, automations, file_path: Path) -> None:
        """Check automation configurations."""
        if not isinstance(automations, list):
            return

        for i, automation in enumerate(automations):
            if not isinstance(automation, dict):
                continue

            # Check for missing alias
            if "alias" not in automation:
                self.issues.append({
                    "file": str(file_path),
                    "type": "missing_alias",
                    "message": f"Automation #{i+1} is missing 'alias'"
                })

            # Check for missing id
            if "id" not in automation:
                self.suggestions.append(
                    f"Automation '{automation.get('alias', f'#{i+1}')}' in {file_path.name}: "
                    "Consider adding 'id' for UI editing support"
                )

            # Check for mode (good practice)
            if "mode" not in automation and self.verbose:
                self.suggestions.append(
                    f"Automation '{automation.get('alias', f'#{i+1}')}': "
                    "Consider specifying 'mode' (single/restart/queued/parallel)"
                )

    def _check_scripts(self, scripts, file_path: Path) -> None:
        """Check script configurations."""
        if not isinstance(scripts, dict):
            return

        for script_id, script in scripts.items():
            if not isinstance(script, dict):
                continue

            # Check for missing alias
            if "alias" not in script:
                self.suggestions.append(
                    f"Script '{script_id}' in {file_path.name}: Consider adding 'alias'"
                )

    def _generate_report(self, base_path: Path, has_main_config: bool) -> dict:
        """Generate the analysis report."""
        report = {
            "path": str(base_path),
            "files_checked": len(self.files_checked),
            "has_configuration_yaml": has_main_config,
            "summary": {
                "domains_found": list(self.entities_found.keys()),
                "total_entities": sum(len(v) for v in self.entities_found.values()),
                "secrets_referenced": len(self.secrets_used),
                "includes_found": len(self.includes_found),
                "issues_found": len(self.issues)
            },
            "issues": self.issues if self.issues else None,
            "suggestions": self.suggestions if self.suggestions else None
        }

        if self.verbose:
            report["details"] = {
                "files": self.files_checked,
                "entities": {k: list(v) for k, v in self.entities_found.items()},
                "secrets": list(self.secrets_used),
                "includes": self.includes_found
            }

        # Add overall status
        if self.issues:
            report["status"] = "issues_found"
        elif self.suggestions:
            report["status"] = "ok_with_suggestions"
        else:
            report["status"] = "ok"

        return report


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: check_config.py <directory_or_file> [--verbose]",
            "examples": [
                "python3 check_config.py /config",
                "python3 check_config.py configuration.yaml --verbose"
            ]
        }, indent=2))
        sys.exit(1)

    path = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    checker = HAConfigChecker(verbose=verbose)
    result = checker.check_path(path)

    print(json.dumps(result, indent=2))

    # Exit code based on issues
    if result.get("issues"):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
