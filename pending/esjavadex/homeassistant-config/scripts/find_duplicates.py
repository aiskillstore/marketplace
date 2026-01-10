#!/usr/bin/env python3
"""
Home Assistant Duplicate Finder

Finds duplicate and similar automations/scripts in HA configuration.
Usage: python3 find_duplicates.py <directory_or_file> [--verbose]
"""

import sys
import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from difflib import SequenceMatcher
from collections import defaultdict

try:
    import yaml
except ImportError:
    print(json.dumps({
        "error": "PyYAML not installed. Run: pip install pyyaml"
    }))
    sys.exit(1)


# Custom YAML loader to handle Home Assistant tags
class HAYamlLoader(yaml.SafeLoader):
    """YAML loader that handles Home Assistant custom tags."""
    pass


def _ha_tag_constructor(loader, tag_suffix, node):
    """Handle HA custom tags by returning their value as a string."""
    if isinstance(node, yaml.ScalarNode):
        return f"!{tag_suffix} {loader.construct_scalar(node)}"
    elif isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    elif isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


# Register handlers for common HA tags
for tag in ['include', 'include_dir_list', 'include_dir_named',
            'include_dir_merge_list', 'include_dir_merge_named',
            'secret', 'input', 'env_var']:
    HAYamlLoader.add_constructor(
        f'!{tag}',
        lambda loader, node, t=tag: _ha_tag_constructor(loader, t, node)
    )

# Handle any unknown tags gracefully
HAYamlLoader.add_multi_constructor(
    '',
    lambda loader, tag, node: _ha_tag_constructor(loader, tag.lstrip('!'), node)
)


