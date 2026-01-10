#!/usr/bin/env python3
"""
Aggregate catalog-info.yaml files from multiple repositories.

Usage: python aggregate-metadata.py [repos_directory]
Output: JSON containing aggregated metadata from all repos
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Load and parse a YAML file."""
    try:
        import yaml
        with open(file_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # Fallback: simple parsing for our schema
        return simple_parse_yaml(file_path)


def simple_parse_yaml(file_path: Path) -> Dict[str, Any]:
    """Simple YAML parser for catalog-info.yaml structure."""
    result = {}
    current_section = None
    current_list = None
    list_indent = 0

    with open(file_path, 'r') as f:
        for line in f:
            stripped = line.rstrip()
            if not stripped or stripped.startswith('#'):
                continue

            indent = len(line) - len(line.lstrip())

            # Top level sections
            if indent == 0 and ':' in stripped:
                key = stripped.split(':', 1)[0]
                if key in ['apiVersion', 'kind']:
                    result[key] = stripped.split(':', 1)[1].strip().strip('"').strip("'")
                elif key == 'metadata':
                    result['metadata'] = {}
                    current_section = result['metadata']
                elif key == 'spec':
                    result['spec'] = {}
                    current_section = result['spec']
                continue

            # Within a section
            if current_section is not None:
                # Check for list item
                if stripped.startswith('- ') and ':' in stripped[2:]:
                    if current_list is None:
                        current_list = []
                        # Find the key in current_section that should hold this list
                        list_indent = indent

                    item_content = stripped[2:]
                    if ':' in item_content:
                        item_key = item_content.split(':', 1)[0].strip()
                        item_value = item_content.split(':', 1)[1].strip().strip('"').strip("'")
                        current_list.append({item_key: item_value})
                    continue

                # End of list
                if current_list is not None and indent <= list_indent:
                    # Assign list to section (simplified - assumes single list per section)
                    if isinstance(current_section, dict):
                        # Determine which key this list belongs to
                        for key in list(current_section.keys())[-1:]:
                            current_section[key] = current_list
                    current_list = None

                # Key-value pair
                if ':' in stripped:
                    key = stripped.split(':', 1)[0].strip()
                    value = stripped.split(':', 1)[1].strip().strip('"').strip("'")
                    if value and value != 'null' and value != '~':
                        current_section[key] = value
                    else:
                        current_section[key] = None

    return result


def find_catalog_files(repos_dir: Path) -> List[tuple[str, Path]]:
    """Find all catalog-info.yaml files in repository directories."""
    catalog_files = []

    if not repos_dir.exists():
        return catalog_files

    for item in repos_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            catalog_path = item / "catalog-info.yaml"
            if catalog_path.exists():
                catalog_files.append((item.name, catalog_path))

    return catalog_files


def aggregate_metadata(repos_dir: Path) -> Dict[str, Any]:
    """Aggregate metadata from all repositories."""
    catalog_files = find_catalog_files(repos_dir)

    aggregated = {
        "repositories": [],
        "components": {},
        "domains": {},
        "owners": {},
        "types": {
            "gateway": [],
            "service": [],
            "worker": [],
            "library": [],
            "frontend": [],
            "database": [],
        },
        "dependencies": {},
        "events": {
            "topics": set(),
            "producers": {},
            "consumers": {},
        },
        "routes": [],
        "missing_metadata": [],
    }

    for repo_name, catalog_path in catalog_files:
        try:
            catalog = load_yaml(catalog_path)

            # Extract basic info
            metadata = catalog.get("metadata", {})
            spec = catalog.get("spec", {})

            name = metadata.get("name", repo_name)
            component_type = spec.get("type", "unknown")
            domain = spec.get("domain", "unknown")
            owner = spec.get("owner", "unknown")

            # Store component
            aggregated["components"][name] = {
                "name": name,
                "repo": repo_name,
                "description": metadata.get("description", ""),
                "type": component_type,
                "domain": domain,
                "owner": owner,
                "lifecycle": spec.get("lifecycle", "unknown"),
                "runtime": spec.get("runtime", "unknown"),
                "framework": spec.get("framework", "unknown"),
                "catalog_path": str(catalog_path),
            }

            # Track by type
            if component_type in aggregated["types"]:
                aggregated["types"][component_type].append(name)

            # Track by domain
            if domain != "unknown":
                if domain not in aggregated["domains"]:
                    aggregated["domains"][domain] = []
                aggregated["domains"][domain].append(name)

            # Track by owner
            if owner != "unknown":
                if owner not in aggregated["owners"]:
                    aggregated["owners"][owner] = []
                aggregated["owners"][owner].append(name)

            # Dependencies
            depends_on = spec.get("dependsOn", [])
            if depends_on:
                aggregated["dependencies"][name] = [
                    dep.get("component", dep) if isinstance(dep, dict) else dep
                    for dep in depends_on
                ]

            # Events
            for producer in spec.get("eventProducers", []):
                topic = producer.get("topic", "")
                if topic:
                    aggregated["events"]["topics"].add(topic)
                    if topic not in aggregated["events"]["producers"]:
                        aggregated["events"]["producers"][topic] = []
                    aggregated["events"]["producers"][topic].append(name)

            for consumer in spec.get("eventConsumers", []):
                topic = consumer.get("topic", "")
                if topic:
                    aggregated["events"]["topics"].add(topic)
                    if topic not in aggregated["events"]["consumers"]:
                        aggregated["events"]["consumers"][topic] = []
                    aggregated["events"]["consumers"][topic].append(name)

            # Routes (for gateways)
            if component_type == "gateway":
                for route in spec.get("routes", []):
                    aggregated["routes"].append({
                        "gateway": name,
                        "path": route.get("path", ""),
                        "methods": route.get("methods", []),
                        "forwardsTo": route.get("forwardsTo"),
                        "handler": route.get("handler"),
                    })

        except Exception as e:
            print(f"Warning: Failed to parse {catalog_path}: {e}", file=sys.stderr)
            aggregated["missing_metadata"].append(repo_name)

    # Check for repos without catalog-info.yaml
    for item in repos_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            catalog_path = item / "catalog-info.yaml"
            if not catalog_path.exists() and item.name not in aggregated["missing_metadata"]:
                aggregated["missing_metadata"].append(item.name)

    # Convert sets to lists for JSON serialization
    aggregated["events"]["topics"] = sorted(list(aggregated["events"]["topics"]))

    return aggregated


def print_summary(aggregated: Dict[str, Any]):
    """Print a summary of aggregated metadata."""
    print(f"# Architecture Summary")
    print()
    print(f"- **Total repositories scanned:** {len(aggregated['components']) + len(aggregated['missing_metadata'])}")
    print(f"- **Components with metadata:** {len(aggregated['components'])}")
    print(f"- **Missing metadata:** {len(aggregated['missing_metadata'])}")
    print()
    print(f"## Components by Type")
    for comp_type, components in aggregated["types"].items():
        if components:
            print(f"- **{comp_type}:** {', '.join(components)}")
    print()
    print(f"## Domains")
    for domain, components in aggregated["domains"].items():
        print(f"- **{domain}:** {', '.join(components)}")
    print()

    if aggregated["missing_metadata"]:
        print(f"## Missing Metadata")
        for repo in aggregated["missing_metadata"]:
            print(f"- {repo}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate catalog-info.yaml files from multiple repositories"
    )
    parser.add_argument("repos_dir", nargs="?", default="repos",
                       help="Directory containing repositories")
    parser.add_argument("--format", choices=["json", "summary"], default="summary",
                       help="Output format")
    parser.add_argument("--output", "-o", help="Write to file instead of stdout")
    args = parser.parse_args()

    repos_dir = Path(args.repos_dir)

    if not repos_dir.exists():
        print(f"Error: Directory '{repos_dir}' does not exist", file=sys.stderr)
        return 1

    aggregated = aggregate_metadata(repos_dir)

    if args.format == "json":
        output = json.dumps(aggregated, indent=2, default=str)
    else:
        output = ""
        # Capture summary output
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        print_summary(aggregated)
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

    if args.output:
        Path(args.output).write_text(output)
        print(f"Wrote {args.format} output to {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
