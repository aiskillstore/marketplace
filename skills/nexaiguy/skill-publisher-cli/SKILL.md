---
name: skill-publisher-cli
description: 'Validate, version, and package SKILL.md folders for multi-registry marketplace publishing. Use when: Validate SKILL.md files against marketplace standards before shipping; Automate SemVer versioning and CHANGELOG updates for AI skills; Generate clean distribution ZIPs without git or cache junk files.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: skill-publisher-cli
compatibility: Compatible with SKILL.md-compatible agents
---

# Skill Publisher CLI

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/skill-publisher-cli). Scripts, extension source, and templates from the original package are not in this folder.

## Professional Skill Deployment Pipeline

The Skill Publisher CLI transforms your raw AI skill folders into production-ready marketplace packages. It solves the fragmentation problem of publishing to multiple registries like skills.sh, Agensi, and Gumroad by automating validation, versioning, and packaging into a single repeatable workflow.

## What it does

This skill orchestrates a suite of Python-based tools to ensure your SKILL.md files meet strict marketplace standards. At its core, it handles:

- **Validation:** Checks YAML frontmatter, naming conventions, and broken internal links to prevent registry rejections.
- **Versioning:** Manages SemVer bumps and automatically maintains a CHANGELOG.md file.
- **Packaging:** Generates clean, junk-free ZIP files and GitHub-ready directory structures.
- **Metadata Generation:** Renders READMEs and platform-specific metadata from your source files.

## Supported Workflows

Built for developers who need to ship fast, it supports standard registries using a 'Dry-run first' philosophy. It ensures that no files are written or bumped until you explicitly approve the changes. The tool outputs a standardized `dist/` folder containing everything needed for manual or automated uploads.

## Why use this?

Instead of manually zipping files or guessing why a registry rejected your skill, this CLI provides a local "Pre-flight Check." It guarantees that every asset—from the ZIP contents to the metadata description—is perfectly formatted for the AI skill ecosystem.

Built by Nex AI. More skills and info at nex-ai.be and slopsome.com.

## When to use

- Validate SKILL.md files against marketplace standards before shipping
- Automate SemVer versioning and CHANGELOG updates for AI skills
- Generate clean distribution ZIPs without git or cache junk files
- Create GitHub-ready folder structures for skills.sh compatibility
- Extract platform-specific metadata and tags from skill descriptions

## Known limitations

- Requires Python 3.x for helper scripts
- Local validation only: does not auto-upload to registries
- Limited to SKILL.md project structures

## Example

**Request**

Bump the version of the code-reviewer skill by a patch, add a changelog message about fixing the regex, and package it for distribution.

**Result**

Dry-run:
- Validated 'code-reviewer' (OK)
- Bump version: 0.1.0 -> 0.1.1
- Message: "Fixed regex for edge-case parsing"
- Prepare dist/code-reviewer-0.1.1.zip (excluding .git, __pycache__)
- Create github-tree/code-reviewer/
Ready to apply? Use --apply.

## Questions

### What specific problem does the Skill Publisher CLI solve for developers?

This CLI solves the problem of manual packaging and formatting errors. It automates validation, versioning, and distribution prep, ensuring your skills meet the strict submission standards of multiple registries without manual editing.

### Which AI agents and registries are compatible with this tool?

The tool is built on Python and designed to be platform-agnostic for the AI ecosystem. It is compatible with any agent or framework that uses the SKILL.md standard or requires structured YAML frontmatter for marketplace listings.

### How does the 'Dry-run' mode help during the publishing process?

The 'dry-run' feature allows you to simulate the entire publishing process without making permanent changes to your files. It identifies validation errors and shows you proposed version bumps before they are committed, preventing accidental data loss.

### What exactly is included with my purchase of this skill?

You receive the full skill package including the orchestrator tools, pre-configured validation rules, and the CLI binary. It also includes comprehensive documentation on how to integrate the CLI into your existing CI/CD or local development workflow.

### How does the skill handle versioning and changelogs?

The CLI handles SemVer (Semantic Versioning) automatically. It manages version increments in your metadata and concurrently maintains a CHANGELOG.md, ensuring your users can track features and bug fixes across every release.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
