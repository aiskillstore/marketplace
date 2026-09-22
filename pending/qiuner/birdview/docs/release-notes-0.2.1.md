# Birdview 0.2.1

[中文](release-notes-0.2.1.zh.md)

Better guidance for better AI code: this patch refines how Birdview asks agents to understand architecture, clarify decisions and evaluate changes before implementation.

- Planning now resolves source-answerable questions first, asks only about material unresolved decisions, and gives a recommendation with its tradeoff.
- On-demand architecture review examines responsibilities, coupling and verification difficulties using source evidence, migration costs and risks. Ordinary mapping does not automatically start a refactor; proposals remain distinct from the current architecture.
- The website offers Codex, Claude Code and DeepSeek Harness installation choices, copyable commands, dependency checks and a trial prompt in English and Chinese.
- Clearer README examples and a short usage feedback form make it easier to share successful runs, missing modules, incorrect relationships and installation problems.

These refinements aim to improve coding quality by reducing blind edits and unsupported refactoring. No comparative coding-quality benchmark has been run; passing repository checks does not establish better code generation or guarantee agent compliance.

Install the complete release source using the [installation guide](installation.md), then run `npm ci` and `node scripts/birdview.mjs doctor` in the skill directory. Preserve local customizations when updating; explicit project on-demand settings remain in effect. GitHub distribution only; no npm publication.

Verification: repository tests, example validation, doctor, reproducible demo build and browser checks. Documentation pairs and links were checked. Claude Code and DeepSeek Harness live-session activation remains unverified; Birdview displays declared activity, not independently observed edits.
