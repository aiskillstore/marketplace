#!/usr/bin/env python3
"""
Home Assistant Lovelace Dashboard Validator

Validates Lovelace dashboard configurations (YAML and JSON storage format).
Usage: python3 lovelace_validator.py <file_path> [--strict]
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional

try:
    import yaml
except ImportError:
    print(json.dumps({
        "valid": False,
        "error": "PyYAML not installed. Run: pip install pyyaml"
    }))
    sys.exit(1)


class LovelaceValidator:
    """Validator for Lovelace dashboard configurations."""

    # Built-in card types
    BUILTIN_CARDS = {
        "alarm-panel", "area", "button", "calendar", "conditional",
        "entities", "entity", "entity-filter", "gauge", "glance",
        "grid", "heading", "history-graph", "horizontal-stack",
        "humidifier", "iframe", "light", "logbook", "map",
        "markdown", "media-control", "picture", "picture-elements",
        "picture-entity", "picture-glance", "plant-status", "sensor",
        "shopping-list", "statistic", "statistics-graph", "thermostat",
        "tile", "todo-list", "vertical-stack", "weather-forecast",
        "webpage", "energy-distribution", "energy-usage-graph"
    }

    # Popular custom cards (HACS)
    KNOWN_CUSTOM_CARDS = {
        "custom:button-card", "custom:mushroom-light-card",
        "custom:mushroom-entity-card", "custom:mushroom-chips-card",
        "custom:mushroom-climate-card", "custom:mushroom-cover-card",
        "custom:mushroom-fan-card", "custom:mushroom-person-card",
        "custom:mushroom-template-card", "custom:mushroom-alarm-control-panel-card",
        "custom:mini-graph-card", "custom:mini-media-player",
        "custom:stack-in-card", "custom:layout-card", "custom:card-mod",
        "custom:auto-entities", "custom:swipe-card", "custom:fold-entity-row",
        "custom:slider-entity-row", "custom:bar-card", "custom:apexcharts-card",
        "custom:vacuum-card", "custom:weather-card", "custom:clock-weather-card"
    }

    # Valid action types
    VALID_ACTIONS = {
        "none", "more-info", "toggle", "call-service", "navigate",
        "url", "assist", "fire-dom-event"
    }

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.errors: List[dict] = []
        self.warnings: List[dict] = []
        self.cards_found: Dict[str, int] = {}
        self.entities_referenced: Set[str] = set()
        self.custom_cards_used: Set[str] = set()

    def validate_file(self, file_path: str) -> dict:
        """Validate a Lovelace configuration file."""
        path = Path(file_path)

        if not path.exists():
            return {"valid": False, "error": f"File not found: {file_path}"}

        try:
            content = path.read_text(encoding='utf-8')
        except Exception as e:
            return {"valid": False, "error": f"Cannot read file: {e}"}

        # Determine format and parse
        data = None
        file_format = "unknown"

        # Try JSON first (for .storage/lovelace)
        if path.suffix == '.json' or 'lovelace' in path.name:
            try:
                data = json.loads(content)
                file_format = "json"
                # Handle .storage format
                if "data" in data and "config" in data.get("data", {}):
                    data = data["data"]["config"]
            except json.JSONDecodeError:
                pass

        # Try YAML
        if data is None:
            try:
                data = yaml.safe_load(content)
                file_format = "yaml"
            except yaml.YAMLError as e:
                return {
                    "valid": False,
                    "error": "YAML syntax error",
                    "details": str(e)
                }

        if not data:
            return {
                "valid": False,
                "error": "Empty or invalid configuration"
            }

        # Validate structure
        self._validate_dashboard(data)

        is_valid = len(self.errors) == 0
        if self.strict:
            is_valid = is_valid and len(self.warnings) == 0

        return {
            "valid": is_valid,
            "file": str(path.absolute()),
            "format": file_format,
            "summary": {
                "views": self._count_views(data),
                "total_cards": sum(self.cards_found.values()),
                "card_types": self.cards_found,
                "custom_cards": list(self.custom_cards_used),
                "entities_referenced": len(self.entities_referenced)
            },
            "errors": self.errors if self.errors else None,
            "warnings": self.warnings if self.warnings else None
        }

    def _count_views(self, data: dict) -> int:
        """Count views in dashboard."""
        if isinstance(data.get("views"), list):
            return len(data["views"])
        return 0

    def _validate_dashboard(self, data: dict, path: str = ""):
        """Validate dashboard structure."""
        if not isinstance(data, dict):
            return

        # Check for views
        if "views" in data:
            views = data["views"]
            if not isinstance(views, list):
                self.errors.append({
                    "path": "views",
                    "message": "'views' must be a list"
                })
            else:
                for i, view in enumerate(views):
                    self._validate_view(view, f"views[{i}]")

    def _validate_view(self, view: dict, path: str):
        """Validate a single view."""
        if not isinstance(view, dict):
            self.errors.append({
                "path": path,
                "message": "View must be an object"
            })
            return

        # Check recommended fields
        if "title" not in view and "path" not in view:
            self.warnings.append({
                "path": path,
                "message": "View should have 'title' or 'path' for navigation"
            })

        # Validate cards
        if "cards" in view:
            cards = view["cards"]
            if isinstance(cards, list):
                for i, card in enumerate(cards):
                    self._validate_card(card, f"{path}.cards[{i}]")

        # Validate sections (new dashboard format)
        if "sections" in view:
            sections = view["sections"]
            if isinstance(sections, list):
                for i, section in enumerate(sections):
                    self._validate_section(section, f"{path}.sections[{i}]")

    def _validate_section(self, section: dict, path: str):
        """Validate a dashboard section."""
        if not isinstance(section, dict):
            return

        if "cards" in section:
            cards = section["cards"]
            if isinstance(cards, list):
                for i, card in enumerate(cards):
                    self._validate_card(card, f"{path}.cards[{i}]")

    def _validate_card(self, card: dict, path: str):
        """Validate a single card."""
        if not isinstance(card, dict):
            self.errors.append({
                "path": path,
                "message": "Card must be an object"
            })
            return

        # Check for type
        card_type = card.get("type")
        if not card_type:
            self.errors.append({
                "path": path,
                "message": "Card is missing 'type'"
            })
            return

        # Track card type usage
        self.cards_found[card_type] = self.cards_found.get(card_type, 0) + 1

        # Check if it's a custom card
        if card_type.startswith("custom:"):
            self.custom_cards_used.add(card_type)
            if card_type not in self.KNOWN_CUSTOM_CARDS and self.strict:
                self.warnings.append({
                    "path": path,
                    "message": f"Unknown custom card '{card_type}' - ensure it's installed via HACS"
                })
        elif card_type not in self.BUILTIN_CARDS:
            self.warnings.append({
                "path": path,
                "message": f"Unknown card type '{card_type}'"
            })

        # Validate entity references
        self._extract_entities(card, path)

        # Validate actions
        for action_key in ["tap_action", "hold_action", "double_tap_action"]:
            if action_key in card:
                self._validate_action(card[action_key], f"{path}.{action_key}")

        # Validate nested cards (stacks, grids, etc.)
        if card_type in {"horizontal-stack", "vertical-stack", "grid"}:
            if "cards" in card:
                for i, nested in enumerate(card.get("cards", [])):
                    self._validate_card(nested, f"{path}.cards[{i}]")

        # Validate conditional cards
        if card_type == "conditional":
            if "card" in card:
                self._validate_card(card["card"], f"{path}.card")
            if "conditions" not in card:
                self.errors.append({
                    "path": path,
                    "message": "Conditional card requires 'conditions'"
                })

    def _extract_entities(self, card: dict, path: str):
        """Extract and validate entity references."""
        # Single entity
        if "entity" in card:
            entity = card["entity"]
            if isinstance(entity, str):
                self.entities_referenced.add(entity)
                self._validate_entity_format(entity, f"{path}.entity")

        # Multiple entities
        if "entities" in card:
            entities = card["entities"]
            if isinstance(entities, list):
                for i, entity in enumerate(entities):
                    if isinstance(entity, str):
                        self.entities_referenced.add(entity)
                        self._validate_entity_format(entity, f"{path}.entities[{i}]")
                    elif isinstance(entity, dict) and "entity" in entity:
                        self.entities_referenced.add(entity["entity"])
                        self._validate_entity_format(entity["entity"], f"{path}.entities[{i}].entity")

    def _validate_entity_format(self, entity_id: str, path: str):
        """Validate entity ID format."""
        if not re.match(r'^[a-z_]+\.[a-z0-9_]+$', entity_id):
            self.warnings.append({
                "path": path,
                "message": f"Entity ID '{entity_id}' may have invalid format (expected: domain.entity_name)"
            })

    def _validate_action(self, action: dict, path: str):
        """Validate card action configuration."""
        if not isinstance(action, dict):
            return

        action_type = action.get("action")
        if action_type and action_type not in self.VALID_ACTIONS:
            self.warnings.append({
                "path": path,
                "message": f"Unknown action type '{action_type}'"
            })

        # Validate navigate action
        if action_type == "navigate" and "navigation_path" not in action:
            self.errors.append({
                "path": path,
                "message": "Navigate action requires 'navigation_path'"
            })

        # Validate call-service action
        if action_type == "call-service":
            if "service" not in action and "action" not in action:
                self.errors.append({
                    "path": path,
                    "message": "Call-service action requires 'service' or 'action'"
                })

        # Validate url action
        if action_type == "url" and "url_path" not in action:
            self.errors.append({
                "path": path,
                "message": "URL action requires 'url_path'"
            })


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: lovelace_validator.py <file_path> [--strict]",
            "examples": [
                "python3 lovelace_validator.py ui-lovelace.yaml",
                "python3 lovelace_validator.py .storage/lovelace --strict"
            ]
        }, indent=2))
        sys.exit(1)

    file_path = sys.argv[1]
    strict = "--strict" in sys.argv

    validator = LovelaceValidator(strict=strict)
    result = validator.validate_file(file_path)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("valid", False) else 1)


if __name__ == "__main__":
    main()
