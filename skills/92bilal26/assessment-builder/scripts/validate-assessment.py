#!/usr/bin/env python3
"""
Validate assessment for objective coverage, cognitive distribution, and quality.

Usage: python validate-assessment.py <assessment.yml>

Returns: Exit code 0 on success, 1 on failure
Outputs: JSON with validation results
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


def validate_assessment(assessment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate assessment quality and balance.

    Args:
        assessment: Assessment specification

    Returns:
        Dictionary with validation results and recommendations
    """
    result = {
        "success": True,
        "validation_score": 100,
        "issues": [],
        "warnings": [],
        "recommendations": [],
        "cognitive_analysis": {},
        "question_analysis": []
    }

    questions = assessment.get("questions", [])
    if not questions:
        result["issues"].append({
            "severity": "critical",
            "message": "No questions found in assessment"
        })
        result["validation_score"] = 0
        result["success"] = False
        return result

    # Analyze cognitive distribution
    bloom_counts = {
        "remember": 0,
        "understand": 0,
        "apply": 0,
        "analyze": 0,
        "evaluate": 0,
        "create": 0
    }

    total_questions = len(questions)

    for q in questions:
        bloom_level = q.get("bloom_level", "").lower()
        if bloom_level in bloom_counts:
            bloom_counts[bloom_level] += 1

    # Calculate percentages
    bloom_percentages = {
        level: (count / total_questions * 100) if total_questions > 0 else 0
        for level, count in bloom_counts.items()
    }

    # Group by higher categories
    remember_understand = bloom_percentages["remember"] + bloom_percentages["understand"]
    apply = bloom_percentages["apply"]
    analyze_evaluate = bloom_percentages["analyze"] + bloom_percentages["evaluate"]
    create = bloom_percentages["create"]

    result["cognitive_analysis"] = {
        "remember_understand_pct": round(remember_understand, 1),
        "apply_pct": round(apply, 1),
        "analyze_evaluate_pct": round(analyze_evaluate, 1),
        "create_pct": round(create, 1),
        "total_questions": total_questions
    }

    # Check cognitive balance (target: 60%+ non-recall)
    non_recall = apply + analyze_evaluate + create
    if non_recall < 60:
        result["issues"].append({
            "severity": "moderate",
            "message": f"Only {non_recall:.1f}% of questions test application or higher-order thinking (target: 60%+). Too much recall/recognition."
        })
        result["validation_score"] -= 20

    # Check for variety in question types
    question_types = {}
    for q in questions:
        q_type = q.get("type", "unknown")
        question_types[q_type] = question_types.get(q_type, 0) + 1

    if len(question_types) < 3:
        result["warnings"].append(
            f"Limited question type variety ({len(question_types)} types). Consider using more varied formats."
        )
        result["validation_score"] -= 10

    # Check MCQ distractor quality
    mcq_without_analysis = 0
    for q in questions:
        if q.get("type") == "mcq":
            if not q.get("distractor_analysis"):
                mcq_without_analysis += 1

    if mcq_without_analysis > 0:
        result["warnings"].append(
            f"{mcq_without_analysis} MCQ(s) lack distractor analysis. Distractors should be based on common misconceptions."
        )
        result["validation_score"] -= 5

    # Check for rubrics on open-ended questions
    open_ended_types = ["code-writing", "explanation", "code-review", "comparison", "project"]
    missing_rubrics = 0

    for q in questions:
        if q.get("type") in open_ended_types:
            if not q.get("rubric") and not assessment.get("grading_guidelines"):
                missing_rubrics += 1

    if missing_rubrics > 0:
        result["issues"].append({
            "severity": "moderate",
            "message": f"{missing_rubrics} open-ended question(s) lack rubrics or grading guidelines"
        })
        result["validation_score"] -= 15

    # Check objective alignment
    objectives = assessment.get("learning_objectives_covered", [])
    if not objectives:
        result["warnings"].append(
            "No learning objectives specified. Questions should align with learning objectives."
        )
        result["validation_score"] -= 5

    # Recommendations based on analysis
    if remember_understand > 40:
        result["recommendations"].append(
            f"Reduce recall/recognition questions ({remember_understand:.0f}%). Add more application and analysis questions."
        )

    if apply < 30:
        result["recommendations"].append(
            f"Increase application questions ({apply:.0f}% currently). These test core skill demonstration."
        )

    if analyze_evaluate < 20:
        result["recommendations"].append(
            "Add more analysis questions (debugging, comparison, code review) to test higher-order thinking."
        )

    # Question-specific analysis
    for i, q in enumerate(questions, 1):
        q_analysis = {
            "question_id": q.get("question_id", f"Q{i}"),
            "type": q.get("type", "unknown"),
            "bloom_level": q.get("bloom_level", "unknown"),
            "issues": []
        }

        # Check for solution/answer
        if not q.get("solution") and not q.get("correct_answer"):
            q_analysis["issues"].append("Missing solution or correct answer")

        # Check MCQ has exactly one correct answer
        if q.get("type") == "mcq":
            options = q.get("options", [])
            correct_count = sum(1 for opt in options if opt.get("correct"))
            if correct_count != 1:
                q_analysis["issues"].append(f"MCQ should have exactly 1 correct answer (found {correct_count})")

        if q_analysis["issues"]:
            result["question_analysis"].append(q_analysis)

    # Overall success determination
    if result["validation_score"] < 60:
        result["success"] = False

    return result


def main():
    """Main entry point for assessment validation."""
    if len(sys.argv) != 2:
        print("Usage: python validate-assessment.py <assessment.yml>", file=sys.stderr)
        sys.exit(1)

    assessment_file = Path(sys.argv[1])

    if not assessment_file.exists():
        print(f"Error: File not found: {assessment_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(assessment_file, 'r') as f:
            assessment = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = validate_assessment(assessment)
        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(1)

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
