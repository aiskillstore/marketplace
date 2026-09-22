# Birdview 0.2.0

[中文](release-notes-0.2.0.zh.md)

Use Birdview to change the development workflow: shift attention from code to architecture and open up the AI coding black box.

This release adds multi-agent installation guidance for Codex and Claude Code through the third-party skills CLI, plus native DeepSeek Harness skill-directory installation without an extra plugin.

- `mode --agent claude-code` manages `CLAUDE.md`; `codex` (default) and `deepseek` manage `AGENTS.md`. Existing rules outside the managed block are preserved.
- `doctor` validates and renders the bundled example in memory to check dependencies and template assets without writing project files.
- English and Chinese installation and mode documentation are synchronized. The default remains auto; explicit project on-demand settings still take precedence.

Follow the [installation guide](installation.md), or extract this release's complete source archive and run `npm ci`, then `node scripts/birdview.mjs doctor` inside the skill directory. Keep all assets and license notices. This release is on GitHub, not npm.

Verified: 48 automated tests, example validation, reproducible demo build, three browser checks covering views/guides/viewports, and a temporary Claude Code installation through the skills CLI followed by dependency installation and doctor. Paired documentation and local links were also checked.

Claude Code and DeepSeek Harness live-session activation has not been tested end to end. Harness discovery was checked against its filesystem provider source. Birdview shows agent-declared activity and provides instructions; it does not independently observe edits or enforce the workflow.
