#!/usr/bin/env python3
"""
Generate Mermaid diagrams from aggregated metadata.

Usage: python generate-mermaid.py aggregated.json
Output: Mermaid diagrams for dependency graph, request flow, event topology
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Set


def load_aggregated(file_path: Path) -> Dict[str, Any]:
    """Load aggregated metadata JSON."""
    with open(file_path, 'r') as f:
        return json.load(f)


def generate_dependency_graph(aggregated: Dict[str, Any]) -> str:
    """Generate service dependency graph as Mermaid."""
    lines = ["```mermaid", "graph TD"]

    # Track edges to avoid duplicates
    edges = set()

    # Generate nodes
    for name, comp in aggregated["components"].items():
        comp_type = comp["type"]

        # Node label
        label = f"{name}<br/>type: {comp_type}"
        if comp.get("domain") != "unknown":
            label += f"<br/>domain: {comp['domain']}"

        # Node shape based on type
        if comp_type == "database":
            lines.append(f'    {name}[({label})]')
        elif comp_type == "gateway":
            lines.append(f'    {{name}}[{{label}}]')
        else:
            lines.append(f'    {name}[{label}]')

        # Add dependency edges
        if name in aggregated.get("dependencies", {}):
            for dep in aggregated["dependencies"][name]:
                edge = f"{name} --> {dep}"
                if edge not in edges:
                    edges.add(edge)

    # Add all edges
    for edge in sorted(edges):
        lines.append(f"    {edge}")

    # Add styling
    lines.append("")
    lines.append("    classDef gateway fill:#e1f5fe,stroke:#01579b")
    lines.append("    classDef service fill:#f3e5f5,stroke:#4a148c")
    lines.append("    classDef worker fill:#fff3e0,stroke:#e65100")
    lines.append("    classDef library fill:#f3e5f5,stroke:#7b1fa2,stroke-dasharray: 5 5")
    lines.append("    classDef database fill:#e8f5e9,stroke:#1b5e20")
    lines.append("    classDef frontend fill:#fce4ec,stroke:#880e4f")
    lines.append("")

    # Assign classes
    for name, comp in aggregated["components"].items():
        comp_type = comp["type"]
        if comp_type in ["gateway", "service", "worker", "library", "database", "frontend"]:
            lines.append(f"    class {name} {comp_type}")

    lines.append("```")
    return "\n".join(lines)


def generate_request_flow(aggregated: Dict[str, Any]) -> str:
    """Generate request flow map as Mermaid."""
    lines = ["```mermaid", "flowchart LR"]
    lines.append('    Client[External Client]')

    # Find gateways
    gateways = [name for name, comp in aggregated["components"].items()
                if comp["type"] == "gateway"]

    # Track added nodes
    added = set()

    # Connect clients to gateways
    for gateway in gateways:
        lines.append(f'    Client -->|API| {gateway}')
        added.add(gateway)

        # Add routes from this gateway
        for route in aggregated.get("routes", []):
            if route["gateway"] == gateway:
                target = route.get("forwardsTo") or route.get("handler")
                path = route.get("path", "")

                if target and target != "this":
                    if target not in added:
                        lines.append(f'    {gateway}[{gateway}] -->|{path}| {target}')
                        added.add(target)
                    else:
                        lines.append(f'    {gateway} -->|{path}| {target}')

    # Add service dependencies to databases
    for name, comp in aggregated["components"].items():
        if comp["type"] in ["service", "gateway"]:
            for dep in aggregated.get("dependencies", {}).get(name, []):
                dep_comp = aggregated["components"].get(dep, {})
                if dep_comp.get("type") == "database":
                    lines.append(f'    {name} --> {dep}[({dep})]')

    # Styling
    lines.append("")
    lines.append("    classDef gateway fill:#e1f5fe,stroke:#01579b,stroke-width:2px")
    lines.append("    classDef service fill:#f3e5f5,stroke:#4a148c")
    lines.append("    classDef database fill:#e8f5e9,stroke:#1b5e20")
    lines.append("    classDef client fill:#ffebee,stroke:#b71c1c")
    lines.append("")
    lines.append("    class Client client")
    lines.append("    class " + " ".join(gateways) + f" {'gateway' if gateways else ''}")
    lines.append("```")

    return "\n".join(lines)


def generate_event_topology(aggregated: Dict[str, Any]) -> str:
    """Generate event topology as Mermaid."""
    lines = ["```mermaid", "graph LR"]

    events = aggregated.get("events", {})
    topics = sorted(events.get("topics", []))
    producers = events.get("producers", {})
    consumers = events.get("consumers", {})

    # Track added nodes
    added = set()

    # Create topic nodes
    for topic in topics:
        safe_topic = topic.replace(".", "_").replace("-", "_")
        lines.append(f'    {safe_topic}[((Kafka: {topic}))]')
        added.add(safe_topic)

    # Add producer edges
    for topic, services in producers.items():
        safe_topic = topic.replace(".", "_").replace("-", "_")
        for service in services:
            if service not in added:
                lines.append(f'    {service}[{service}]')
                added.add(service)
            lines.append(f'    {service} -->|{topic}| {safe_topic}')

    # Add consumer edges
    for topic, services in consumers.items():
        safe_topic = topic.replace(".", "_").replace("-", "_")
        for service in services:
            if service not in added:
                lines.append(f'    {service}[{service}]')
                added.add(service)
            lines.append(f'    {safe_topic} -->|{topic}| {service}')

    # Styling
    lines.append("")
    lines.append("    classDef producer fill:#e8f5e9,stroke:#2e7d32")
    lines.append("    classDef consumer fill:#fff3e0,stroke:#e65100")
    lines.append("    classDef topic fill:#e1f5fe,stroke:#0277bd,stroke-width:2px")
    lines.append("")

    # Classify
    all_producers = set()
    for services in producers.values():
        all_producers.update(services)

    all_consumers = set()
    for services in consumers.values():
        all_consumers.update(services)

    lines.append("    class " + " ".join(sorted(all_producers)) + f" {'producer' if all_producers else ''}")
    lines.append("    class " + " ".join(sorted(all_consumers)) + f" {'consumer' if all_consumers else ''}")
    lines.append("    class " + " ".join(t.replace(".", "_").replace("-", "_") for t in topics) + " topic")

    lines.append("```")
    return "\n".join(lines)


def generate_service_groupings(aggregated: Dict[str, Any]) -> str:
    """Generate service groupings as Markdown tables."""
    lines = ["## Services by Domain", ""]
    lines.append("| Domain | Services | Owner |")
    lines.append("|--------|----------|-------|")

    for domain, services in sorted(aggregated.get("domains", {}).items()):
        # Get owner for this domain (first service's owner)
        owner = "unknown"
        for service in services:
            comp = aggregated["components"].get(service, {})
            if comp.get("owner") != "unknown":
                owner = comp["owner"]
                break

        lines.append(f"| {domain} | {', '.join(services)} | {owner} |")

    lines.append("")
    lines.append("## Services by Type")
    lines.append("")
    lines.append("| Type | Services |")
    lines.append("|------|----------|")

    for comp_type, services in aggregated["types"].items():
        if services:
            lines.append(f"| {comp_type} | {', '.join(services)} |")

    return "\n".join(lines)


def generate_full_view(aggregated: Dict[str, Any]) -> str:
    """Generate complete architecture view with all diagrams."""
    lines = ["# Architecture View", ""]
    lines.append("## Summary")
    lines.append(f"- **Total components:** {len(aggregated['components'])}")
    lines.append(f"- **Components by type:**")
    for comp_type, services in aggregated["types"].items():
        if services:
            lines.append(f"  - {comp_type}: {len(services)}")
    lines.append("")

    if aggregated.get("domains"):
        lines.append("## Domains")
        for domain, services in sorted(aggregated["domains"].items()):
            lines.append(f"- **{domain}**: {', '.join(services)}")
        lines.append("")

    lines.append("## Service Dependency Graph")
    lines.append(generate_dependency_graph(aggregated))
    lines.append("")

    lines.append("## Request Flow Map")
    lines.append(generate_request_flow(aggregated))
    lines.append("")

    if aggregated["events"]["topics"]:
        lines.append("## Event Topology")
        lines.append(generate_event_topology(aggregated))
        lines.append("")

    lines.append("## Service Groupings")
    lines.append(generate_service_groupings(aggregated))
    lines.append("")

    if aggregated.get("missing_metadata"):
        lines.append("## Missing Metadata")
        lines.append("The following repositories lack catalog-info.yaml:")
        for repo in aggregated["missing_metadata"]:
            lines.append(f"- {repo}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Mermaid diagrams from aggregated metadata"
    )
    parser.add_argument("input_file", help="Aggregated metadata JSON file")
    parser.add_argument("--view", choices=["dependency", "request-flow", "events", "groupings", "full"],
                       default="full", help="Which view to generate")
    parser.add_argument("--output", "-o", help="Write to file instead of stdout")
    args = parser.parse_args()

    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"Error: File '{input_path}' does not exist", file=sys.stderr)
        return 1

    aggregated = load_aggregated(input_path)

    view_generators = {
        "dependency": generate_dependency_graph,
        "request-flow": generate_request_flow,
        "events": generate_event_topology,
        "groupings": generate_service_groupings,
        "full": generate_full_view,
    }

    output = view_generators[args.view](aggregated)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Wrote {args.view} view to {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
