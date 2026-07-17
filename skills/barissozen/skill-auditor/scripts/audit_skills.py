#!/usr/bin/env python3
"""
Audit skills for quality, completeness, and best practices.

Usage:
    python audit_skills.py <skills-directory> [--fix] [--json]

Example:
    python audit_skills.py .claude/skills/
    python audit_skills.py .claude/skills/ --json
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AuditResult:
    """Result of auditing a single skill."""
    skill_name: str
    skill_path: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)
    score: int = 10
    word_count: int = 0
    todo_count: int = 0
    has_frontmatter: bool = False
    has_name: bool = False
    has_description: bool = False
    description_length: int = 0
    has_when_to_use: bool = False
    has_workflow: bool = False
    decomposition_recommended: bool = False
    decomposition_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "skill_path": self.skill_path,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "score": self.score,
            "word_count": self.word_count,
            "todo_count": self.todo_count,
            "validation": {
                "frontmatter": self.has_frontmatter,
                "name": self.has_name,
                "description": self.has_description,
                "description_length": self.description_length,
                "when_to_use": self.has_when_to_use,
                "workflow": self.has_workflow,
            },
            "decomposition": {
                "recommended": self.decomposition_recommended,
                "reasons": self.decomposition_reasons,
            }
        }


class SkillAuditor:
    """Audits skill definitions for quality and best practices."""

    # Score deductions
    DEDUCTIONS = {
        "missing_skill_md": 10,
        "missing_frontmatter": 3,
        "missing_name": 2,
        "missing_description": 2,
        "short_description": 1,
        "todo_in_description": 2,
        "todo_placeholder": 0.5,
        "missing_when_to_use": 1,
        "missing_workflow": 1,
        "excessive_word_count": 1,
        "empty_directory": 0.5,
        "non_executable_script": 0.5,
    }

    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.results: list[AuditResult] = []

    def audit_all(self) -> list[AuditResult]:
        """Audit all skills in the directory."""
        self.results = []

        if not self.skills_dir.exists():
            print(f"Error: Skills directory not found: {self.skills_dir}")
            sys.exit(1)

        # Find all skill directories (those containing SKILL.md)
        skill_dirs = []
        for item in self.skills_dir.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                skill_dirs.append(item)

        if not skill_dirs:
            print(f"No skills found in {self.skills_dir}")
            return []

        for skill_dir in sorted(skill_dirs):
            result = self.audit_skill(skill_dir)
            self.results.append(result)

        return self.results

    def audit_skill(self, skill_path: Path) -> AuditResult:
        """Audit a single skill."""
        result = AuditResult(
            skill_name=skill_path.name,
            skill_path=str(skill_path)
        )

        skill_md = skill_path / "SKILL.md"

        if not skill_md.exists():
            result.errors.append("Missing required file: SKILL.md")
            result.score -= self.DEDUCTIONS["missing_skill_md"]
            return result

        content = skill_md.read_text()

        # Validate frontmatter
        self._validate_frontmatter(content, result)

        # Validate content structure
        self._validate_content(content, result)

        # Count words and TODOs
        self._analyze_content(content, result)

        # Validate resources
        self._validate_resources(skill_path, result)

        # Analyze decomposition need
        self._analyze_decomposition(content, skill_path, result)

        # Ensure score doesn't go below 0
        result.score = max(0, result.score)

        return result

    def _validate_frontmatter(self, content: str, result: AuditResult):
        """Validate YAML frontmatter."""
        if not content.startswith("---"):
            result.errors.append("SKILL.md must start with YAML frontmatter (---)")
            result.score -= self.DEDUCTIONS["missing_frontmatter"]
            return

        parts = content.split("---", 2)
        if len(parts) < 3:
            result.errors.append("Invalid YAML frontmatter format")
            result.score -= self.DEDUCTIONS["missing_frontmatter"]
            return

        result.has_frontmatter = True
        frontmatter = parts[1].strip()

        # Check name field
        if "name:" not in frontmatter:
            result.errors.append("Missing required 'name' field in frontmatter")
            result.score -= self.DEDUCTIONS["missing_name"]
        else:
            result.has_name = True

        # Check description field
        if "description:" not in frontmatter:
            result.errors.append("Missing required 'description' field in frontmatter")
            result.score -= self.DEDUCTIONS["missing_description"]
        else:
            result.has_description = True
            # Extract and validate description
            desc_match = re.search(r'description:\s*(.+?)(?:\n[a-z]|$)', frontmatter, re.DOTALL)
            if desc_match:
                description = desc_match.group(1).strip()
                result.description_length = len(description)

                if len(description) < 50:
                    result.warnings.append(f"Description is short ({len(description)} chars, recommended: 50+)")
                    result.score -= self.DEDUCTIONS["short_description"]

                if "TODO" in description:
                    result.errors.append("Description contains TODO placeholder")
                    result.score -= self.DEDUCTIONS["todo_in_description"]

    def _validate_content(self, content: str, result: AuditResult):
        """Validate content structure."""
        # Check for "When to Use" section
        if re.search(r'##\s*When to Use', content, re.IGNORECASE):
            result.has_when_to_use = True
        else:
            result.warnings.append("Missing 'When to Use' section")
            result.score -= self.DEDUCTIONS["missing_when_to_use"]

        # Check for Workflow section
        if re.search(r'##\s*Workflow', content, re.IGNORECASE):
            result.has_workflow = True
        else:
            result.warnings.append("Missing 'Workflow' section")
            result.score -= self.DEDUCTIONS["missing_workflow"]

    def _analyze_content(self, content: str, result: AuditResult):
        """Analyze content metrics."""
        # Word count
        result.word_count = len(content.split())
        if result.word_count > 5000:
            result.warnings.append(f"Word count ({result.word_count}) exceeds recommended limit (5000)")
            result.score -= self.DEDUCTIONS["excessive_word_count"]
        elif result.word_count > 3000:
            result.info.append(f"Word count ({result.word_count}) is high, consider moving content to references/")

        # TODO count
        result.todo_count = content.count("TODO")
        if result.todo_count > 0:
            result.warnings.append(f"Found {result.todo_count} TODO placeholder(s)")
            result.score -= self.DEDUCTIONS["todo_placeholder"] * result.todo_count

    def _validate_resources(self, skill_path: Path, result: AuditResult):
        """Validate bundled resources."""
        # Check for empty directories
        for subdir in ["scripts", "references", "assets"]:
            dir_path = skill_path / subdir
            if dir_path.exists():
                files = [f for f in dir_path.glob("*") if f.name != "README.md"]
                if len(files) == 0:
                    result.warnings.append(f"Empty {subdir}/ directory - consider removing")
                    result.score -= self.DEDUCTIONS["empty_directory"]

        # Check script executability
        scripts_dir = skill_path / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.glob("*.py"):
                if not os.access(script, os.X_OK):
                    result.warnings.append(f"Script {script.name} is not executable")
                    result.score -= self.DEDUCTIONS["non_executable_script"]

    def _analyze_decomposition(self, content: str, skill_path: Path, result: AuditResult):
        """Analyze if skill should be decomposed into sub-skills."""
        reasons = []

        # Check word count
        if result.word_count > 5000:
            reasons.append(f"High word count ({result.word_count} words)")

        # Count distinct concerns (h2 sections)
        h2_sections = re.findall(r'^##\s+(?!When to Use|Workflow|Bundled)(.+)$', content, re.MULTILINE)
        if len(h2_sections) > 5:
            reasons.append(f"Many distinct sections ({len(h2_sections)} h2 headings)")

        # Check for multiple distinct workflows
        workflow_steps = re.findall(r'###\s+Step\s+\d+', content)
        if len(workflow_steps) > 8:
            reasons.append(f"Complex workflow ({len(workflow_steps)} steps)")

        # Check references directory size
        refs_dir = skill_path / "references"
        if refs_dir.exists():
            ref_files = list(refs_dir.glob("*.md"))
            if len(ref_files) > 5:
                reasons.append(f"Many reference files ({len(ref_files)})")

        # Check for distinct tool/format handlers
        distinct_handlers = re.findall(r'(?:handle|process|convert|parse)\s+(\w+)', content, re.IGNORECASE)
        unique_handlers = set(distinct_handlers)
        if len(unique_handlers) > 4:
            reasons.append(f"Multiple distinct handlers ({len(unique_handlers)})")

        if reasons:
            result.decomposition_recommended = True
            result.decomposition_reasons = reasons
            result.info.append("Consider splitting into sub-skills")

    def print_report(self):
        """Print formatted audit report."""
        total_score = 0
        total_skills = len(self.results)

        print("\n" + "=" * 60)
        print("SKILL AUDIT REPORT")
        print("=" * 60)

        for result in self.results:
            print(f"\n## Skill: {result.skill_name}")
            print("-" * 40)

            # Validation results
            print("\n### Validation Results")
            print(f"- Frontmatter: {'PASS' if result.has_frontmatter else 'FAIL'}")
            print(f"- Name field: {'PASS' if result.has_name else 'FAIL'}")
            print(f"- Description: {'PASS' if result.has_description else 'FAIL'} ({result.description_length} chars)")
            print(f"- When to Use: {'PASS' if result.has_when_to_use else 'MISSING'}")
            print(f"- Workflow: {'PASS' if result.has_workflow else 'MISSING'}")
            print(f"- Word Count: {result.word_count} words {'(WARNING: >5000)' if result.word_count > 5000 else ''}")
            print(f"- TODO Placeholders: {result.todo_count}")

            # Errors
            if result.errors:
                print("\n### Errors")
                for error in result.errors:
                    print(f"  - {error}")

            # Warnings
            if result.warnings:
                print("\n### Warnings")
                for warning in result.warnings:
                    print(f"  - {warning}")

            # Decomposition
            print("\n### Decomposition Analysis")
            if result.decomposition_recommended:
                print(f"- Should split: YES")
                print(f"- Reasons:")
                for reason in result.decomposition_reasons:
                    print(f"    - {reason}")
            else:
                print("- Should split: NO")

            # Score
            print(f"\n### Quality Score: {result.score:.1f}/10")
            total_score += result.score

        # Summary
        avg_score = total_score / total_skills if total_skills > 0 else 0
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Skills audited: {total_skills}")
        print(f"Average score: {avg_score:.1f}/10")

        # Count by score range
        excellent = sum(1 for r in self.results if r.score >= 9)
        good = sum(1 for r in self.results if 7 <= r.score < 9)
        needs_work = sum(1 for r in self.results if r.score < 7)

        print(f"\nBreakdown:")
        print(f"  Excellent (9-10): {excellent}")
        print(f"  Good (7-8.9): {good}")
        print(f"  Needs work (<7): {needs_work}")

    def to_json(self) -> str:
        """Export results as JSON."""
        return json.dumps({
            "skills": [r.to_dict() for r in self.results],
            "summary": {
                "total": len(self.results),
                "average_score": sum(r.score for r in self.results) / len(self.results) if self.results else 0,
            }
        }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Audit skills for quality and best practices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s .claude/skills/
    %(prog)s .claude/skills/ --json
    %(prog)s .claude/skills/my-skill --single
        """
    )

    parser.add_argument(
        "skills_path",
        help="Path to skills directory or single skill"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    parser.add_argument(
        "--single",
        action="store_true",
        help="Audit a single skill instead of a directory"
    )

    args = parser.parse_args()

    skills_path = Path(args.skills_path).resolve()

    if args.single:
        # Audit single skill
        auditor = SkillAuditor(skills_path.parent)
        result = auditor.audit_skill(skills_path)
        auditor.results = [result]
    else:
        # Audit all skills
        auditor = SkillAuditor(skills_path)
        auditor.audit_all()

    if args.json:
        print(auditor.to_json())
    else:
        auditor.print_report()

    # Exit with error code if any skill has critical errors
    has_critical = any(r.score < 5 for r in auditor.results)
    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    main()
