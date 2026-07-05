#!/usr/bin/env python3
"""
Prompt Quality Validator - Analyze prompt effectiveness for AI-assisted learning

This script validates prompts for:
1. Clarity and specificity
2. Appropriate context setting
3. Clear task specification
4. Testability and verifiability
5. Learning-focused framing

Usage:
    python validate-prompts.py prompts.yml
    # OR
    python validate-prompts.py prompts.txt

Output: JSON with validation results and improvement suggestions
"""

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def load_prompts(filepath: str) -> dict[str, Any]:
    """Load prompts from YAML or text file."""
    path = Path(filepath)

    if not path.exists():
        return {"error": f"File not found: {filepath}"}

    # Try YAML first
    if yaml and (path.suffix in [".yml", ".yaml"]):
        try:
            with open(filepath, "r") as f:
                data = yaml.safe_load(f)
                return data
        except Exception as e:
            return {"error": f"Failed to parse YAML: {str(e)}"}

    # Try text file (one prompt per line or separated by blank lines)
    try:
        with open(filepath, "r") as f:
            content = f.read()

        # Split by double newlines (blank lines)
        prompts = [p.strip() for p in content.split("\n\n") if p.strip()]

        return {"prompts": prompts}
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}


def extract_prompts(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract prompt list from loaded data."""
    if "prompts" in data and isinstance(data["prompts"], list):
        # Handle both string prompts and dict prompts
        prompts = []
        for idx, p in enumerate(data["prompts"]):
            if isinstance(p, str):
                prompts.append({"id": f"prompt-{idx + 1}", "text": p})
            elif isinstance(p, dict):
                prompts.append(
                    {
                        "id": p.get("id", f"prompt-{idx + 1}"),
                        "text": p.get("text", p.get("prompt", "")),
                        "context": p.get("context", ""),
                    }
                )
        return prompts

    # Try ai_prompt_templates structure
    if "ai_prompt_templates" in data:
        templates = data["ai_prompt_templates"]
        return [
            {
                "id": t.get("name", f"template-{idx + 1}"),
                "text": t.get("template", ""),
            }
            for idx, t in enumerate(templates)
        ]

    return []


def assess_clarity(prompt_text: str) -> dict[str, Any]:
    """Assess prompt clarity and specificity."""
    analysis = {
        "length": len(prompt_text),
        "word_count": len(prompt_text.split()),
        "has_question": "?" in prompt_text,
        "issues": [],
        "suggestions": [],
    }

    # Too short
    if analysis["word_count"] < 5:
        analysis["issues"].append("Prompt too brief - likely lacks specificity")
        analysis["suggestions"].append("Add more context and specific details (aim for 15-50 words)")

    # Too vague
    vague_patterns = [
        r"\bwrite code\b",
        r"\bfix this\b",
        r"\bhelp me\b",
        r"\bexplain this\b",
        r"\bmake\s+\w+\b",
    ]

    for pattern in vague_patterns:
        if re.search(pattern, prompt_text, re.IGNORECASE):
            analysis["issues"].append(f"Contains vague phrase: {pattern}")
            analysis["suggestions"].append("Be more specific about what you want")

    # Good specificity indicators
    specific_indicators = [
        "python",
        "function",
        "list",
        "dict",
        "error",
        "should",
        "expected",
        "actual",
        "using",
        "with",
    ]

    specificity_score = sum(1 for ind in specific_indicators if ind in prompt_text.lower())

    if specificity_score == 0:
        analysis["suggestions"].append(
            "Add specific technical terms (language, data structures, expected behavior)"
        )

    analysis["specificity_score"] = specificity_score

    return analysis


def assess_context(prompt_text: str) -> dict[str, Any]:
    """Check if prompt provides adequate context."""
    analysis = {
        "has_context_markers": False,
        "context_elements": [],
        "issues": [],
        "suggestions": [],
    }

    # Context markers
    context_markers = [
        (r"i'?m\s+(learning|working on|building)", "learning context"),
        (r"(beginner|intermediate|advanced)", "skill level"),
        (r"python\s+[\d.]+", "version specification"),
        (r"using\s+\w+", "tool/library mention"),
        (r"should\s+\w+", "expected behavior"),
        (r"(currently|so far|already)", "progress indication"),
    ]

    for pattern, element_type in context_markers:
        if re.search(pattern, prompt_text, re.IGNORECASE):
            analysis["context_elements"].append(element_type)
            analysis["has_context_markers"] = True

    # Check for minimal context
    if not analysis["has_context_markers"]:
        analysis["issues"].append("No context provided")
        analysis["suggestions"].append(
            "Add context: what you're working on, your skill level, environment, what you've tried"
        )

    # Good prompts explain "why" not just "what"
    if "because" not in prompt_text.lower() and "since" not in prompt_text.lower():
        analysis["suggestions"].append(
            "Consider adding rationale: why you need this, what problem you're solving"
        )

    return analysis


def assess_task_clarity(prompt_text: str) -> dict[str, Any]:
    """Check if the requested task is clear."""
    analysis = {
        "has_task_verb": False,
        "task_type": "Unknown",
        "issues": [],
        "suggestions": [],
    }

    # Task verbs
    task_patterns = [
        (r"\b(write|create|generate|implement|build)\b", "Generation"),
        (r"\b(explain|describe|clarify|tell me|what is)\b", "Explanation"),
        (r"\b(debug|fix|find\s+bug|what'?s\s+wrong)\b", "Debugging"),
        (r"\b(review|check|improve|refactor)\b", "Review"),
        (r"\b(compare|difference|alternative|versus)\b", "Comparison"),
    ]

    for pattern, task_type in task_patterns:
        if re.search(pattern, prompt_text, re.IGNORECASE):
            analysis["has_task_verb"] = True
            analysis["task_type"] = task_type
            break

    if not analysis["has_task_verb"]:
        analysis["issues"].append("No clear task verb (write, explain, debug, review, etc.)")
        analysis["suggestions"].append(
            "Start with clear action verb: 'Write a function...', 'Explain how...', 'Debug this code...'"
        )

    return analysis


def assess_testability(prompt_text: str) -> dict[str, Any]:
    """Check if prompt includes testable criteria."""
    analysis = {
        "has_test_criteria": False,
        "criteria_elements": [],
        "issues": [],
        "suggestions": [],
    }

    # Test criteria markers
    criteria_patterns = [
        (r"(expected|should return|output|result)", "expected output"),
        (r"(example|test case|input.*output)", "examples"),
        (r"(handle|check for|validate|edge case)", "edge cases"),
        (r"(requirements?|must|needs? to)", "requirements"),
    ]

    for pattern, element_type in criteria_patterns:
        if re.search(pattern, prompt_text, re.IGNORECASE):
            analysis["criteria_elements"].append(element_type)
            analysis["has_test_criteria"] = True

    if not analysis["has_test_criteria"]:
        analysis["issues"].append("No testable criteria specified")
        analysis["suggestions"].append(
            "Add expected behavior, example inputs/outputs, or test cases to verify correctness"
        )

    return analysis


def assess_constraints(prompt_text: str) -> dict[str, Any]:
    """Check if prompt specifies constraints and requirements."""
    analysis = {
        "has_constraints": False,
        "constraint_types": [],
        "issues": [],
        "suggestions": [],
    }

    # Constraint patterns
    constraint_patterns = [
        (r"(standard library|no external|without using)", "library constraints"),
        (r"(pep\s*8|style|format|convention)", "style requirements"),
        (r"(type hints?|docstring|comments?)", "documentation requirements"),
        (r"(error handling|exception|validate)", "error handling"),
        (r"(performance|efficient|optimize|o\()", "performance requirements"),
    ]

    for pattern, constraint_type in constraint_patterns:
        if re.search(pattern, prompt_text, re.IGNORECASE):
            analysis["constraint_types"].append(constraint_type)
            analysis["has_constraints"] = True

    if not analysis["has_constraints"]:
        analysis["suggestions"].append(
            "Consider adding constraints: library restrictions, style requirements, performance needs"
        )

    return analysis


def validate_prompt(prompt_data: dict[str, Any]) -> dict[str, Any]:
    """Validate a single prompt for quality."""
    prompt_id = prompt_data.get("id", "unknown")
    prompt_text = prompt_data.get("text", "")

    if not prompt_text:
        return {
            "id": prompt_id,
            "valid": False,
            "error": "Empty prompt text",
        }

    # Run all assessments
    clarity = assess_clarity(prompt_text)
    context = assess_context(prompt_text)
    task = assess_task_clarity(prompt_text)
    testability = assess_testability(prompt_text)
    constraints = assess_constraints(prompt_text)

    # Calculate quality score (0-100)
    score = 100

    # Deduct for issues
    score -= len(clarity["issues"]) * 10
    score -= len(context["issues"]) * 10
    score -= len(task["issues"]) * 15  # Task clarity is critical
    score -= len(testability["issues"]) * 10

    # Bonus for good elements
    score += clarity.get("specificity_score", 0) * 2
    score += len(context.get("context_elements", [])) * 3
    score += len(testability.get("criteria_elements", [])) * 3

    score = max(0, min(100, score))  # Clamp to 0-100

    # Overall assessment
    quality = (
        "Excellent"
        if score >= 85
        else "Good" if score >= 70 else "Needs Improvement" if score >= 50 else "Poor"
    )

    # Compile all suggestions
    all_suggestions = []
    all_suggestions.extend(clarity.get("suggestions", []))
    all_suggestions.extend(context.get("suggestions", []))
    all_suggestions.extend(task.get("suggestions", []))
    all_suggestions.extend(testability.get("suggestions", []))
    all_suggestions.extend(constraints.get("suggestions", []))

    return {
        "id": prompt_id,
        "valid": True,
        "quality_score": score,
        "quality_assessment": quality,
        "length": clarity["length"],
        "word_count": clarity["word_count"],
        "task_type": task["task_type"],
        "has_context": context["has_context_markers"],
        "has_test_criteria": testability["has_test_criteria"],
        "has_constraints": constraints["has_constraints"],
        "analysis": {
            "clarity": clarity,
            "context": context,
            "task": task,
            "testability": testability,
            "constraints": constraints,
        },
        "suggestions": all_suggestions,
    }


def validate_prompts_file(filepath: str) -> dict[str, Any]:
    """Validate all prompts in a file."""
    # Load prompts
    data = load_prompts(filepath)

    if "error" in data:
        return {"valid": False, "error": data["error"]}

    # Extract prompts
    prompts = extract_prompts(data)

    if not prompts:
        return {
            "valid": False,
            "error": "No prompts found in file. Ensure proper YAML structure or text format.",
        }

    # Validate each prompt
    results = []
    total_score = 0

    for prompt in prompts:
        result = validate_prompt(prompt)
        results.append(result)
        total_score += result.get("quality_score", 0)

    avg_score = total_score / len(results) if results else 0

    # Summary
    excellent_count = sum(1 for r in results if r.get("quality_score", 0) >= 85)
    good_count = sum(1 for r in results if 70 <= r.get("quality_score", 0) < 85)
    needs_improvement_count = sum(1 for r in results if 50 <= r.get("quality_score", 0) < 70)
    poor_count = sum(1 for r in results if r.get("quality_score", 0) < 50)

    return {
        "valid": True,
        "total_prompts": len(results),
        "average_quality_score": round(avg_score, 1),
        "summary": {
            "excellent": excellent_count,
            "good": good_count,
            "needs_improvement": needs_improvement_count,
            "poor": poor_count,
        },
        "prompts": results,
    }


def main() -> None:
    """Parse arguments and validate prompts."""
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "valid": False,
                    "error": "Usage: python validate-prompts.py <prompts.yml|prompts.txt>",
                }
            )
        )
        sys.exit(1)

    prompts_file = sys.argv[1]

    # Check file exists
    if not Path(prompts_file).exists():
        print(json.dumps({"valid": False, "error": f"File not found: {prompts_file}"}))
        sys.exit(1)

    # Validate
    results = validate_prompts_file(prompts_file)
    print(json.dumps(results, indent=2))

    # Exit with success (this is analysis, not strict validation)
    sys.exit(0)


if __name__ == "__main__":
    main()
