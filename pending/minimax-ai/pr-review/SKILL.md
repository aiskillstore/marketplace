---
name: pr-review
description: >
  Review pull requests for the MiniMax Skills repository. Use when reviewing PRs,
  validating new skill submissions, or checking existing skills for compliance.
  Run the validation script first for hard checks, then apply quality guidelines
  for content review. Triggers: PR review, pull request, validate skill, check skill.
license: MIT
metadata:
  version: "1.0"
  category: tooling
---

# PR Review Skill

Review pull requests against repository standards. Two-phase process: automated validation, then manual content review.

## Phase 1: Automated Validation (Hard Rules)

Run the validation script to check structural requirements:

```bash
python .claude/skills/pr-review/scripts/validate_skills.py
```

The script checks:
- `SKILL.md` exists in every skill directory
- YAML frontmatter is parseable
- Required fields present: `name`, `description`
- `name` matches directory name
- No hardcoded secrets detected

All ERROR-level checks must pass. WARNING-level items (missing `license`, `metadata`) should be flagged but are not blockers.

See [references/structure-rules.md](references/structure-rules.md) for the complete hard rules specification.

## Phase 2: Content Review (Soft Guidelines)

After automated checks pass, review the PR against quality guidelines:

1. **Skill scope** — Does it overlap with existing skills? Is the boundary clear?
2. **Description quality** — Does the `description` include clear trigger conditions?
3. **File size** — Are reference docs reasonably sized for context window consumption?
4. **API key handling** — If external APIs are used, are credentials read from environment variables?
5. **Script quality** — Do scripts have shebang, requirements.txt, and error handling?
6. **Language** — Are SKILL.md and code written in English?
7. **README sync** — Are `README.md` and `README_zh.md` updated for new skills?

See [references/quality-guidelines.md](references/quality-guidelines.md) for soft guidelines details.

## Review Checklist Summary

### Must Pass (Blockers)
- [ ] `validate_skills.py` exits with code 0
- [ ] PR title follows conventional commit format
- [ ] One PR, one purpose

### Should Pass (Flagged in Review)
- [ ] No functional overlap with existing skills
- [ ] Description includes trigger conditions
- [ ] Files are reasonably sized
- [ ] API keys via environment variables
- [ ] README tables updated for new skills (Source column set to `Community`)
