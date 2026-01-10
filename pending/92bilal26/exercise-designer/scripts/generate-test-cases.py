#!/usr/bin/env python3
"""
Generate test cases for programming exercises.

Usage: python generate-test-cases.py <exercise.yml>

Returns: Exit code 0 on success, 1 on failure
Outputs: JSON with suggested test cases
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


def generate_test_cases(exercise: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive test cases for an exercise.

    Args:
        exercise: Exercise specification

    Returns:
        Dictionary with generated test cases and coverage analysis
    """
    result = {
        "success": True,
        "test_cases": [],
        "coverage": {
            "normal_cases": 0,
            "edge_cases": 0,
            "error_cases": 0
        },
        "recommendations": []
    }

    primary_concept = exercise.get("primary_concept", "").lower()
    difficulty = exercise.get("difficulty", "medium")

    # Analyze existing test cases
    existing_tests = exercise.get("test_cases", [])
    if existing_tests:
        result["test_cases"] = existing_tests
        result["coverage"] = analyze_coverage(existing_tests)

    # Generate missing test case types
    recommendations = []

    if result["coverage"]["normal_cases"] == 0:
        recommendations.append(
            "Add normal/typical test cases showing standard usage"
        )

    if result["coverage"]["edge_cases"] < 2:
        recommendations.append(
            "Add edge cases: empty inputs, boundary values, special characters"
        )

    if result["coverage"]["error_cases"] == 0 and difficulty != "easy":
        recommendations.append(
            "Add error test cases: invalid types, None values, out-of-range"
        )

    # Concept-specific recommendations
    if "list" in primary_concept or "array" in primary_concept:
        recommendations.extend([
            "Test with empty list: []",
            "Test with single element: [1]",
            "Test with duplicates: [1, 1, 1]",
            "Test with negative numbers if applicable"
        ])

    if "string" in primary_concept:
        recommendations.extend([
            "Test with empty string: ''",
            "Test with spaces: ' '",
            "Test with special characters: '!@#$'",
            "Test with unicode if applicable"
        ])

    if "function" in primary_concept or "parameter" in primary_concept:
        recommendations.extend([
            "Test with required parameters only",
            "Test with optional parameters",
            "Test with default values"
        ])

    if "loop" in primary_concept or "iteration" in primary_concept:
        recommendations.extend([
            "Test with zero iterations",
            "Test with one iteration",
            "Test with many iterations (100+)"
        ])

    result["recommendations"] = recommendations

    # Generate sample test cases if none provided
    if not existing_tests:
        result["test_cases"] = generate_sample_tests(exercise)

    return result


def analyze_coverage(test_cases: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Analyze test case coverage.

    Args:
        test_cases: List of test case dictionaries

    Returns:
        Dictionary with coverage counts
    """
    coverage = {
        "normal_cases": 0,
        "edge_cases": 0,
        "error_cases": 0
    }

    edge_indicators = ["empty", "zero", "none", "null", "boundary", "max", "min"]
    error_indicators = ["error", "invalid", "exception", "raise", "fail"]

    for test in test_cases:
        description = test.get("description", "").lower()

        is_edge = any(indicator in description for indicator in edge_indicators)
        is_error = any(indicator in description for indicator in error_indicators)

        if is_error:
            coverage["error_cases"] += 1
        elif is_edge:
            coverage["edge_cases"] += 1
        else:
            coverage["normal_cases"] += 1

    return coverage


def generate_sample_tests(exercise: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate sample test cases based on exercise type.

    Args:
        exercise: Exercise specification

    Returns:
        List of sample test cases
    """
    exercise_type = exercise.get("type", "")

    # Generic template tests
    return [
        {
            "input": "Sample input",
            "expected_output": "Expected output",
            "description": "Normal case - typical usage"
        },
        {
            "input": "Edge case input",
            "expected_output": "Edge case output",
            "description": "Edge case - empty/boundary value"
        },
        {
            "input": "Error case input",
            "expected_output": "Exception or error message",
            "description": "Error case - invalid input"
        }
    ]


def main():
    """Main entry point for test case generation."""
    if len(sys.argv) != 2:
        print("Usage: python generate-test-cases.py <exercise.yml>", file=sys.stderr)
        sys.exit(1)

    exercise_file = Path(sys.argv[1])

    if not exercise_file.exists():
        print(f"Error: File not found: {exercise_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(exercise_file, 'r') as f:
            exercise = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = generate_test_cases(exercise)
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
