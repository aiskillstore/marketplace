---
name: github-release-assistant
description: Generate bilingual GitHub release documentation (README.md + README.zh.md) from repo metadata and user input, and guide release prep with git add/commit/push. Use when the user asks to write or polish README files, create bilingual docs, prepare a GitHub release, or mentions release assistant/README generation.
---

# GitHub Release Assistant

## Overview
Generate polished README files in English and Chinese using repo facts plus a small config file, following a concise “Redmax-style” layout. Produce `README.md` + `README.zh.md`, then optionally guide a clean git commit and push.

## Workflow
1. Collect repo facts from `config.json`, `README.md`, `PROJECT_STRUCTURE.md`, `requirements*.txt`, and `docs/`.
2. Ask for missing details or have the user fill `release_assistant.json` (see `assets/release_config.example.json`).
3. Run the generator script to write README files.
4. Review the diff with the user and refine content if needed.
5. If requested, stage/commit/push changes with explicit confirmation.

## Quick Start
- Create or edit `release_assistant.json` in the repo root (optional but recommended).
- Run:
  `python3 /Users/cuizhanlin/.codex/skills/github-release-assistant/scripts/generate_release_readme.py --project-root <repo> --language both --overwrite`
- Verify `README.md` and `README.zh.md`.

## Git Workflow (Commit + Push)
- Run `git status` and `git diff` to show changes.
- Ask for confirmation before `git add`, `git commit`, and `git push`.
- Propose a concise commit message (e.g., `docs: add bilingual README`), and wait for approval.

## Resources
- Script: `scripts/generate_release_readme.py`.
- Templates: `assets/readme_template_en.md`, `assets/readme_template_zh.md`.
- Config example: `assets/release_config.example.json`.
- Style cues: `references/redmax_style.md`.
- Outline guide: `references/readme_outline.md`.
