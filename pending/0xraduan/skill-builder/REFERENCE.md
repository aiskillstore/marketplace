# Skill Builder - Reference Documentation

Comprehensive guide for the skill-builder meta-skill.

## Table of Contents

1. [Skill Anatomy](#skill-anatomy)
2. [YAML Frontmatter Reference](#yaml-frontmatter-reference)
3. [Description Best Practices](#description-best-practices)
4. [File Structure Patterns](#file-structure-patterns)
5. [Script Templates](#script-templates)
6. [Common Skill Patterns](#common-skill-patterns)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Testing & Validation](#testing--validation)

---

## Skill Anatomy

Every skill must have a `SKILL.md` file with YAML frontmatter and Markdown content:

```yaml
---
name: skill-name              # Required: lowercase, hyphens, max 64 chars
description: Brief description # Required: max 1024 chars, include triggers
allowed-tools: Tool1, Tool2   # Optional: restrict available tools
---

# Skill Title

## Requirements
[Dependencies if needed]

## Instructions
[Step-by-step guidance for Claude]

## Examples
[Concrete usage examples]
```

### Required Fields

**`name`:**
- Must use lowercase letters, numbers, and hyphens only
- Maximum 64 characters
- Cannot contain spaces, underscores, or special characters
- Example: `pdf-processor`, `test-coverage-analyzer`

**`description`:**
- Maximum 1024 characters
- Must include WHAT the skill does AND WHEN to use it
- Should mention trigger keywords, file types, technologies
- Can mention required dependencies
- This is THE MOST CRITICAL field for skill discovery

### Optional Fields

**`allowed-tools`:**
- Comma-separated list of tool names
- Restricts Claude to only these tools when skill is active
- No permission prompts needed for listed tools
- Useful for read-only or limited-scope skills

**Examples:**
```yaml
allowed-tools: Read, Grep, Glob                    # Read-only
allowed-tools: Read, Write, Edit, Glob, Grep       # File operations
allowed-tools: Bash                                 # Shell operations only
```

---

## YAML Frontmatter Reference

### Minimal Frontmatter
```yaml
---
name: simple-skill
description: Does X when user mentions Y or works with Z files.
---
```

### With Tool Restrictions
```yaml
---
name: code-reviewer
description: Review code for best practices and issues. Use when reviewing code, checking PRs, or analyzing code quality.
allowed-tools: Read, Grep, Glob
---
```

### Common Tool Combinations

**Read-only analysis:**
```yaml
allowed-tools: Read, Grep, Glob
```

**Documentation generation:**
```yaml
allowed-tools: Read, Write, Glob, Grep
```

**File manipulation:**
```yaml
allowed-tools: Read, Write, Edit, Glob, Grep
```

**Git operations:**
```yaml
allowed-tools: Bash, Read, Glob
```

---

## Description Best Practices

### The Formula

```
[Action verbs] [what it does]. Use when [triggers: keywords, scenarios, file types]. [Optional: Requires X].
```

### Good Examples

**PDF Processing:**
```
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction. Requires pypdf and pdfplumber packages.
```

**Excel Analysis:**
```
Analyze Excel spreadsheets, create pivot tables, and generate charts. Use when working with Excel files, spreadsheets, or analyzing tabular data in .xlsx format. Requires pandas and openpyxl.
```

**Code Review:**
```
Review code for best practices, security issues, and performance concerns. Use when reviewing code, checking pull requests, analyzing code quality, or when user mentions code review or PR review.
```

**Git Commit Messages:**
```
Generate clear, conventional commit messages from git diffs. Use when writing commit messages, reviewing staged changes, or when user mentions commits or committing code.
```

### Bad Examples (and why)

❌ **Too vague:**
```
Helps with documents
```
*Why bad: Doesn't specify which documents, what help, or when to use*

❌ **Missing triggers:**
```
Processes PDF files using pypdf library
```
*Why bad: No trigger keywords for when to activate*

❌ **What without when:**
```
A skill for analyzing Python test coverage and generating reports
```
*Why bad: Doesn't mention trigger words like "coverage", "pytest", "tests"*

❌ **Too technical:**
```
Leverages pypdf2 API to perform PDF manipulation operations via programmatic interfaces
```
*Why bad: User wouldn't say these words; use "PDF files", "extract", "merge" instead*

### Trigger Keywords to Include

**File types:**
- Mention extensions: `.pdf`, `.xlsx`, `.csv`, `.json`, etc.
- Mention formats: "PDF files", "Excel spreadsheets", "JSON data"

**Technologies:**
- Tools: "pytest", "git", "docker", "npm"
- Languages: "Python", "JavaScript", "TypeScript"
- Frameworks: "React", "FastAPI", "Django"

**Actions/Scenarios:**
- What user might say: "analyze", "review", "generate", "extract"
- Use cases: "test coverage", "code review", "commit messages"

**Common phrases:**
- Include synonyms: "PDF/pdf files", "tests/testing", "commit/committing"
- Natural language: "when user asks about X", "when working with Y"

---

## File Structure Patterns

### Pattern 1: Simple Instruction-Based Skill

**When to use:** Skill teaches Claude how to do something, no custom scripts needed

```
skill-name/
└── SKILL.md
```

**Example use cases:**
- Git commit message generation
- Code review checklists
- Documentation standards
- Communication templates

**SKILL.md structure:**
```markdown
---
name: skill-name
description: [focused description with triggers]
---

# Skill Name

Brief overview of what this does.

## Instructions

1. Step-by-step process
2. What to look for
3. How to format output

## Examples

**Example 1:**
[Show concrete example]

**Example 2:**
[Show another example]
```

### Pattern 2: Script-Powered Skill

**When to use:** Skill needs custom tooling, data processing, or API calls

```
skill-name/
├── SKILL.md
└── scripts/
    └── processor.py
```

**Example use cases:**
- PDF text extraction with custom parsing
- API integrations
- Data transformation
- File format conversions

**SKILL.md structure:**
```markdown
---
name: skill-name
description: [description with what it does and when to use]
---

# Skill Name

## Requirements

Scripts use `uv` for dependency management. Dependencies are declared inline using PEP 723 metadata.

## Instructions

1. Process input using the helper script
2. Run with: `uv run scripts/processor.py <args>`
3. Handle output/results

## Script Usage

**Basic usage:**
```bash
uv run scripts/processor.py input.txt
```

**With options:**
```bash
uv run scripts/processor.py input.txt -o output.txt --verbose
```

Or if executable:
```bash
./scripts/processor.py input.txt
```

## Examples

[Examples showing script usage]
```

### Pattern 3: Comprehensive Multi-File Skill

**When to use:** Complex skill with extensive documentation, multiple scripts, templates

```
skill-name/
├── SKILL.md
├── REFERENCE.md
├── scripts/
│   ├── main.py
│   └── utils.py
└── templates/
    └── template.txt
```

**Example use cases:**
- Full workflow automation
- Complex data pipelines
- Multi-step processes
- Framework scaffolding

**File purposes:**
- `SKILL.md` - Quick start, basic usage, common examples
- `REFERENCE.md` - Detailed API docs, advanced usage, troubleshooting
- `scripts/` - Custom tooling
- `templates/` - File templates, boilerplate code

**SKILL.md uses progressive disclosure:**
```markdown
## Quick Start

[Basic usage here]

For advanced usage, see [REFERENCE.md](REFERENCE.md).
```

---

## Script Templates

### Python Script Template (Preferred)

**File:** `scripts/[name].py`

**IMPORTANT: Always use uv with PEP 723 inline metadata for self-contained, portable scripts.**

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "package-name>=1.0.0",
#     "another-package>=2.0.0",
# ]
# ///
"""
[Script purpose - one line]

Usage:
    uv run scripts/[name].py <input> [options]
    ./scripts/[name].py <input> [options]  # if executable

Description:
    [Detailed description of what this script does]
    [Mention key features or behavior]

Dependencies:
    Dependencies are declared inline using PEP 723 metadata.
    uv will automatically install them when the script runs.

Examples:
    uv run scripts/[name].py data.txt
    uv run scripts/[name].py data.txt -o output.json --verbose
"""

import argparse
import sys
from pathlib import Path
from typing import Optional


def process(input_path: Path, output_path: Optional[Path] = None, verbose: bool = False) -> None:
    """
    Main processing logic.

    Args:
        input_path: Path to input file
        output_path: Optional path to output file
        verbose: Enable verbose logging
    """
    if verbose:
        print(f"Processing: {input_path}")

    # Read input
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open('r') as f:
        data = f.read()

    # Process data
    result = data  # Replace with actual processing

    # Write output
    if output_path:
        with output_path.open('w') as f:
            f.write(result)
        if verbose:
            print(f"Output written to: {output_path}")
    else:
        print(result)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="[Brief description]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run scripts/[name].py input.txt
  uv run scripts/[name].py input.txt -o output.txt --verbose
        """
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input file path"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (optional, prints to stdout if not specified)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    try:
        process(args.input, args.output, args.verbose)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Bash Script Template (When Needed)

**File:** `scripts/[name].sh`

```bash
#!/bin/bash
#
# [Script purpose - one line]
#
# Usage:
#   bash scripts/[name].sh <input> [options]
#
# Description:
#   [Detailed description]

set -euo pipefail

# Default values
VERBOSE=false
OUTPUT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 <input> [-o output] [-v]"
            exit 0
            ;;
        *)
            INPUT="$1"
            shift
            ;;
    esac
done

# Validate input
if [ -z "${INPUT:-}" ]; then
    echo "Error: Input file required" >&2
    echo "Usage: $0 <input> [-o output] [-v]" >&2
    exit 1
fi

if [ ! -f "$INPUT" ]; then
    echo "Error: Input file not found: $INPUT" >&2
    exit 1
fi

# Process
if [ "$VERBOSE" = true ]; then
    echo "Processing: $INPUT"
fi

# Main logic here
result=$(cat "$INPUT")  # Replace with actual processing

# Output
if [ -n "$OUTPUT" ]; then
    echo "$result" > "$OUTPUT"
    [ "$VERBOSE" = true ] && echo "Output written to: $OUTPUT"
else
    echo "$result"
fi
```

---

## Common Skill Patterns

### Pattern: Read-Only Analysis Skill

**Characteristics:**
- Analyzes code, files, or data
- Doesn't modify anything
- Uses `allowed-tools: Read, Grep, Glob`

**Example:**
```yaml
---
name: security-reviewer
description: Analyze code for security vulnerabilities, hardcoded secrets, and unsafe patterns. Use when reviewing security, checking for vulnerabilities, or auditing code security.
allowed-tools: Read, Grep, Glob
---

# Security Reviewer

## Instructions

1. Search for common vulnerability patterns:
   - Hardcoded secrets (API keys, passwords)
   - SQL injection risks
   - XSS vulnerabilities
   - Insecure dependencies

2. Check for:
   - Exposed credentials in .env files
   - Unsafe eval() usage
   - Missing input validation
   - Weak cryptography

3. Report findings with:
   - Severity (Critical/High/Medium/Low)
   - File location and line number
   - Recommended fix

## Examples

**Check for hardcoded secrets:**
Use Grep to search for patterns like `api_key=`, `password=`, `SECRET_KEY`
```

### Pattern: Code Generation Skill

**Characteristics:**
- Creates or modifies code
- May use templates
- Needs Write/Edit tools

**Example:**
```yaml
---
name: react-component-generator
description: Generate React components with TypeScript, props interfaces, and tests. Use when creating React components, scaffolding UI elements, or building TypeScript React code.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# React Component Generator

## Instructions

1. Analyze project structure:
   - Find existing components for patterns
   - Check TypeScript config
   - Identify testing setup

2. Generate component with:
   - TypeScript interface for props
   - Functional component with proper typing
   - Basic styling setup
   - Unit tests

3. Follow project conventions:
   - Match existing naming patterns
   - Use project's import style
   - Follow component structure

## Template

[Component template here]

## Examples

**Creating a Button component:**
[Show example]
```

### Pattern: Script-Powered Data Processing

**Characteristics:**
- Custom data transformation
- Python script for heavy lifting (using uv)
- Self-contained with inline dependencies

**Example:**
```yaml
---
name: csv-analyzer
description: Analyze CSV files, generate statistics, detect data quality issues, and create visualizations. Use when working with CSV files, data analysis, or spreadsheet data.
---

# CSV Analyzer

## Requirements

The script uses `uv` for dependency management. Dependencies are declared inline using PEP 723 metadata.

## Instructions

1. Use the analysis script:
   ```bash
   uv run scripts/analyze_csv.py data.csv
   ```

   Or if executable:
   ```bash
   ./scripts/analyze_csv.py data.csv
   ```

2. Script provides:
   - Basic statistics (mean, median, std)
   - Missing value analysis
   - Column type detection
   - Data quality report

3. Optional visualization:
   ```bash
   uv run scripts/analyze_csv.py data.csv --plot
   ```

## Examples

[Examples here]
```

### Pattern: Workflow Orchestration Skill

**Characteristics:**
- Multi-step process
- Coordinates multiple tools
- May check various conditions

**Example:**
```yaml
---
name: deployment-checker
description: Pre-deployment validation checklist for production releases. Use before deploying, when preparing releases, or when user mentions deployment or production release.
allowed-tools: Bash, Read, Grep
---

# Deployment Checker

## Instructions

Execute this pre-deployment checklist:

### 1. Code Quality
- [ ] Run linter: `npm run lint`
- [ ] Run tests: `npm run test`
- [ ] Check test coverage > 80%

### 2. Build Verification
- [ ] Production build succeeds: `npm run build`
- [ ] No build warnings
- [ ] Bundle size acceptable

### 3. Configuration
- [ ] Environment variables set
- [ ] Secrets not in code
- [ ] Database migrations ready

### 4. Documentation
- [ ] CHANGELOG updated
- [ ] README current
- [ ] API docs updated

### 5. Final Checks
- [ ] Version bumped
- [ ] Git tag created
- [ ] Deployment notes written

Report results in checklist format with ✓/✗ for each item.
```

---

## Troubleshooting Guide

### Problem: Skill Doesn't Activate

**Symptoms:**
- User triggers skill-appropriate request but skill isn't used
- Claude doesn't recognize when to use the skill

**Diagnosis:**
1. Check description specificity
2. Verify trigger keywords present
3. Test with exact trigger phrases

**Solutions:**

**Add specific trigger keywords:**
```yaml
# Before (vague)
description: Process PDF files

# After (specific)
description: Extract text from PDF files. Use when working with PDF files, .pdf documents, or when user mentions PDF extraction or PDF parsing.
```

**Include file extensions:**
```yaml
# Before
description: Work with Excel files

# After
description: Analyze Excel spreadsheets (.xlsx, .xls), create pivot tables, generate charts. Use when working with Excel, spreadsheets, or .xlsx files.
```

**Add synonym triggers:**
```yaml
# Include variations users might say
description: Generate git commit messages. Use when writing commits, committing code, creating commit messages, or when user mentions git commit or committing changes.
```

**Test with exact phrases from description:**
If description says "Use when working with PDF files", test with: "Can you help me work with this PDF file?"

### Problem: Skill Activates Too Often

**Symptoms:**
- Skill activates for unrelated requests
- Description too broad

**Solutions:**

**Make description more specific:**
```yaml
# Before (too broad)
description: Help with Python code

# After (focused)
description: Analyze Python test coverage using pytest-cov. Use specifically for Python test coverage analysis, pytest coverage reports, or identifying untested code.
```

**Split into multiple focused skills:**
```yaml
# Instead of one broad "Python helper" skill, create:
# - python-test-coverage
# - python-linter
# - python-formatter
```

### Problem: Scripts Don't Execute

**Symptoms:**
- Permission denied errors
- Scripts not found
- Import errors

**Solutions:**

**Make scripts executable:**
```bash
chmod +x scripts/*.py
```

**Use full python path in SKILL.md:**
```bash
python scripts/name.py  # Not just ./scripts/name.py
```

**Document dependencies clearly:**
```markdown
## Requirements

Install required packages:
```bash
pip install pandas numpy
```
```

**Test scripts independently:**
```bash
cd /path/to/skill
python scripts/name.py --help
```

### Problem: YAML Parse Errors

**Symptoms:**
- Skill doesn't load
- Error messages about frontmatter

**Solutions:**

**Check frontmatter format:**
```yaml
# Correct
---
name: skill-name
description: Description here
---

# Incorrect - missing closing ---
---
name: skill-name
description: Description here

# Incorrect - no opening ---
name: skill-name
description: Description here
---
```

**Validate YAML syntax:**
- No tabs (use spaces)
- Proper indentation
- Quotes around special characters

**Test with minimal frontmatter:**
```yaml
---
name: test-skill
description: Test description
---
```

---

## Testing & Validation

### Manual Testing Process

**1. Verify file structure:**
```bash
# Personal skill
ls -la ~/.claude/skills/skill-name/
# Should show SKILL.md at minimum

# Project skill
ls -la .claude/skills/skill-name/
```

**2. Check YAML validity:**
```bash
head -n 10 ~/.claude/skills/skill-name/SKILL.md
# Verify frontmatter format
```

**3. Test activation with trigger phrases:**

From the skill description, extract trigger keywords and test:

```
Description: "Extract text from PDF files. Use when working with PDF files..."

Test phrases:
- "Can you help me extract text from a PDF?"
- "I need to work with PDF files"
- "How do I process this .pdf document?"
```

**4. Ask Claude to list skills:**
```
What skills are available?
```

Verify your skill appears in the list.

**5. Debug mode (if needed):**
```bash
claude --debug
# Watch for skill loading messages
```

### Validation Checklist

When creating a skill, verify:

- [ ] Name is lowercase with hyphens only
- [ ] Name is max 64 characters
- [ ] Description is max 1024 characters
- [ ] Description includes WHAT and WHEN
- [ ] Description has specific trigger keywords
- [ ] YAML frontmatter is valid (opening and closing `---`)
- [ ] SKILL.md has clear instructions
- [ ] SKILL.md has concrete examples
- [ ] Scripts (if any) are documented
- [ ] Dependencies (if any) are listed
- [ ] File is saved in correct location (personal vs project)

### Testing Different Scopes

**Personal skill test:**
```bash
# Skill should work in any directory
cd /tmp
claude
> [trigger the skill]
```

**Project skill test:**
```bash
# Skill should only work in project directory
cd /path/to/project
claude
> [trigger the skill]

cd /somewhere/else
claude
> [skill should not activate]
```

---

## Quick Reference

### File Locations

```
Personal skills: ~/.claude/skills/
Project skills (personal-os): /path/to/personal-os/skills/
Project skills (generic): .claude/skills/
```

### SKILL.md Minimal Template

```yaml
---
name: skill-name
description: What it does. Use when triggers.
---

# Skill Name

## Instructions
1. Step one
2. Step two

## Examples
**Example:**
[Show usage]
```

### Common allowed-tools Patterns

```yaml
# Read-only
allowed-tools: Read, Grep, Glob

# File editing
allowed-tools: Read, Write, Edit, Glob, Grep

# Shell operations
allowed-tools: Bash, Read

# Web research
allowed-tools: WebFetch, WebSearch, Read
```

### Description Formula

```
[Action verbs] [capabilities]. Use when [triggers: keywords, file types, scenarios]. [Optional: Requires packages].
```

### When to Use Scripts

**YES - Create scripts when:**
- Custom data processing logic needed
- API calls or external service integration
- Complex parsing or transformation
- Specialized algorithms
- Performance-critical operations

**Python Script Requirements:**
- ALWAYS use `uv run` with PEP 723 inline metadata
- Scripts must be self-contained and portable
- No separate requirements.txt or virtual environments
- Include `#!/usr/bin/env -S uv run` shebang
- Declare dependencies in `# /// script` block

**NO - Skip scripts when:**
- Teaching Claude how to use existing tools
- Providing instructions or checklists
- Defining standards or patterns
- Orchestrating existing tools
- Simple file operations
