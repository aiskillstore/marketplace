# Quality Guidelines (Soft Review)

These guidelines are not enforced by automated tooling. Reviewers should check these during manual PR review and flag violations as suggestions.

## 1. Skill Scope — Avoid Overlap

Before approving a new skill, check existing skills for functional overlap.

- If the new skill's capability is a subset of an existing skill, suggest extending the existing one instead
- If there is partial overlap, the PR description must clearly explain the boundary
- Example: a voice synthesis skill should clarify how it differs from `frontend-dev`'s TTS capabilities

## 2. Description Quality

The `description` field in SKILL.md is what the agent uses to decide whether to activate the skill. A good description must include:

- What the skill does
- When to use it (trigger conditions)
- Keywords or phrases that should activate it

Bad: `"A skill for making PDFs"`
Good: `"Generate, fill, and reformat PDF documents. Use when the user asks to create, modify, or design any PDF file. Triggers: PDF, .pdf, document generation."`

## 3. File Size Awareness

Skills are loaded into the agent's context window. Every token counts.

- Individual `.md` files should stay focused and concise
- If a reference document exceeds ~500 lines, consider splitting it into parts
- Do not embed large data blobs (base64 images, full API responses) in Markdown
- Prefer linking to external resources over inlining lengthy content

## 4. Credential Handling

The validation script only blocks high-confidence secret patterns (OpenAI keys, AWS keys, JWT tokens). Reviewers should additionally check for:

- API keys or passwords assigned directly in code (e.g., `api_key = "abc123..."`)
- Credentials passed as plain string arguments instead of environment variable reads
- Example keys that look realistic enough to be mistaken for real ones
- Scripts that lack a clear error message when a required env var is missing

If a skill involves external APIs, verify that SKILL.md documents the required environment variables.

## 5. Script Quality

If the skill includes helper scripts in `scripts/`:

- Scripts should have a shebang line (`#!/usr/bin/env python3`)
- A `requirements.txt` should be present listing all dependencies if external libraries are needed.
- Errors should produce clear messages, not raw tracebacks

## 6. Language

- SKILL.md content and code should be written in English
- Reference docs are recommended to be in English

## 7. README Sync

When a new skill is added, both `README.md` and `README_zh.md` should be updated with the new skill in the table. Community-submitted skills should set the Source column to `Community`.
