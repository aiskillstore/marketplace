# Code Review Skill

Automated PR code review with multi-agent analysis.

## Commands

### `/code_review`

Performs automated code review on a pull request.

**Usage:**
```bash
/code_review              # Output to terminal
/code_review --comment    # Post as PR comments
```

## Features

- Pre-check: Skips closed, draft, trivial, or already-reviewed PRs
- Multi-agent review: 2x AGENTS.md compliance, 1x bug detection, 1x logic analysis
- Confidence scoring: Filters issues below 80% confidence
- Inline comments: Posts review feedback directly on PR files

## Prerequisites

- [GitHub CLI](https://cli.github.com/) installed and authenticated
- `github-pr` skill installed (bundled automatically)
