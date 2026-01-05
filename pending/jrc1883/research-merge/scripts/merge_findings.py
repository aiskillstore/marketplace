#!/usr/bin/env python3
"""
Research Findings Merge Script.

Merge findings from multiple research notes into a unified document.

Usage:
    python merge_findings.py FILE1 FILE2 [FILE3...] [--output OUTPUT]

Output:
    Merged research document
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


def parse_frontmatter(content: str) -> tuple:
    """Parse YAML frontmatter and content."""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1].strip(), parts[2].strip()
    return '', content


def extract_metadata(frontmatter: str) -> Dict[str, Any]:
    """Extract metadata from frontmatter."""
    metadata = {}

    # Simple YAML parsing
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Handle arrays
            if value.startswith('['):
                value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]

            metadata[key] = value

    return metadata


def extract_sections(content: str) -> Dict[str, str]:
    """Extract sections from markdown content."""
    sections = {}
    current_section = None
    current_content = []

    for line in content.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)

    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections


def extract_bullet_points(content: str) -> List[str]:
    """Extract bullet points from content."""
    points = []
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('- ') or line.startswith('* '):
            points.append(line[2:].strip())
    return points


def dedupe_points(points: List[str], threshold: float = 0.8) -> List[str]:
    """Remove duplicate or very similar points."""
    unique = []

    for point in points:
        is_dup = False
        point_words = set(point.lower().split())

        for existing in unique:
            existing_words = set(existing.lower().split())
            if not point_words or not existing_words:
                continue

            # Calculate Jaccard similarity
            intersection = len(point_words & existing_words)
            union = len(point_words | existing_words)
            similarity = intersection / union if union > 0 else 0

            if similarity > threshold:
                is_dup = True
                # Keep longer version
                if len(point) > len(existing):
                    unique.remove(existing)
                    unique.append(point)
                break

        if not is_dup:
            unique.append(point)

    return unique


def merge_research_notes(files: List[Path]) -> Dict[str, Any]:
    """Merge multiple research notes."""
    merged = {
        "title": "",
        "sources": [],
        "tags": set(),
        "findings": [],
        "code_examples": [],
        "references": [],
        "questions": []
    }

    all_sections = {}

    for file_path in files:
        if not file_path.exists():
            continue

        content = file_path.read_text()
        frontmatter, body = parse_frontmatter(content)
        metadata = extract_metadata(frontmatter)
        sections = extract_sections(body)

        # Collect metadata
        merged["sources"].append(str(file_path))

        if metadata.get("tags"):
            if isinstance(metadata["tags"], list):
                merged["tags"].update(metadata["tags"])
            else:
                merged["tags"].add(metadata["tags"])

        # Merge sections
        for section_name, section_content in sections.items():
            if section_name not in all_sections:
                all_sections[section_name] = []
            all_sections[section_name].append(section_content)

    # Process merged sections
    if "Key Findings" in all_sections:
        all_findings = []
        for content in all_sections["Key Findings"]:
            all_findings.extend(extract_bullet_points(content))
        merged["findings"] = dedupe_points(all_findings)

    if "Questions & Follow-ups" in all_sections:
        all_questions = []
        for content in all_sections["Questions & Follow-ups"]:
            all_questions.extend(extract_bullet_points(content))
        merged["questions"] = dedupe_points(all_questions)

    if "References" in all_sections:
        all_refs = []
        for content in all_sections["References"]:
            all_refs.extend(extract_bullet_points(content))
        merged["references"] = dedupe_points(all_refs)

    # Convert set to list
    merged["tags"] = list(merged["tags"])

    return merged


def generate_merged_document(merged: Dict[str, Any], title: str = None) -> str:
    """Generate merged research document."""
    lines = [
        "---",
        f"title: \"{title or 'Merged Research'}\"",
        f"date: {datetime.now().strftime('%Y-%m-%d')}",
        f"tags: [{', '.join(merged['tags'])}]",
        f"sources: [{', '.join(merged['sources'])}]",
        "status: draft",
        "---",
        "",
        f"# {title or 'Merged Research'}",
        "",
        "## Overview",
        "",
        f"This document merges research from {len(merged['sources'])} source(s).",
        "",
        "## Key Findings",
        ""
    ]

    for finding in merged["findings"]:
        lines.append(f"- {finding}")

    if merged["questions"]:
        lines.extend([
            "",
            "## Questions & Follow-ups",
            ""
        ])
        for question in merged["questions"]:
            lines.append(f"- [ ] {question}")

    if merged["references"]:
        lines.extend([
            "",
            "## References",
            ""
        ])
        for ref in merged["references"]:
            lines.append(f"- {ref}")

    lines.extend([
        "",
        "## Sources Merged",
        ""
    ])
    for source in merged["sources"]:
        lines.append(f"- {source}")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Merge research findings")
    parser.add_argument("files", nargs="+", help="Research files to merge")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--title", "-t", help="Title for merged document")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be merged")
    args = parser.parse_args()

    files = [Path(f) for f in args.files]

    # Validate files exist
    missing = [f for f in files if not f.exists()]
    if missing:
        print(json.dumps({
            "success": False,
            "error": f"Files not found: {[str(f) for f in missing]}"
        }, indent=2))
        return 1

    if args.dry_run:
        print(json.dumps({
            "operation": "merge_findings",
            "dry_run": True,
            "files": [str(f) for f in files],
            "output": args.output or "stdout"
        }, indent=2))
        return 0

    # Merge
    merged = merge_research_notes(files)

    # Output
    if args.format == "json":
        output = json.dumps({
            "operation": "merge_findings",
            "success": True,
            "files_merged": len(files),
            **merged
        }, indent=2)
    else:
        output = generate_merged_document(merged, args.title)

    if args.output:
        Path(args.output).write_text(output)
        print(json.dumps({
            "operation": "merge_findings",
            "success": True,
            "files_merged": len(files),
            "output_file": args.output
        }, indent=2))
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