class DuplicateFinder:
    """Finds duplicate and similar automations/scripts in HA configuration."""

    SIMILARITY_THRESHOLD = 0.8  # 80% similarity for "similar" items

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.automations: List[dict] = []
        self.scripts: List[dict] = []
        self.files_checked: List[str] = []
        self.errors: List[dict] = []

    def scan_path(self, path: str) -> dict:
        """Scan a file or directory for duplicates."""
        p = Path(path)

        if not p.exists():
            return {"error": f"Path not found: {path}"}

        if p.is_file():
            self._scan_file(p)
        elif p.is_dir():
            self._scan_directory(p)

        return self._analyze_duplicates()

    def _scan_directory(self, directory: Path) -> None:
        """Scan all YAML files in a directory."""
        yaml_files = list(directory.glob("**/*.yaml")) + list(directory.glob("**/*.yml"))

        for yaml_file in yaml_files:
            # Skip hidden directories and common non-config files
            if any(part.startswith('.') for part in yaml_file.parts):
                continue
            self._scan_file(yaml_file)

    def _scan_file(self, file_path: Path) -> None:
        """Scan a single YAML file."""
        self.files_checked.append(str(file_path))

        try:
            content = file_path.read_text(encoding='utf-8')
            data = yaml.load(content, Loader=HAYamlLoader)
        except yaml.YAMLError as e:
            self.errors.append({
                "file": str(file_path),
                "error": f"YAML parse error: {e}"
            })
            return
        except Exception as e:
            self.errors.append({
                "file": str(file_path),
                "error": str(e)
            })
            return

        if not data:
            return

        # Handle different file structures
        if isinstance(data, dict):
            # File with domain keys (e.g., configuration.yaml with automation: key)
            if "automation" in data:
                self._extract_automations(data["automation"], file_path)
            if "script" in data:
                self._extract_scripts(data["script"], file_path)
        elif isinstance(data, list):
            # File is a list of automations (e.g., automations.yaml)
            if file_path.stem in ("automations", "automation"):
                self._extract_automations(data, file_path)
            elif file_path.stem in ("scripts", "script"):
                self._extract_scripts_from_list(data, file_path)
            else:
                # Try to detect type from content
                if data and isinstance(data[0], dict):
                    if "trigger" in data[0] or "triggers" in data[0]:
                        self._extract_automations(data, file_path)

    def _extract_automations(self, automations, file_path: Path) -> None:
        """Extract automations from configuration."""
        if not isinstance(automations, list):
            return

        for idx, automation in enumerate(automations):
            if not isinstance(automation, dict):
                continue

            auto_info = {
                "file": str(file_path),
                "index": idx,
                "alias": automation.get("alias", f"Unnamed #{idx+1}"),
                "id": automation.get("id"),
                "triggers": self._normalize_triggers(automation),
                "conditions": self._normalize_conditions(automation),
                "actions": self._normalize_actions(automation),
                "entities": self._extract_entity_ids(automation),
                "raw": automation
            }
            auto_info["hash"] = self._compute_hash(auto_info)
            self.automations.append(auto_info)

    def _extract_scripts(self, scripts, file_path: Path) -> None:
        """Extract scripts from dict configuration."""
        if not isinstance(scripts, dict):
            return

        for script_id, script in scripts.items():
            if not isinstance(script, dict):
                continue

            script_info = {
                "file": str(file_path),
                "script_id": script_id,
                "alias": script.get("alias", script_id),
                "sequence": self._normalize_sequence(script),
                "entities": self._extract_entity_ids(script),
                "raw": script
            }
            script_info["hash"] = self._compute_hash(script_info)
            self.scripts.append(script_info)

    def _extract_scripts_from_list(self, scripts, file_path: Path) -> None:
        """Extract scripts from list format."""
        if not isinstance(scripts, list):
            return

        for idx, script in enumerate(scripts):
            if not isinstance(script, dict):
                continue

            script_info = {
                "file": str(file_path),
                "index": idx,
                "alias": script.get("alias", f"Script #{idx+1}"),
                "sequence": self._normalize_sequence(script),
                "entities": self._extract_entity_ids(script),
                "raw": script
            }
            script_info["hash"] = self._compute_hash(script_info)
            self.scripts.append(script_info)

    def _normalize_triggers(self, automation: dict) -> List[dict]:
        """Normalize triggers for comparison."""
        triggers = automation.get("triggers") or automation.get("trigger") or []
        if isinstance(triggers, dict):
            triggers = [triggers]
        return self._sort_dict_list(triggers)

    def _normalize_conditions(self, automation: dict) -> List[dict]:
        """Normalize conditions for comparison."""
        conditions = automation.get("conditions") or automation.get("condition") or []
        if isinstance(conditions, dict):
            conditions = [conditions]
        return self._sort_dict_list(conditions)

    def _normalize_actions(self, automation: dict) -> List[dict]:
        """Normalize actions for comparison."""
        actions = automation.get("actions") or automation.get("action") or []
        if isinstance(actions, dict):
            actions = [actions]
        return actions  # Preserve order for actions

    def _normalize_sequence(self, script: dict) -> List[dict]:
        """Normalize script sequence for comparison."""
        sequence = script.get("sequence") or []
        if isinstance(sequence, dict):
            sequence = [sequence]
        return sequence

    def _sort_dict_list(self, items: List) -> List:
        """Sort a list of dicts for consistent comparison."""
        if not items:
            return []
        try:
            return sorted(items, key=lambda x: json.dumps(x, sort_keys=True) if isinstance(x, dict) else str(x))
        except TypeError:
            return items

    def _extract_entity_ids(self, config: dict) -> Set[str]:
        """Extract all entity IDs from a configuration."""
        entities = set()

        def extract_from_value(value):
            if isinstance(value, str):
                # Match entity_id patterns
                if re.match(r'^[a-z_]+\.[a-z0-9_]+$', value):
                    entities.add(value)
            elif isinstance(value, list):
                for item in value:
                    extract_from_value(item)
            elif isinstance(value, dict):
                for k, v in value.items():
                    if k in ("entity_id", "entity", "target", "service"):
                        if isinstance(v, str):
                            entities.add(v)
                        elif isinstance(v, list):
                            entities.update(v)
                        elif isinstance(v, dict) and "entity_id" in v:
                            eid = v["entity_id"]
                            if isinstance(eid, str):
                                entities.add(eid)
                            elif isinstance(eid, list):
                                entities.update(eid)
                    else:
                        extract_from_value(v)

        extract_from_value(config)
        return entities

    def _compute_hash(self, item: dict) -> str:
        """Compute a hash of the meaningful parts for exact duplicate detection."""
        # For automations, hash triggers + actions (ignore alias/id)
        if "triggers" in item:
            hashable = {
                "triggers": item["triggers"],
                "conditions": item["conditions"],
                "actions": item["actions"]
            }
        else:
            # For scripts
            hashable = {
                "sequence": item["sequence"]
            }

        content = json.dumps(hashable, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _analyze_duplicates(self) -> dict:
        """Analyze collected items for duplicates and similarities."""
        result = {
            "files_scanned": len(self.files_checked),
            "automations_found": len(self.automations),
            "scripts_found": len(self.scripts),
            "exact_duplicates": {
                "automations": [],
                "scripts": []
            },
            "similar_items": {
                "automations": [],
                "scripts": []
            },
            "trigger_conflicts": [],
            "errors": self.errors if self.errors else None
        }

        # Find exact duplicates (same hash)
        result["exact_duplicates"]["automations"] = self._find_exact_duplicates(self.automations, "automation")
        result["exact_duplicates"]["scripts"] = self._find_exact_duplicates(self.scripts, "script")

        # Find similar items
        result["similar_items"]["automations"] = self._find_similar_items(self.automations, "automation")
        result["similar_items"]["scripts"] = self._find_similar_items(self.scripts, "script")

        # Find trigger conflicts (multiple automations with same trigger)
        result["trigger_conflicts"] = self._find_trigger_conflicts()

        # Generate summary
        total_exact = (
            len(result["exact_duplicates"]["automations"]) +
            len(result["exact_duplicates"]["scripts"])
        )
        total_similar = (
            len(result["similar_items"]["automations"]) +
            len(result["similar_items"]["scripts"])
        )

        if total_exact == 0 and total_similar == 0 and not result["trigger_conflicts"]:
            result["status"] = "clean"
            result["message"] = "No duplicates or conflicts found"
        else:
            result["status"] = "duplicates_found"
            result["summary"] = {
                "exact_duplicate_groups": total_exact,
                "similar_item_groups": total_similar,
                "trigger_conflict_groups": len(result["trigger_conflicts"])
            }

        if self.verbose:
            result["details"] = {
                "files": self.files_checked,
                "all_automations": [
                    {"alias": a["alias"], "file": a["file"], "id": a.get("id")}
                    for a in self.automations
                ],
                "all_scripts": [
                    {"alias": s["alias"], "file": s["file"], "script_id": s.get("script_id")}
                    for s in self.scripts
                ]
            }

        return result

    def _find_exact_duplicates(self, items: List[dict], item_type: str) -> List[dict]:
        """Find items with identical hashes."""
        hash_groups = defaultdict(list)

        for item in items:
            hash_groups[item["hash"]].append(item)

        duplicates = []
        for hash_val, group in hash_groups.items():
            if len(group) > 1:
                duplicates.append({
                    "type": item_type,
                    "count": len(group),
                    "items": [
                        {
                            "alias": item["alias"],
                            "file": item["file"],
                            "id": item.get("id") or item.get("script_id"),
                            "index": item.get("index")
                        }
                        for item in group
                    ]
                })

        return duplicates

    def _find_similar_items(self, items: List[dict], item_type: str) -> List[dict]:
        """Find items with similar names or overlapping entities."""
        similar_groups = []
        checked_pairs = set()

        for i, item1 in enumerate(items):
            for j, item2 in enumerate(items):
                if i >= j:
                    continue

                pair_key = (item1["hash"], item2["hash"])
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)

                # Skip if they're exact duplicates (already reported)
                if item1["hash"] == item2["hash"]:
                    continue

                similarity = self._calculate_similarity(item1, item2)
                if similarity >= self.SIMILARITY_THRESHOLD:
                    similar_groups.append({
                        "type": item_type,
                        "similarity": f"{similarity:.0%}",
                        "reason": self._get_similarity_reason(item1, item2),
                        "items": [
                            {
                                "alias": item1["alias"],
                                "file": item1["file"],
                                "id": item1.get("id") or item1.get("script_id")
                            },
                            {
                                "alias": item2["alias"],
                                "file": item2["file"],
                                "id": item2.get("id") or item2.get("script_id")
                            }
                        ]
                    })

        return similar_groups

    def _calculate_similarity(self, item1: dict, item2: dict) -> float:
        """Calculate similarity between two items."""
        scores = []

        # Name similarity
        name_sim = SequenceMatcher(
            None,
            item1["alias"].lower(),
            item2["alias"].lower()
        ).ratio()
        scores.append(name_sim * 0.3)  # 30% weight

        # Entity overlap
        entities1 = item1.get("entities", set())
        entities2 = item2.get("entities", set())
        if entities1 and entities2:
            overlap = len(entities1 & entities2) / max(len(entities1 | entities2), 1)
            scores.append(overlap * 0.4)  # 40% weight

        # Trigger similarity (for automations)
        if "triggers" in item1 and "triggers" in item2:
            trigger_sim = self._compare_structures(item1["triggers"], item2["triggers"])
            scores.append(trigger_sim * 0.3)  # 30% weight

        # Sequence similarity (for scripts)
        if "sequence" in item1 and "sequence" in item2:
            seq_sim = self._compare_structures(item1["sequence"], item2["sequence"])
            scores.append(seq_sim * 0.3)

        return sum(scores) / max(len(scores) * 0.3, 0.3)  # Normalize

    def _compare_structures(self, struct1, struct2) -> float:
        """Compare two structures for similarity."""
        str1 = json.dumps(struct1, sort_keys=True)
        str2 = json.dumps(struct2, sort_keys=True)
        return SequenceMatcher(None, str1, str2).ratio()

    def _get_similarity_reason(self, item1: dict, item2: dict) -> str:
        """Get a human-readable reason for similarity."""
        reasons = []

        # Check name similarity
        name_sim = SequenceMatcher(
            None,
            item1["alias"].lower(),
            item2["alias"].lower()
        ).ratio()
        if name_sim > 0.7:
            reasons.append("similar names")

        # Check entity overlap
        entities1 = item1.get("entities", set())
        entities2 = item2.get("entities", set())
        if entities1 and entities2:
            common = entities1 & entities2
            if common:
                reasons.append(f"shared entities: {', '.join(list(common)[:3])}")

        # Check trigger similarity
        if "triggers" in item1 and "triggers" in item2:
            if self._compare_structures(item1["triggers"], item2["triggers"]) > 0.8:
                reasons.append("similar triggers")

        return "; ".join(reasons) if reasons else "structural similarity"

    def _find_trigger_conflicts(self) -> List[dict]:
        """Find automations with potentially conflicting triggers."""
        trigger_groups = defaultdict(list)

        for auto in self.automations:
            for trigger in auto.get("triggers", []):
                if isinstance(trigger, dict):
                    # Create a simplified trigger key
                    trigger_type = trigger.get("trigger") or trigger.get("platform", "unknown")
                    entity = trigger.get("entity_id", "")

                    if isinstance(entity, list):
                        entity = ",".join(sorted(entity))

                    key = f"{trigger_type}:{entity}"
                    if entity:  # Only track if there's an entity
                        trigger_groups[key].append(auto)

        conflicts = []
        for trigger_key, autos in trigger_groups.items():
            if len(autos) > 1:
                conflicts.append({
                    "trigger": trigger_key,
                    "count": len(autos),
                    "automations": [
                        {
                            "alias": a["alias"],
                            "file": a["file"],
                            "id": a.get("id")
                        }
                        for a in autos
                    ]
                })

        return conflicts


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: find_duplicates.py <directory_or_file> [--verbose]",
            "examples": [
                "python3 find_duplicates.py /config",
                "python3 find_duplicates.py automations.yaml --verbose"
            ]
        }, indent=2))
        sys.exit(1)

    path = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    finder = DuplicateFinder(verbose=verbose)
    result = finder.scan_path(path)

    print(json.dumps(result, indent=2, default=str))

    # Exit code based on findings
    # Only exit 1 for actual duplicates, not trigger conflicts (often intentional)
    exact_dupes = result.get("exact_duplicates", {})
    similar = result.get("similar_items", {})
    has_real_duplicates = (
        len(exact_dupes.get("automations", [])) > 0 or
        len(exact_dupes.get("scripts", [])) > 0 or
        len(similar.get("automations", [])) > 0 or
        len(similar.get("scripts", [])) > 0
    )
    if has_real_duplicates:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
