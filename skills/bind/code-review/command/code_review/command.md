---
description: Automated PR code review
allowed-tools: Bash(*)
agent: build
---

Run an automated code review:

1. Run check: `bun .opencode/skill/github-pr/check-review-needed.js`
2. Gather guidelines: `bun .opencode/skill/github-pr/list-guideline-files.js --json`
3. Summarize PR with `gh pr view` and `gh pr diff`
4. Launch 4 parallel @reviewer subagents (2x compliance, 1x bug, 1x logic)
5. Validate and filter issues (80+ confidence)
6. Post inline comments

If no issues: post "No issues found. Checked for bugs and AGENTS.md compliance."
