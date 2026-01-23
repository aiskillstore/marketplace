#!/usr/bin/env python3
"""
EPIC Workflow Phase Validation Script

Validates that subagents have completed their work by checking for required
report files in the session directory after each phase.

Usage:
    python validate-phase.py <phase> <session-dir>

Phases:
    explore   - Checks for codebase-status.md
    research  - Checks for research-report.md
    plan      - Checks for implementation-plan.md
    validate  - Checks for validation-feedback.md
    implement - Checks for implementation completion
    review    - Checks for quality-report.md
    iterate   - Checks for final verification

Example:
    python validate-phase.py explore .claude/sessions/01-user-auth-feature
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple

# Phase requirements mapping
PHASE_REQUIREMENTS: Dict[str, Dict[str, any]] = {
    "explore": {
        "name": "Exploration",
        "required_files": ["codebase-status.md"],
        "optional_files": ["dependencies.md", "recent-changes.md"],
        "description": "Codebase exploration completed by codebase-explorer agent"
    },
    "research": {
        "name": "Research",
        "required_files": ["research-report.md"],
        "optional_files": ["best-practices.md", "technical-refs.md"],
        "description": "Research completed by research-specialist agent"
    },
    "plan": {
        "name": "Planning",
        "required_files": ["implementation-plan.md"],
        "optional_files": ["architecture-decisions.md", "trade-offs.md"],
        "description": "Strategic plan created by strategic-planner agent"
    },
    "validate": {
        "name": "Plan Validation",
        "required_files": ["validation-feedback.md"],
        "optional_files": ["risk-analysis.md", "alternatives.md"],
        "description": "Plan validation completed by consulting-expert agent"
    },
    "implement": {
        "name": "Implementation",
        "required_files": ["implementation-complete.md"],
        "optional_files": ["code-changes.md", "decisions.md"],
        "description": "Implementation completed by main agent"
    },
    "review": {
        "name": "Review",
        "required_files": ["quality-report.md"],
        "optional_files": ["test-results.md", "security-review.md"],
        "description": "Code review and testing completed"
    },
    "iterate": {
        "name": "Iteration",
        "required_files": ["final-verification.md"],
        "optional_files": ["fixes-applied.md", "re-review.md"],
        "description": "Iteration and final verification completed"
    }
}


def validate_session_dir(session_dir: str) -> Tuple[bool, str]:
    """Validate that the session directory exists and follows naming convention."""
    path = Path(session_dir)
    
    if not path.exists():
        return False, f"Session directory does not exist: {session_dir}"
    
    if not path.is_dir():
        return False, f"Path is not a directory: {session_dir}"
    
    # Check naming convention [NN]-[session-description]
    dir_name = path.name
    if not dir_name[0:2].isdigit() or not dir_name[2] == '-':
        return False, f"Session directory name should follow format [NN]-[session-description]: {dir_name}"
    
    return True, "Session directory validated"


def check_file_exists(session_dir: Path, filename: str) -> bool:
    """Check if a required file exists in the session directory."""
    file_path = session_dir / filename
    return file_path.exists() and file_path.is_file()


def validate_phase(phase: str, session_dir: str) -> Tuple[bool, List[str], List[str]]:
    """
    Validate that a phase has been completed.
    
    Returns:
        Tuple of (success, messages, warnings)
    """
    messages = []
    warnings = []
    
    # Validate phase name
    if phase not in PHASE_REQUIREMENTS:
        return False, [f"Invalid phase: {phase}. Valid phases: {', '.join(PHASE_REQUIREMENTS.keys())}"], []
    
    # Validate session directory
    dir_valid, dir_msg = validate_session_dir(session_dir)
    if not dir_valid:
        return False, [dir_msg], []
    
    messages.append(f"✓ {dir_msg}")
    
    session_path = Path(session_dir)
    phase_config = PHASE_REQUIREMENTS[phase]
    
    messages.append(f"\nValidating Phase: {phase_config['name']}")
    messages.append(f"Description: {phase_config['description']}")
    messages.append(f"Session Directory: {session_dir}\n")
    
    # Check required files
    missing_required = []
    found_required = []
    
    for required_file in phase_config["required_files"]:
        if check_file_exists(session_path, required_file):
            found_required.append(required_file)
            messages.append(f"✓ Required file found: {required_file}")
        else:
            missing_required.append(required_file)
            messages.append(f"✗ Required file missing: {required_file}")
    
    # Check optional files
    found_optional = []
    for optional_file in phase_config.get("optional_files", []):
        if check_file_exists(session_path, optional_file):
            found_optional.append(optional_file)
            warnings.append(f"ℹ Optional file found: {optional_file}")
    
    # Determine success
    success = len(missing_required) == 0
    
    if success:
        messages.append(f"\n✅ Phase '{phase_config['name']}' validation PASSED")
        messages.append(f"   Required files: {len(found_required)}/{len(phase_config['required_files'])}")
        if found_optional:
            messages.append(f"   Optional files: {len(found_optional)}")
    else:
        messages.append(f"\n❌ Phase '{phase_config['name']}' validation FAILED")
        messages.append(f"   Missing required files: {missing_required}")
        messages.append(f"\n⚠️  ACTION REQUIRED:")
        messages.append(f"   The main agent MUST reinvoke the responsible subagent to create missing reports.")
        messages.append(f"   This is an iterative compliance flow - continue retrying until validation passes.")
        messages.append(f"\n   Next Steps:")
        for missing_file in missing_required:
            messages.append(f"   1. Reinvoke the subagent to create: {missing_file}")
        messages.append(f"   2. Re-run this validation script")
        messages.append(f"   3. Repeat until validation passes")
        messages.append(f"\n   Do NOT proceed to the next phase until validation passes.")

    return success, messages, warnings


def main():
    """Main entry point for the validation script."""
    if len(sys.argv) != 3:
        print("Usage: python validate-phase.py <phase> <session-dir>")
        print("\nAvailable phases:")
        for phase, config in PHASE_REQUIREMENTS.items():
            print(f"  {phase:10} - {config['description']}")
        print("\nExample:")
        print("  python validate-phase.py explore .claude/sessions/01-user-auth-feature")
        sys.exit(1)
    
    phase = sys.argv[1].lower()
    session_dir = sys.argv[2]
    
    success, messages, warnings = validate_phase(phase, session_dir)
    
    # Print all messages
    for msg in messages:
        print(msg)
    
    # Print warnings
    if warnings:
        print("\nAdditional Information:")
        for warning in warnings:
            print(warning)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
