---
name: creating-pull-requests
description: >
  Creates pull requests with generated descriptions.
  Triggered when: PR creation, pull request, merge request, code review preparation.
allowed-tools: Bash(git:*), Bash(gh:*)
---

# Pre-check

```bash
git branch --show-current
git status
git log --oneline <main-branch>..HEAD  # Check CLAUDE.md for main branch name
```

# Push to Remote

```bash
git push -u origin <branch-name>
```

# PR Description Format

```markdown
## Summary

- [Change 1]
- [Change 2]

## Test plan

- [ ] [Test item 1]
- [ ] [Test item 2]
```

# Create PR

```bash
gh pr create \
  --title "<title>" \
  --body "$(cat <<'EOF'
## Summary

- Changes...

## Test plan

- [ ] Test items...
EOF
)"
```

# Options

| Option | Usage |
|--------|-------|
| `--draft` | Draft PR |
| `--base <branch>` | Target branch |
| `--assignee @me` | Self-assign |
| `--label <label>` | Add label |

# Completion Report

- PR URL
- Title
- Target branch
