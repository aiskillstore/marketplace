# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-14

### Added
- `SKILL.md` with 8 core actions: `capture`, `classify`, `route`, `normalize`, `review`, `archive`, `audit`, `suggest`
- Classification decision tree with Project / Area / Resource / Archive indicators (`references/classification-rules.md`)
- Frontmatter schema with all PARA-specific fields and writing rules (`references/frontmatter-schema.md`)
- Review playbook with weekly / monthly / quarterly rhythms and structured report format (`references/review-playbook.md`)
- Compatibility notes for `obsidian-markdown` and `obsidian-cli` role division (`references/compatibility-notes.md`)
- Defensive-by-default safety rules (no mass moves, no deletion, dry-run mode)
- Configurable vault paths (default: `0_Inbox`, `1_Projects`, `2_Areas`, `3_Resources`, `4_Archives`)
- Dry-run mode support for all structural actions
- Change log format (`PARA-Changelog.md` appended to vault root on structural changes)
- Confidence levels (`high` / `medium` / `low`) with corresponding action thresholds
- `needs_review` flag for ambiguous classifications
