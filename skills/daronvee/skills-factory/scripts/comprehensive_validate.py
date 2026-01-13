#!/usr/bin/env python3
"""
Comprehensive validation script for Claude Code skills.

Validates:
- YAML structure and required fields
- Naming conventions (hyphen-case, character limits)
- Description quality (length, clarity, trigger terms)
- Progressive disclosure patterns (file references one-level deep)
- Best practices (no absolute paths, no TODO markers, etc.)
- Content quality (examples present, clear structure)
- Workflow validation (if workflows present)
- Script structure (if scripts present)

Exit codes:
  0 = All validations passed
  1 = Errors found (must fix before packaging)
  2 = Warnings only (should review but can package)
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Tuple

class SkillValidator:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.suggestions = []

    def validate_all(self) -> Tuple[bool, str]:
        """Run all validation checks."""
        # Core structure validation
        self.validate_directory_structure()
        self.validate_yaml_frontmatter()
        self.validate_naming_conventions()
        self.validate_description_quality()

        # Content validation
        self.validate_content_quality()
        self.validate_progressive_disclosure()
        self.validate_best_practices()

        # Resource validation
        self.validate_references()
        self.validate_scripts()

        # Workflow validation (if applicable)
        self.validate_workflows()

        # Generate report
        return self.generate_report()

    def validate_directory_structure(self):
        """Check that basic skill structure exists."""
        skill_md = self.skill_path / 'SKILL.md'

        if not self.skill_path.exists():
            self.errors.append(f"[ERROR] Skill directory not found: {self.skill_path}")
            return

        if not self.skill_path.is_dir():
            self.errors.append(f"[ERROR] Path is not a directory: {self.skill_path}")
            return

        if not skill_md.exists():
            self.errors.append("[ERROR] SKILL.md not found (required)")
            return

        # Check for optional but recommended directories
        references_dir = self.skill_path / 'references'
        scripts_dir = self.skill_path / 'scripts'
        assets_dir = self.skill_path / 'assets'

        if references_dir.exists() and not references_dir.is_dir():
            self.errors.append("[ERROR] references/ exists but is not a directory")

        if scripts_dir.exists() and not scripts_dir.is_dir():
            self.errors.append("[ERROR] scripts/ exists but is not a directory")

        if assets_dir.exists() and not assets_dir.is_dir():
            self.errors.append("[ERROR] assets/ exists but is not a directory")

    def validate_yaml_frontmatter(self):
        """Validate YAML frontmatter structure and required fields."""
        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            return  # Already reported in directory validation

        try:
            content = skill_md.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append(f"[ERROR] Cannot read SKILL.md: {e}")
            return

        # Check frontmatter exists
        if not content.startswith('---'):
            self.errors.append("[ERROR] SKILL.md must start with YAML frontmatter (---)")
            return

        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            self.errors.append("[ERROR] Invalid YAML frontmatter format (must be enclosed in ---)")
            return

        frontmatter = match.group(1)

        # Check for tabs (YAML doesn't allow tabs)
        if '\t' in frontmatter:
            self.errors.append("[ERROR] YAML frontmatter contains tabs - use spaces only")

        # Check required fields
        if 'name:' not in frontmatter:
            self.errors.append("[ERROR] Missing required field: 'name' in YAML frontmatter")

        if 'description:' not in frontmatter:
            self.errors.append("[ERROR] Missing required field: 'description' in YAML frontmatter")

        # Extract name
        name_match = re.search(r'name:\s*(.+)', frontmatter)
        if name_match:
            self.yaml_name = name_match.group(1).strip().strip('"').strip("'")
        else:
            self.yaml_name = None

        # Extract description (handle multiline with |)
        desc_match = re.search(r'description:\s*\|?\s*(.+?)(?=\n\w+:|$)', frontmatter, re.DOTALL)
        if desc_match:
            self.yaml_description = desc_match.group(1).strip()
        else:
            self.yaml_description = None

        # Check for TODO markers in frontmatter
        if 'TODO' in frontmatter:
            self.errors.append("[ERROR] Found TODO markers in YAML frontmatter - replace with actual content")

        # Validate allowed-tools (optional field)
        if 'allowed-tools:' in frontmatter:
            # Extract allowed-tools value
            tools_match = re.search(r'allowed-tools:\s*\[(.*?)\]', frontmatter, re.DOTALL)
            if tools_match:
                tools_str = tools_match.group(1).strip()
                # Parse tool names (handle quotes, spaces, commas)
                tools = [t.strip().strip('"').strip("'") for t in tools_str.split(',') if t.strip()]

                # Known Claude Code tools (as of 2025-11-22)
                valid_tools = ['Read', 'Write', 'Edit', 'Grep', 'Glob', 'Bash', 'Task', 'SlashCommand', 'Skill']

                for tool in tools:
                    if tool not in valid_tools:
                        self.warnings.append(
                            f"[WARNING] allowed-tools contains unknown tool '{tool}'. "
                            f"Verify spelling or check if this is a new Claude Code tool. "
                            f"Known tools: {', '.join(valid_tools)}"
                        )
            else:
                # Check if it's a multiline list format
                tools_multiline = re.search(r'allowed-tools:\s*\n((?:\s+-\s+\w+\n?)+)', frontmatter)
                if tools_multiline:
                    tools_lines = tools_multiline.group(1).strip().split('\n')
                    tools = [re.search(r'-\s+(\w+)', line).group(1) for line in tools_lines if re.search(r'-\s+(\w+)', line)]

                    valid_tools = ['Read', 'Write', 'Edit', 'Grep', 'Glob', 'Bash', 'Task', 'SlashCommand', 'Skill']

                    for tool in tools:
                        if tool not in valid_tools:
                            self.warnings.append(
                                f"[WARNING] allowed-tools contains unknown tool '{tool}'. "
                                f"Verify spelling or check if this is a new Claude Code tool. "
                                f"Known tools: {', '.join(valid_tools)}"
                            )
                else:
                    self.errors.append("[ERROR] allowed-tools format invalid - must be YAML list (e.g., [Read, Grep, Glob] or multiline)")

        # Validate metadata (optional field)
        if 'metadata:' in frontmatter:
            # Extract metadata block
            metadata_match = re.search(r'metadata:\s*\n((?:\s+\w+:\s*.+\n?)+)', frontmatter)
            if metadata_match:
                metadata_block = metadata_match.group(1)
                # Check each key-value pair is valid format
                metadata_lines = [line.strip() for line in metadata_block.split('\n') if line.strip()]
                for line in metadata_lines:
                    if not re.match(r'^\w+:\s*.+$', line):
                        self.errors.append(
                            f"[ERROR] metadata entry invalid format: '{line}' "
                            "(must be 'key: value')"
                        )
            else:
                # Check if it's inline dict format
                inline_match = re.search(r'metadata:\s*\{(.+?)\}', frontmatter)
                if not inline_match:
                    self.errors.append("[ERROR] metadata format invalid - must be YAML dictionary (key: value pairs)")

    def validate_naming_conventions(self):
        """Validate skill name follows conventions."""
        if not self.yaml_name:
            return  # Already reported in YAML validation

        # Check hyphen-case format (lowercase + hyphens only)
        if not re.match(r'^[a-z0-9-]+$', self.yaml_name):
            self.errors.append(
                f"[ERROR] Skill name '{self.yaml_name}' must be hyphen-case "
                "(lowercase letters, digits, and hyphens only)"
            )

        # Check doesn't start/end with hyphen
        if self.yaml_name.startswith('-') or self.yaml_name.endswith('-'):
            self.errors.append(f"[ERROR] Skill name '{self.yaml_name}' cannot start or end with hyphen")

        # Check no consecutive hyphens
        if '--' in self.yaml_name:
            self.errors.append(f"[ERROR] Skill name '{self.yaml_name}' cannot contain consecutive hyphens")

        # Check length (max 64 characters per spec)
        if len(self.yaml_name) > 64:
            self.errors.append(
                f"[ERROR] Skill name too long: {len(self.yaml_name)} characters (max 64)"
            )

        # Check name matches directory name
        dir_name = self.skill_path.name
        if self.yaml_name != dir_name:
            self.errors.append(
                f"[ERROR] Skill name '{self.yaml_name}' doesn't match directory name '{dir_name}'"
            )

    def validate_description_quality(self):
        """Validate description content and quality."""
        if not self.yaml_description:
            return  # Already reported in YAML validation

        # Check character limit (1024 per spec)
        desc_length = len(self.yaml_description)
        if desc_length > 1024:
            self.errors.append(
                f"[ERROR] Description too long: {desc_length} characters (max 1024)"
            )

        # Check for angle brackets (not allowed)
        if '<' in self.yaml_description or '>' in self.yaml_description:
            self.errors.append("[ERROR] Description cannot contain angle brackets (< or >)")

        # Check minimum length (too short = not descriptive enough)
        if desc_length < 50:
            self.warnings.append(
                f"[WARNING]  Description very short ({desc_length} chars) - consider adding more detail for better triggering"
            )

        # Check for trigger terms (action verbs, use cases)
        action_verbs = ['create', 'generate', 'validate', 'analyze', 'guide', 'help', 'build', 'test']
        has_action_verb = any(verb in self.yaml_description.lower() for verb in action_verbs)

        if not has_action_verb:
            self.suggestions.append(
                "[TIP] Consider adding action verbs to description (create, generate, validate, etc.) to improve triggering"
            )

        # Check for "use for:" pattern (good practice)
        if 'use for' not in self.yaml_description.lower():
            self.suggestions.append(
                "[TIP] Consider adding 'Use for: X, Y, Z' to description to clarify triggering scenarios"
            )

    def validate_content_quality(self):
        """Validate SKILL.md body content quality."""
        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        # Remove frontmatter for body analysis
        body_match = re.search(r'^---\n.*?\n---\n(.+)', content, re.DOTALL)
        if not body_match:
            self.warnings.append("[WARNING]  No content after YAML frontmatter")
            return

        body = body_match.group(1)
        lines = body.split('\n')
        line_count = len(lines)

        # Check length (progressive disclosure: keep under 500 lines, ideally under 200)
        if line_count > 500:
            self.warnings.append(
                f"[WARNING]  SKILL.md body is very long ({line_count} lines) - consider moving content to references/"
            )
        elif line_count > 200:
            self.suggestions.append(
                f"[TIP] SKILL.md body is {line_count} lines - consider progressive disclosure (move details to references/)"
            )

        # Check for TODO markers
        if 'TODO' in body:
            self.errors.append("[ERROR] Found TODO markers in SKILL.md body - replace with actual content")

        # Check for examples (good practice)
        has_code_blocks = '```' in body
        has_example_header = re.search(r'##?\s+Example', body, re.IGNORECASE)

        if not has_code_blocks and not has_example_header:
            self.suggestions.append(
                "[TIP] No code examples found - consider adding examples for clarity"
            )

        # Check for workflow structure (numbered steps or checklist)
        has_workflow = bool(
            re.search(r'###?\s+Step\s+\d+', body) or  # "### Step 1:"
            re.search(r'##?\s+Workflow', body, re.IGNORECASE) or
            '- [ ]' in body  # Checklist
        )

        if not has_workflow:
            self.suggestions.append(
                "[TIP] No workflow structure detected - consider adding numbered steps or checklist if applicable"
            )

    def validate_progressive_disclosure(self):
        """Validate progressive disclosure patterns."""
        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        # Find all file references: [text](path/to/file.md)
        file_refs = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

        for link_text, link_path in file_refs:
            # Skip external links (http/https)
            if link_path.startswith('http://') or link_path.startswith('https://'):
                continue

            # Check file reference depth (should be one level: references/file.md)
            path_parts = link_path.split('/')

            # Skip anchors (file.md#section)
            clean_path = link_path.split('#')[0]
            if not clean_path:
                continue

            # Count directory depth
            depth = len([p for p in path_parts[:-1] if p and p != '.'])

            if depth > 1:
                self.warnings.append(
                    f"[WARNING]  File reference too deep: '{link_path}' "
                    "(progressive disclosure recommends one level: references/file.md)"
                )

            # Check if referenced file exists
            ref_file = self.skill_path / clean_path
            if not ref_file.exists():
                self.errors.append(f"[ERROR] Referenced file not found: {clean_path}")

    def validate_best_practices(self):
        """Validate adherence to best practices."""
        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        # Check for absolute paths (bad practice - breaks portability)
        abs_path_patterns = [
            r'~/.claude/skills/',
            r'/Users/[^/]+/',
            r'C:\\',
            r'/home/[^/]+/',
        ]

        for pattern in abs_path_patterns:
            if re.search(pattern, content):
                self.warnings.append(
                    f"[WARNING]  Found absolute path pattern '{pattern}' - use relative paths for portability"
                )
                break

        # Check script references use proper format
        script_refs = re.findall(r'`bash scripts/([^`]+)`', content)
        for script_ref in script_refs:
            # Check if script exists
            script_path = self.skill_path / 'scripts' / script_ref
            if not script_path.exists():
                self.errors.append(f"[ERROR] Referenced script not found: scripts/{script_ref}")

    def validate_references(self):
        """Validate reference files if they exist."""
        references_dir = self.skill_path / 'references'
        if not references_dir.exists():
            return  # References are optional

        ref_files = list(references_dir.glob('*.md'))

        if not ref_files:
            self.warnings.append("[WARNING]  references/ directory exists but contains no .md files")
            return

        # Check each reference file
        for ref_file in ref_files:
            # Check file size (very large files may cause performance issues)
            size = ref_file.stat().st_size
            if size > 100000:  # 100KB
                self.warnings.append(
                    f"[WARNING]  Reference file {ref_file.name} is very large ({size//1000}KB) - may impact performance"
                )

            # Check for TODO markers
            content = ref_file.read_text(encoding='utf-8')
            if 'TODO' in content:
                self.warnings.append(f"[WARNING]  Found TODO markers in {ref_file.name}")

    def validate_scripts(self):
        """Validate script files if they exist."""
        scripts_dir = self.skill_path / 'scripts'
        if not scripts_dir.exists():
            return  # Scripts are optional

        script_files = list(scripts_dir.glob('*.py'))

        if not script_files:
            self.suggestions.append("[TIP] scripts/ directory exists but contains no .py files")
            return

        # Check each script
        for script_file in script_files:
            content = script_file.read_text(encoding='utf-8')

            # Check for shebang
            if not content.startswith('#!/usr/bin/env python'):
                self.suggestions.append(
                    f"[TIP] {script_file.name} missing shebang (#!/usr/bin/env python3)"
                )

            # Check if executable
            if not os.access(script_file, os.X_OK):
                self.suggestions.append(
                    f"[TIP] {script_file.name} not executable (run: chmod +x {script_file.name})"
                )

            # Check for basic validation script structure
            if 'validate' in script_file.name:
                if 'if __name__ == ' not in content:
                    self.warnings.append(
                        f"[WARNING]  {script_file.name} missing __main__ block"
                    )

                if 'sys.exit' not in content:
                    self.warnings.append(
                        f"[WARNING]  {script_file.name} should use sys.exit() with status code"
                    )

    def validate_workflows(self):
        """Validate workflow structure if present."""
        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        # Check if workflow exists
        has_workflow = bool(re.search(r'##?\s+Workflow', content, re.IGNORECASE))
        if not has_workflow:
            return  # Workflows are optional

        # If workflow exists, validate structure
        steps = re.findall(r'###?\s+Step\s+(\d+)', content)
        if steps:
            step_numbers = [int(s) for s in steps]

            # Check sequential numbering
            expected = list(range(1, len(step_numbers) + 1))
            if step_numbers != expected:
                self.warnings.append(
                    f"[WARNING]  Workflow steps not sequential: {step_numbers} (expected: {expected})"
                )

        # Check for validation checkpoints
        if 'validate' not in content.lower() and 'check' not in content.lower():
            self.suggestions.append(
                "[TIP] Workflow found but no validation checkpoints - consider adding quality gates"
            )

    def generate_report(self) -> Tuple[bool, str]:
        """Generate validation report."""
        report_lines = []

        # Header
        report_lines.append("=" * 70)
        report_lines.append(f"SKILL VALIDATION REPORT: {self.skill_path.name}")
        report_lines.append("=" * 70)
        report_lines.append("")

        # Errors
        if self.errors:
            report_lines.append("ERRORS (must fix before packaging):")
            report_lines.append("-" * 70)
            for error in self.errors:
                report_lines.append(error)
            report_lines.append("")

        # Warnings
        if self.warnings:
            report_lines.append("WARNINGS (should review):")
            report_lines.append("-" * 70)
            for warning in self.warnings:
                report_lines.append(warning)
            report_lines.append("")

        # Suggestions
        if self.suggestions:
            report_lines.append("SUGGESTIONS (optional improvements):")
            report_lines.append("-" * 70)
            for suggestion in self.suggestions:
                report_lines.append(suggestion)
            report_lines.append("")

        # Summary
        report_lines.append("=" * 70)
        if self.errors:
            report_lines.append(f"[ERROR] VALIDATION FAILED - {len(self.errors)} error(s) found")
            report_lines.append("Fix all errors before packaging the skill.")
            exit_code = 1
            success = False
        elif self.warnings:
            report_lines.append(f"[WARNING]  VALIDATION PASSED WITH WARNINGS - {len(self.warnings)} warning(s)")
            report_lines.append("Skill can be packaged, but review warnings first.")
            exit_code = 2
            success = True
        else:
            report_lines.append("[OK] ALL VALIDATIONS PASSED")
            if self.suggestions:
                report_lines.append(f"({len(self.suggestions)} optional suggestion(s) provided)")
            exit_code = 0
            success = True

        report_lines.append("=" * 70)

        return success, "\n".join(report_lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python comprehensive_validate.py <skill_directory>")
        print("")
        print("Validates skill structure, content quality, and best practices.")
        print("Exit codes:")
        print("  0 = All validations passed")
        print("  1 = Errors found (must fix)")
        print("  2 = Warnings only (should review)")
        sys.exit(1)

    skill_path = sys.argv[1]
    validator = SkillValidator(skill_path)
    success, report = validator.validate_all()

    print(report)

    # Exit with appropriate code
    if validator.errors:
        sys.exit(1)
    elif validator.warnings:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
