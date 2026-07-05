#!/usr/bin/env python3
"""
Chapter Flow Analyzer - Evaluate cognitive progression and difficulty pacing

This script analyzes book chapter flow for:
1. Cognitive load progression (concept density)
2. Difficulty jumps (sudden increases)
3. Bloom's taxonomy distribution
4. Learning pace (pages per concept, exercises per chapter)
5. Suggestions for reordering or splitting chapters

Usage:
    python analyze-flow.py book-outline.yml

Output: JSON with flow analysis and recommendations
"""

import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def load_book_outline(filepath: str) -> dict[str, Any]:
    """Load and parse book outline YAML file."""
    if yaml is None:
        return {"error": "PyYAML not installed. Install with: pip install pyyaml"}

    try:
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
        return data
    except Exception as e:
        return {"error": f"Failed to parse YAML: {str(e)}"}


def extract_chapter_sequence(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract chapters in reading order with metadata."""
    chapters = []

    if "parts" not in data:
        return chapters

    for part in data["parts"]:
        if "chapters" not in part:
            continue

        for chapter in part["chapters"]:
            chapter_data = {
                "id": chapter.get("id"),
                "number": chapter.get("number"),
                "title": chapter.get("title", "(no title)"),
                "part": part.get("title", "Unknown Part"),
                "purpose": chapter.get("purpose", "Unknown"),
                "estimated_pages": chapter.get("estimated_pages", "Unknown"),
                "key_concepts": chapter.get("key_concepts", []),
                "learning_objectives": chapter.get("learning_objectives", []),
                "dependencies": chapter.get("dependencies", {}),
            }
            chapters.append(chapter_data)

    return chapters


def analyze_concept_density(chapters: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze how many concepts are introduced per chapter."""
    density_analysis = {
        "chapter_densities": [],
        "average_density": 0.0,
        "max_density": 0,
        "min_density": float("inf"),
        "high_density_chapters": [],
        "warnings": [],
    }

    total_concepts = 0

    for chapter in chapters:
        concept_count = len(chapter.get("key_concepts", []))
        total_concepts += concept_count

        chapter_id = chapter.get("id", "unknown")
        chapter_title = chapter.get("title", "Unknown")

        density_analysis["chapter_densities"].append({
            "chapter": chapter_id,
            "title": chapter_title,
            "concept_count": concept_count,
            "density_level": (
                "Low (1-2 concepts)" if concept_count <= 2 else
                "Medium (3-5 concepts)" if concept_count <= 5 else
                "High (6+ concepts)"
            ),
        })

        density_analysis["max_density"] = max(density_analysis["max_density"], concept_count)
        density_analysis["min_density"] = min(density_analysis["min_density"], concept_count)

        # Flag high density chapters
        if concept_count >= 6:
            density_analysis["high_density_chapters"].append({
                "chapter": chapter_id,
                "title": chapter_title,
                "concept_count": concept_count,
            })

    if chapters:
        density_analysis["average_density"] = total_concepts / len(chapters)
    else:
        density_analysis["min_density"] = 0

    # Generate warnings
    if density_analysis["high_density_chapters"]:
        density_analysis["warnings"].append(
            f"Found {len(density_analysis['high_density_chapters'])} chapters with high concept density (6+ concepts). "
            "Consider splitting or adding more scaffolding."
        )

    return density_analysis


def analyze_difficulty_progression(chapters: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze difficulty progression and identify sudden jumps."""
    progression = {
        "progression_sequence": [],
        "difficulty_jumps": [],
        "recommendations": [],
    }

    # Assign difficulty scores based on:
    # - Concept count
    # - Bloom's levels in objectives
    # - Purpose (Core = foundation, Optional = advanced)
    # - Dependencies (more deps = harder)

    prev_score = 0

    for idx, chapter in enumerate(chapters):
        chapter_id = chapter.get("id", "unknown")
        chapter_title = chapter.get("title", "Unknown")

        # Calculate difficulty score
        concept_count = len(chapter.get("key_concepts", []))
        objectives = chapter.get("learning_objectives", [])
        dependencies = chapter.get("dependencies", {})
        required_deps = len(dependencies.get("required", []))

        # Bloom's level scores
        blooms_scores = {
            "Remember": 1,
            "Understand": 2,
            "Apply": 3,
            "Analyze": 4,
            "Evaluate": 5,
            "Create": 6,
        }

        avg_blooms = 0
        if objectives:
            blooms_sum = sum(blooms_scores.get(obj.get("blooms_level", "Understand"), 2) for obj in objectives)
            avg_blooms = blooms_sum / len(objectives)

        # Calculate difficulty score (0-100 scale)
        difficulty_score = (
            (concept_count * 5) +       # Concepts: 5 points each
            (avg_blooms * 5) +          # Bloom's level: up to 30 points
            (required_deps * 3)         # Dependencies: 3 points each
        )

        progression["progression_sequence"].append({
            "chapter": chapter_id,
            "number": chapter.get("number"),
            "title": chapter_title,
            "difficulty_score": round(difficulty_score, 1),
            "concept_count": concept_count,
            "avg_blooms_level": round(avg_blooms, 1),
            "dependency_count": required_deps,
        })

        # Check for difficulty jumps (increase > 20 points)
        if idx > 0 and (difficulty_score - prev_score) > 20:
            progression["difficulty_jumps"].append({
                "from_chapter": chapters[idx - 1].get("title"),
                "to_chapter": chapter_title,
                "score_increase": round(difficulty_score - prev_score, 1),
                "severity": "High" if (difficulty_score - prev_score) > 30 else "Medium",
            })

        prev_score = difficulty_score

    # Generate recommendations
    if progression["difficulty_jumps"]:
        high_jumps = [j for j in progression["difficulty_jumps"] if j["severity"] == "High"]
        if high_jumps:
            progression["recommendations"].append(
                f"Found {len(high_jumps)} high-severity difficulty jumps. "
                "Consider adding intermediate chapters or scaffolding exercises."
            )

    return progression


def analyze_blooms_distribution(chapters: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze distribution of Bloom's taxonomy levels across book."""
    blooms_analysis = {
        "overall_distribution": {
            "Remember": 0,
            "Understand": 0,
            "Apply": 0,
            "Analyze": 0,
            "Evaluate": 0,
            "Create": 0,
        },
        "by_chapter": [],
        "recommendations": [],
    }

    total_objectives = 0

    for chapter in chapters:
        chapter_id = chapter.get("id", "unknown")
        chapter_title = chapter.get("title", "Unknown")
        objectives = chapter.get("learning_objectives", [])

        chapter_blooms = {level: 0 for level in blooms_analysis["overall_distribution"]}

        for obj in objectives:
            level = obj.get("blooms_level", "Understand")
            if level in chapter_blooms:
                chapter_blooms[level] += 1
                blooms_analysis["overall_distribution"][level] += 1
                total_objectives += 1

        blooms_analysis["by_chapter"].append({
            "chapter": chapter_id,
            "title": chapter_title,
            "distribution": chapter_blooms,
            "total_objectives": len(objectives),
        })

    # Calculate percentages
    if total_objectives > 0:
        blooms_percentages = {
            level: round((count / total_objectives) * 100, 1)
            for level, count in blooms_analysis["overall_distribution"].items()
        }
        blooms_analysis["percentages"] = blooms_percentages

        # Recommendations based on distribution
        lower_levels = blooms_percentages.get("Remember", 0) + blooms_percentages.get("Understand", 0)
        higher_levels = blooms_percentages.get("Analyze", 0) + blooms_percentages.get("Evaluate", 0) + blooms_percentages.get("Create", 0)

        if lower_levels > 50:
            blooms_analysis["recommendations"].append(
                f"Lower Bloom's levels (Remember/Understand) comprise {lower_levels}% of objectives. "
                "Consider adding more higher-order thinking objectives (Analyze/Evaluate/Create)."
            )

        if higher_levels < 20:
            blooms_analysis["recommendations"].append(
                f"Higher Bloom's levels comprise only {higher_levels}% of objectives. "
                "Consider adding more analytical and creative learning goals."
            )

    return blooms_analysis


def analyze_learning_pace(chapters: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze learning pace (pages per concept, exercises per chapter)."""
    pace_analysis = {
        "overall_metrics": {},
        "by_chapter": [],
        "recommendations": [],
    }

    total_pages = 0
    total_concepts = 0
    total_exercises = 0

    for chapter in chapters:
        chapter_id = chapter.get("id", "unknown")
        chapter_title = chapter.get("title", "Unknown")

        # Parse estimated pages (handle ranges like "20-25")
        pages_str = str(chapter.get("estimated_pages", "0"))
        if "-" in pages_str:
            page_parts = pages_str.split("-")
            pages = (int(page_parts[0]) + int(page_parts[1])) / 2
        else:
            try:
                pages = float(pages_str)
            except ValueError:
                pages = 0

        concept_count = len(chapter.get("key_concepts", []))

        # Calculate pages per concept
        pages_per_concept = pages / concept_count if concept_count > 0 else 0

        pace_analysis["by_chapter"].append({
            "chapter": chapter_id,
            "title": chapter_title,
            "pages": pages,
            "concepts": concept_count,
            "pages_per_concept": round(pages_per_concept, 1),
        })

        total_pages += pages
        total_concepts += concept_count

    # Overall metrics
    if total_concepts > 0:
        pace_analysis["overall_metrics"] = {
            "total_pages": round(total_pages, 0),
            "total_concepts": total_concepts,
            "average_pages_per_concept": round(total_pages / total_concepts, 1),
            "average_concepts_per_chapter": round(total_concepts / len(chapters), 1) if chapters else 0,
        }

    # Recommendations
    avg_pages_per_concept = pace_analysis["overall_metrics"].get("average_pages_per_concept", 0)

    if avg_pages_per_concept < 3:
        pace_analysis["recommendations"].append(
            f"Average of {avg_pages_per_concept} pages per concept is low. "
            "Ensure adequate explanation, examples, and practice for each concept."
        )
    elif avg_pages_per_concept > 10:
        pace_analysis["recommendations"].append(
            f"Average of {avg_pages_per_concept} pages per concept is high. "
            "Consider breaking down concepts into smaller sub-concepts."
        )

    return pace_analysis


def suggest_reordering(chapters: list[dict[str, Any]]) -> list[str]:
    """Suggest chapter reordering based on dependencies and difficulty."""
    suggestions = []

    # Check if chapters with no dependencies come first
    no_dep_chapters = [ch for ch in chapters if not ch.get("dependencies", {}).get("required", [])]
    first_chapter_has_deps = chapters[0].get("dependencies", {}).get("required", [])

    if first_chapter_has_deps:
        suggestions.append(
            f"First chapter '{chapters[0].get('title')}' has dependencies. "
            f"Consider starting with a chapter that has no prerequisites."
        )

    # Check for optional chapters appearing before core chapters
    for idx, chapter in enumerate(chapters):
        if chapter.get("purpose") == "Optional":
            # Check if there are core chapters after this
            core_after = any(
                ch.get("purpose") == "Core"
                for ch in chapters[idx + 1:]
            )
            if core_after:
                suggestions.append(
                    f"Optional chapter '{chapter.get('title')}' appears before core chapters. "
                    f"Consider moving optional content to later in the book."
                )

    return suggestions


def analyze_chapter_flow(filepath: str) -> dict[str, Any]:
    """
    Analyze complete chapter flow for cognitive progression.

    Returns:
        {
            "valid": bool,
            "concept_density": {...},
            "difficulty_progression": {...},
            "blooms_distribution": {...},
            "learning_pace": {...},
            "reordering_suggestions": [...]
        }
    """
    # Load data
    data = load_book_outline(filepath)

    if "error" in data:
        return {
            "valid": False,
            "error": data["error"],
        }

    # Extract chapters
    chapters = extract_chapter_sequence(data)

    if not chapters:
        return {
            "valid": False,
            "error": "No chapters found in book outline",
        }

    # Perform analyses
    concept_analysis = analyze_concept_density(chapters)
    difficulty_analysis = analyze_difficulty_progression(chapters)
    blooms_analysis = analyze_blooms_distribution(chapters)
    pace_analysis = analyze_learning_pace(chapters)
    reordering_suggestions = suggest_reordering(chapters)

    # Compile results
    results = {
        "valid": True,
        "total_chapters_analyzed": len(chapters),
        "concept_density": concept_analysis,
        "difficulty_progression": difficulty_analysis,
        "blooms_distribution": blooms_analysis,
        "learning_pace": pace_analysis,
        "reordering_suggestions": reordering_suggestions,
    }

    # Summary recommendations
    all_recommendations = []
    all_recommendations.extend(concept_analysis.get("warnings", []))
    all_recommendations.extend(difficulty_analysis.get("recommendations", []))
    all_recommendations.extend(blooms_analysis.get("recommendations", []))
    all_recommendations.extend(pace_analysis.get("recommendations", []))
    all_recommendations.extend(reordering_suggestions)

    results["summary_recommendations"] = all_recommendations
    results["recommendation_count"] = len(all_recommendations)

    return results


def main() -> None:
    """Parse arguments and analyze chapter flow."""
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "valid": False,
                    "error": "Usage: python analyze-flow.py <book-outline.yml>",
                }
            )
        )
        sys.exit(1)

    outline_file = sys.argv[1]

    # Check file exists
    if not Path(outline_file).exists():
        print(json.dumps({"valid": False, "error": f"File not found: {outline_file}"}))
        sys.exit(1)

    # Analyze
    results = analyze_chapter_flow(outline_file)
    print(json.dumps(results, indent=2))

    # Exit with success (this is analysis, not validation)
    sys.exit(0)


if __name__ == "__main__":
    main()
