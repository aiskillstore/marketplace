#!/usr/bin/env python3
"""
AI Integration Assessment - Evaluate balance of AI assistance vs foundational learning

This script assesses whether AI integration in a lesson:
1. Maintains appropriate balance (foundation/AI-assisted/verification)
2. Ensures foundational skills built independently
3. Includes verification of learning without AI
4. Prevents over-reliance on AI tools
5. Aligns AI use with learning objectives

Usage:
    python assess-ai-integration.py lesson-plan.yml

Output: JSON with assessment results and recommendations
"""

import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def load_lesson_plan(filepath: str) -> dict[str, Any]:
    """Load and parse lesson plan YAML file."""
    if yaml is None:
        return {"error": "PyYAML not installed. Install with: pip install pyyaml"}

    try:
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
        return data
    except Exception as e:
        return {"error": f"Failed to parse YAML: {str(e)}"}


def assess_balance(data: dict[str, Any]) -> dict[str, Any]:
    """
    Assess balance between foundational, AI-assisted, and verification work.

    Target ratio: 40% foundational (no AI), 40% AI-assisted, 20% verification (no AI)
    """
    balance = data.get("ai_assistance_balance", {})

    foundational = balance.get("foundational_work_percentage", 0)
    ai_assisted = balance.get("ai_assisted_work_percentage", 0)
    verification = balance.get("independent_verification_percentage", 0)

    total = foundational + ai_assisted + verification

    analysis = {
        "actual_balance": {
            "foundational": foundational,
            "ai_assisted": ai_assisted,
            "verification": verification,
            "total": total,
        },
        "target_balance": {"foundational": 40, "ai_assisted": 40, "verification": 20},
        "balanced": False,
        "issues": [],
        "recommendations": [],
    }

    # Check if total adds to 100
    if total != 100:
        analysis["issues"].append(f"Percentages don't add to 100 (total: {total})")

    # Check foundational work
    if foundational < 30:
        analysis["issues"].append(
            f"Too little foundational work ({foundational}%). Students may not build core skills independently."
        )
        analysis["recommendations"].append(
            "Increase independent foundational work to at least 30-40%. Core concepts should be learned without AI first."
        )
    elif foundational > 60:
        analysis["issues"].append(
            f"Too much foundational work ({foundational}%). AI could accelerate learning more."
        )
        analysis["recommendations"].append(
            "Consider allowing AI assistance for some practice after foundations are solid."
        )

    # Check AI-assisted work
    if ai_assisted < 20:
        analysis["issues"].append(
            f"Very limited AI assistance ({ai_assisted}%). Students may not learn to use AI effectively."
        )
        analysis["recommendations"].append(
            "Increase AI-assisted practice to 30-50% to help students learn effective AI collaboration."
        )
    elif ai_assisted > 60:
        analysis["issues"].append(
            f"Too much AI-assisted work ({ai_assisted}%). Risk of over-reliance on AI."
        )
        analysis["recommendations"].append(
            "Reduce AI assistance to 30-50%. Ensure students build independent problem-solving skills."
        )

    # Check verification work
    if verification < 15:
        analysis["issues"].append(
            f"Insufficient verification ({verification}%). No way to confirm learning without AI."
        )
        analysis["recommendations"].append(
            "Add independent verification activities (15-25%) to ensure learning transferred to capability."
        )
    elif verification > 30:
        analysis["issues"].append(
            f"Excessive verification ({verification}%). May be redundant."
        )

    # Overall balance check
    if (
        30 <= foundational <= 50
        and 30 <= ai_assisted <= 50
        and 15 <= verification <= 25
        and total == 100
    ):
        analysis["balanced"] = True
    else:
        analysis["balanced"] = False

    return analysis


def assess_foundational_skills(data: dict[str, Any]) -> dict[str, Any]:
    """Check if foundational skills are identified and protected from AI assistance."""
    foundational_skills = data.get("foundational_skills_focus", [])
    ai_assisted_skills = data.get("ai_assisted_skills_focus", [])

    analysis = {
        "foundational_skills_count": len(foundational_skills),
        "ai_assisted_skills_count": len(ai_assisted_skills),
        "foundational_skills": foundational_skills,
        "issues": [],
        "recommendations": [],
    }

    # Check if foundational skills are identified
    if len(foundational_skills) == 0:
        analysis["issues"].append("No foundational skills identified")
        analysis["recommendations"].append(
            "Identify 2-5 core skills that must be developed independently without AI assistance"
        )
    elif len(foundational_skills) < 2:
        analysis["issues"].append("Only one foundational skill identified - likely insufficient")
        analysis["recommendations"].append("Add more foundational skills (aim for 3-5)")

    # Check for separation between foundational and AI-assisted
    if foundational_skills and ai_assisted_skills:
        overlap = set(foundational_skills) & set(ai_assisted_skills)
        if overlap:
            analysis["issues"].append(
                f"Skills appear in both foundational and AI-assisted: {list(overlap)}"
            )
            analysis["recommendations"].append(
                "Ensure clear separation: foundational skills should not use AI assistance"
            )

    return analysis


