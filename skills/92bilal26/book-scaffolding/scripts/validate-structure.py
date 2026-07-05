#!/usr/bin/env python3
"""
Book Structure Validator - Check chapter dependency cycles and validate structure

This script validates that a book outline:
1. Has no circular chapter dependencies (DAG property)
2. All chapter references are valid (no broken dependencies)
3. Prerequisites chains are complete
4. Identifies orphaned chapters (unreachable from start)
5. Validates required fields are present

Usage:
    python validate-structure.py book-outline.yml

Output: JSON with validation results
"""

import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def load_book_outline(filepath: str) -> dict[str, Any]:
    """Load and parse book outline YAML file."""
    if yaml is None:
        return {
            "error": "PyYAML not installed. Install with: pip install pyyaml"
        }

    try:
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
        return data
    except Exception as e:
        return {"error": f"Failed to parse YAML: {str(e)}"}


def extract_chapters(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Extract all chapters from book outline into flat dictionary."""
    chapters = {}

    if "parts" not in data:
        return chapters

    for part in data["parts"]:
        if "chapters" not in part:
            continue

        for chapter in part["chapters"]:
            chapter_id = chapter.get("id")
            if chapter_id:
                chapters[chapter_id] = {
                    "id": chapter_id,
                    "number": chapter.get("number"),
                    "title": chapter.get("title", "(no title)"),
                    "dependencies": chapter.get("dependencies", {}),
                    "purpose": chapter.get("purpose", "Unknown"),
                    "part": part.get("title", "Unknown Part"),
                }

    return chapters


def build_dependency_graph(chapters: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    """Build adjacency list representation of chapter dependencies."""
    graph = defaultdict(list)

    for chapter_id, chapter_data in chapters.items():
        deps = chapter_data.get("dependencies", {})
        required_deps = deps.get("required", [])

        # Add edges from dependencies to this chapter
        for dep_id in required_deps:
            graph[dep_id].append(chapter_id)

        # Ensure chapter exists in graph even if no dependencies
        if chapter_id not in graph:
            graph[chapter_id] = []

    return graph


def detect_cycles(graph: dict[str, list[str]], chapters: dict[str, dict[str, Any]]) -> tuple[bool, list[list[str]]]:
    """
    Detect circular dependencies using DFS.

    Returns:
        (has_cycles, list_of_cycles)
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    parent = {node: None for node in graph}
    cycles = []

    def dfs(node: str, path: list[str]) -> None:
        color[node] = GRAY
        path.append(node)

        for neighbor in graph.get(node, []):
            if color[neighbor] == WHITE:
                parent[neighbor] = node
                dfs(neighbor, path[:])
            elif color[neighbor] == GRAY:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        color[node] = BLACK

    for node in graph:
        if color[node] == WHITE:
            dfs(node, [])

    return len(cycles) > 0, cycles


def validate_dependencies(chapters: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate that all chapter dependencies reference valid chapters."""
    errors = []

    for chapter_id, chapter_data in chapters.items():
        deps = chapter_data.get("dependencies", {})

        # Check required dependencies
        for dep_type in ["required", "recommended", "optional"]:
            dep_list = deps.get(dep_type, [])
            for dep_id in dep_list:
                if dep_id not in chapters:
                    errors.append({
                        "chapter": chapter_id,
                        "title": chapter_data.get("title"),
                        "error": f"Invalid {dep_type} dependency: '{dep_id}' does not exist",
                        "severity": "error" if dep_type == "required" else "warning",
                    })

    return errors


def find_orphaned_chapters(chapters: dict[str, dict[str, Any]]) -> list[str]:
    """
    Find chapters that are unreachable from any first chapter.

    A chapter is orphaned if it has required dependencies but is never
    listed as a dependency itself (dead end in the dependency chain).
    """
    # Find chapters with no required dependencies (potential starting points)
    start_chapters = []
    for chapter_id, chapter_data in chapters.items():
        deps = chapter_data.get("dependencies", {})
        required = deps.get("required", [])
        if len(required) == 0:
            start_chapters.append(chapter_id)

    if not start_chapters:
        return []  # If no start chapters, can't determine orphans

    # BFS from all start chapters to find reachable chapters
    reachable = set()
    queue = deque(start_chapters)
    reachable.update(start_chapters)

    # Build forward graph (chapter -> chapters that depend on it)
    forward_graph = defaultdict(list)
    for chapter_id, chapter_data in chapters.items():
        deps = chapter_data.get("dependencies", {})
        for dep_id in deps.get("required", []):
            forward_graph[dep_id].append(chapter_id)

    while queue:
        current = queue.popleft()
        for dependent in forward_graph.get(current, []):
            if dependent not in reachable:
                reachable.add(dependent)
                queue.append(dependent)

    # Orphans are chapters not reachable
    all_chapters = set(chapters.keys())
    orphaned = all_chapters - reachable

    return list(orphaned)


def validate_required_fields(data: dict[str, Any]) -> list[str]:
    """Validate that required fields are present in book outline."""
    errors = []

    # Book-level required fields
    required_book_fields = ["book_title", "target_audience", "prerequisites"]
    for field in required_book_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required book field: '{field}'")

    # Part-level validation
    if "parts" not in data or not data["parts"]:
        errors.append("No parts defined in book outline")
        return errors

    for part_idx, part in enumerate(data["parts"]):
        part_id = part.get("id", f"part-{part_idx + 1}")

        required_part_fields = ["title", "purpose"]
        for field in required_part_fields:
            if field not in part or not part[field]:
                errors.append(f"Part '{part_id}': Missing required field '{field}'")

        # Chapter-level validation
        if "chapters" not in part or not part["chapters"]:
            errors.append(f"Part '{part_id}': No chapters defined")
            continue

        for chapter_idx, chapter in enumerate(part["chapters"]):
            chapter_id = chapter.get("id", f"ch-{chapter_idx + 1}")

            required_chapter_fields = ["id", "title", "purpose", "synopsis"]
            for field in required_chapter_fields:
                if field not in chapter or not chapter[field]:
                    errors.append(f"Chapter '{chapter_id}': Missing required field '{field}'")

    return errors


def analyze_prerequisite_chains(chapters: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Analyze prerequisite chains for depth and complexity."""
    analysis = {
        "max_chain_depth": 0,
        "chapters_by_depth": defaultdict(list),
        "chains": {},
    }

    def get_chain_depth(chapter_id: str, visited: set[str]) -> int:
        if chapter_id in visited:
            return 0  # Cycle detected, don't count

        visited.add(chapter_id)
        chapter_data = chapters.get(chapter_id, {})
        deps = chapter_data.get("dependencies", {})
        required = deps.get("required", [])

        if not required:
            return 0

        max_depth = 0
        for dep_id in required:
            depth = get_chain_depth(dep_id, visited.copy())
            max_depth = max(max_depth, depth)

        return max_depth + 1

    for chapter_id in chapters:
        depth = get_chain_depth(chapter_id, set())
        analysis["chapters_by_depth"][depth].append(chapter_id)
        analysis["max_chain_depth"] = max(analysis["max_chain_depth"], depth)
        analysis["chains"][chapter_id] = depth

    # Convert defaultdict to regular dict for JSON serialization
    analysis["chapters_by_depth"] = dict(analysis["chapters_by_depth"])

    return analysis


def validate_book_structure(filepath: str) -> dict[str, Any]:
    """
    Validate complete book structure.

    Returns:
        {
            "valid": bool,
            "errors": [list of error dicts],
            "warnings": [list of warning dicts],
            "structure_analysis": {
                "total_chapters": int,
                "core_chapters": int,
                "optional_chapters": int,
                "has_cycles": bool,
                "cycles": [list of cycles],
                "orphaned_chapters": [list],
                "max_prerequisite_depth": int
            }
        }
    """
    # Load data
    data = load_book_outline(filepath)

    if "error" in data:
        return {
            "valid": False,
            "errors": [{"message": data["error"], "severity": "error"}],
            "warnings": [],
            "structure_analysis": {},
        }

    # Extract chapters
    chapters = extract_chapters(data)

    if not chapters:
        return {
            "valid": False,
            "errors": [{"message": "No chapters found in book outline", "severity": "error"}],
            "warnings": [],
            "structure_analysis": {},
        }

    errors = []
    warnings = []

    # Validate required fields
    field_errors = validate_required_fields(data)
    errors.extend([{"message": err, "severity": "error"} for err in field_errors])

    # Validate dependencies
    dep_errors = validate_dependencies(chapters)
    for err in dep_errors:
        if err["severity"] == "error":
            errors.append({"message": f"{err['chapter']}: {err['error']}", "severity": "error"})
        else:
            warnings.append({"message": f"{err['chapter']}: {err['error']}", "severity": "warning"})

    # Build dependency graph
    graph = build_dependency_graph(chapters)

    # Detect cycles
    has_cycles, cycles = detect_cycles(graph, chapters)

    if has_cycles:
        for cycle in cycles:
            cycle_str = " → ".join([chapters.get(ch, {}).get("title", ch) for ch in cycle])
            errors.append({
                "message": f"Circular dependency detected: {cycle_str}",
                "severity": "error",
                "cycle": cycle,
            })

    # Find orphaned chapters
    orphaned = find_orphaned_chapters(chapters)

    if orphaned:
        for orphan_id in orphaned:
            orphan_data = chapters.get(orphan_id, {})
            warnings.append({
                "message": f"Orphaned chapter: '{orphan_data.get('title', orphan_id)}' is unreachable from starting chapters",
                "severity": "warning",
                "chapter": orphan_id,
            })

    # Analyze prerequisite chains
    chain_analysis = analyze_prerequisite_chains(chapters)

    # Count chapter types
    core_count = sum(1 for ch in chapters.values() if ch.get("purpose") == "Core")
    optional_count = sum(1 for ch in chapters.values() if ch.get("purpose") == "Optional")

    # Build structure analysis
    structure_analysis = {
        "total_chapters": len(chapters),
        "core_chapters": core_count,
        "optional_chapters": optional_count,
        "has_cycles": has_cycles,
        "cycles": [
            {
                "cycle": cycle,
                "titles": [chapters.get(ch, {}).get("title", ch) for ch in cycle]
            }
            for cycle in cycles
        ],
        "orphaned_chapters": [
            {
                "id": ch_id,
                "title": chapters.get(ch_id, {}).get("title", ch_id)
            }
            for ch_id in orphaned
        ],
        "max_prerequisite_depth": chain_analysis["max_chain_depth"],
        "chapters_by_depth": chain_analysis["chapters_by_depth"],
    }

    # Overall validation status
    is_valid = len(errors) == 0

    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "structure_analysis": structure_analysis,
    }


def main() -> None:
    """Parse arguments and validate book structure."""
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "valid": False,
                    "error": "Usage: python validate-structure.py <book-outline.yml>",
                }
            )
        )
        sys.exit(1)

    outline_file = sys.argv[1]

    # Check file exists
    if not Path(outline_file).exists():
        print(json.dumps({"valid": False, "error": f"File not found: {outline_file}"}))
        sys.exit(1)

    # Validate
    results = validate_book_structure(outline_file)
    print(json.dumps(results, indent=2))

    # Exit with non-zero if validation failed
    sys.exit(0 if results["valid"] else 1)


if __name__ == "__main__":
    main()