def assess_verification_checkpoints(data: dict[str, Any]) -> dict[str, Any]:
    """Check if there are adequate verification points to test learning without AI."""
    phases = data.get("phases", [])

    verification_phases = [p for p in phases if p.get("ai_usage") == "None" and "verification" in p.get("phase_name", "").lower()]

    independent_phases = [p for p in phases if p.get("ai_usage") == "None"]

    analysis = {
        "verification_checkpoint_count": len(verification_phases),
        "ai_free_phase_count": len(independent_phases),
        "verification_checkpoints": [p.get("phase_name") for p in verification_phases],
        "issues": [],
        "recommendations": [],
    }

    # Check for verification checkpoints
    if len(verification_phases) == 0:
        analysis["issues"].append("No explicit verification checkpoints found")
        analysis["recommendations"].append(
            "Add verification phase where students demonstrate learning without AI assistance"
        )

    # Check for AI-free phases
    if len(independent_phases) < 2:
        analysis["issues"].append(
            f"Only {len(independent_phases)} AI-free phases - students need more independent practice"
        )
        analysis["recommendations"].append(
            "Include at least 2-3 phases without AI: initial foundation + final verification"
        )

    # Check if verification phase exists after AI-assisted phase
    ai_assisted_indices = [
        i for i, p in enumerate(phases) if p.get("ai_usage") in ["Encouraged", "Optional"]
    ]

    verification_indices = [i for i, p in enumerate(phases) if p.get("ai_usage") == "None" and i > 0]

    if ai_assisted_indices and verification_indices:
        has_post_ai_verification = any(v > max(ai_assisted_indices) for v in verification_indices)
        if not has_post_ai_verification:
            analysis["issues"].append("No verification checkpoint after AI-assisted work")
            analysis["recommendations"].append(
                "Add verification phase after AI-assisted work to confirm learning transferred"
            )

    return analysis


def assess_ethical_guidelines(data: dict[str, Any]) -> dict[str, Any]:
    """Check if ethical AI use guidelines are included."""
    ethical_focus = data.get("ethical_focus", [])
    ai_guidelines = data.get("ai_usage_guidelines", {})
    disclosure_reqs = data.get("ai_usage_guidelines", {}).get("disclosure_requirements", [])

    analysis = {
        "ethical_principles_count": len(ethical_focus),
        "has_usage_guidelines": bool(ai_guidelines),
        "has_disclosure_requirements": len(disclosure_reqs) > 0,
        "issues": [],
        "recommendations": [],
    }

    # Check ethical focus
    if len(ethical_focus) == 0:
        analysis["issues"].append("No ethical considerations identified")
        analysis["recommendations"].append(
            "Add ethical focus areas: honesty, understanding, verification, over-reliance prevention"
        )

    # Check usage guidelines
    if not ai_guidelines:
        analysis["issues"].append("No AI usage guidelines provided")
        analysis["recommendations"].append(
            "Add guidelines for when to use/not use AI, disclosure requirements"
        )

    # Check disclosure requirements
    if not disclosure_reqs:
        analysis["issues"].append("No disclosure requirements for AI usage")
        analysis["recommendations"].append(
            "Require students to document AI usage (when, why, what they learned)"
        )

    # Check for key ethical principles
    key_principles = ["honesty", "disclosure", "understanding", "verification", "reliance"]
    ethical_text = " ".join([str(p) for p in ethical_focus]).lower()

    missing_principles = [p for p in key_principles if p not in ethical_text]

    if missing_principles:
        analysis["recommendations"].append(
            f"Consider addressing these ethical principles: {', '.join(missing_principles)}"
        )

    return analysis


def assess_ai_integration(filepath: str) -> dict[str, Any]:
    """
    Comprehensive assessment of AI integration in lesson plan.

    Returns:
        {
            "valid": bool,
            "overall_score": int (0-100),
            "balance_assessment": {...},
            "foundational_skills_assessment": {...},
            "verification_assessment": {...},
            "ethical_assessment": {...},
            "summary_recommendations": [...]
        }
    """
    # Load data
    data = load_lesson_plan(filepath)

    if "error" in data:
        return {"valid": False, "error": data["error"]}

    # Perform assessments
    balance_assessment = assess_balance(data)
    foundational_assessment = assess_foundational_skills(data)
    verification_assessment = assess_verification_checkpoints(data)
    ethical_assessment = assess_ethical_guidelines(data)

    # Calculate overall score (0-100)
    score = 100

    # Deduct for issues
    score -= len(balance_assessment["issues"]) * 10
    score -= len(foundational_assessment["issues"]) * 10
    score -= len(verification_assessment["issues"]) * 10
    score -= len(ethical_assessment["issues"]) * 5

    # Major issues (balance problems)
    if not balance_assessment["balanced"]:
        score -= 15

    score = max(0, score)  # Floor at 0

    # Compile all recommendations
    all_recommendations = []
    all_recommendations.extend(balance_assessment["recommendations"])
    all_recommendations.extend(foundational_assessment["recommendations"])
    all_recommendations.extend(verification_assessment["recommendations"])
    all_recommendations.extend(ethical_assessment["recommendations"])

    # Overall assessment
    overall = "Excellent" if score >= 90 else "Good" if score >= 75 else "Needs Improvement" if score >= 60 else "Poor"

    results = {
        "valid": True,
        "overall_score": score,
        "overall_assessment": overall,
        "balance_assessment": balance_assessment,
        "foundational_skills_assessment": foundational_assessment,
        "verification_assessment": verification_assessment,
        "ethical_assessment": ethical_assessment,
        "summary_recommendations": all_recommendations,
        "recommendation_count": len(all_recommendations),
    }

    return results


def main() -> None:
    """Parse arguments and assess AI integration."""
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "valid": False,
                    "error": "Usage: python assess-ai-integration.py <lesson-plan.yml>",
                }
            )
        )
        sys.exit(1)

    lesson_file = sys.argv[1]

    # Check file exists
    if not Path(lesson_file).exists():
        print(json.dumps({"valid": False, "error": f"File not found: {lesson_file}"}))
        sys.exit(1)

    # Assess
    results = assess_ai_integration(lesson_file)
    print(json.dumps(results, indent=2))

    # Exit with success (this is assessment, not validation)
    sys.exit(0)


if __name__ == "__main__":
    main()
