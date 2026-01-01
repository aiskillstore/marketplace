# Changelog

All notable changes to the AI Skillstore marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.1.0] - 2026-01-01

### Summary

AI Skillstore marketplace v0.1.0 launches with 28 new plugins spanning agent development, document and office formats, design, integrations, and testing. This release also strengthens release/sync workflows and schema compliance, improving namespaced plugin handling, incremental imports, and CI reliability for publishing and Supabase synchronization. 

### Statistics

- Total plugins: 28
- New plugins: 28
- Updated plugins: 0

### New Plugins

- `agent-development`
- `algorithmic-art`
- `brand-guidelines`
- `canvas-design`
- `claude-opus-4-5-migration`
- `command-development`
- `doc-coauthoring`
- `docx`
- `frontend-design`
- `hook-development`
- `internal-comms`
- `mcp-builder`
- `mcp-integration`
- `metabase-docs-review`
- `payloadcms-payload`
- `pdf`
- `plugin-settings`
- `plugin-structure`
- `pptx`
- `skill-creator`
- `skill-development`
- `slack-gif-creator`
- `template-skill`
- `theme-factory`
- `web-artifacts-builder`
- `webapp-testing`
- `writing-hookify-rules`
- `xlsx`

### Changes

- feat: add tag-triggered auto-release workflow
- chore: remove outdated CHANGELOG.md file
- fix: correct plugin slug extraction in incremental sync
- fix: remove redundant canonical_name assignment in sync-to-supabase workflow
- fix: support nested plugin structure in release workflows
- fix: correct plugin move path in on-pr-merge workflow
- refactor: simplify plugin path resolution to use source directly
- fix: correct source paths to include plugins/ prefix (#49)
- fix: use source field for directory path in on-pr-merge workflow
- refactor: remove payload plugin and standardize field naming
- refactor: update plugin.schema.json with official component fields
- refactor: align marketplace.json and schema with official Claude Code spec
- fix: use namespaced plugin name in marketplace.json
- fix: support namespaced plugin paths in sync-to-supabase workflow
- fix: add owner property to skill-report.schema.json meta
- fix: allow namespaced plugin names in plugin.schema.json
- chore: fix schema naming patterns, upgrade Node.js to v24, publish English only
- chore: clear all plugins from marketplace for re-import
- feat: migrate to GitHub-style username/skill-name naming
- fix: use global git config for CLI subprocess operations
- fix: handle race conditions and stale branches in CI workflows
- fix: configure git identity before CLI runs to prevent author unknown error
- refactor: replace trust_level with source_type in schema and all skill-report files
- refactor: replace AI API call with codex CLI in release workflow
- chore: remove unused process-skills.sh script
- feat: add skillstore callback notifications in process-submission workflow
- chore: reset to v0.1.0 for changelog sync test
- chore: reset to v0.1.0 for clean v0.2.0 release test
- chore: reset version to 0.1.0 for clean v0.2.0 release
- fix: remove broken JSON.parse on CHANGELOG.md in release sync
- fix: uncomment package-lock.json in .gitignore to include it in version control
- fix: validate plugins/ skill-report.json and migrate legacy format
- ci: add SKILLSTORE_AGENTS env var to process-submission workflow
- fix: map risk_level to skills table enum (safe→low, critical→high)
- fix: remove deprecated fields, add file_structure and language
- feat: comprehensive Supabase sync with all fields
- fix: use kebab-case slugs for plugin name field
- fix: use PAT_TOKEN for PR creation to trigger validation workflow
- fix: only validate skill-report.json in pending/ folder
- fix: correct path patterns to match .claude-plugin structure
- fix: correct CLI output path to avoid double pending directory
- fix: use PAT_TOKEN for cross-repo CLI download
- fix: use gh CLI for reliable release download
- refactor: replace bash script with pre-built CLI binary
- fix: add canonical_name to sync script
- fix: remove extra closing brace from JSON schema
- fix: use --slurpfile for JSON schema to avoid jq escaping issues
- feat: add multi-skill detection to process-submission workflow
- fix: extract skill name from SKILL.md frontmatter instead of repo name
- refactor: use dynamic WORK_DIR for concurrency safety
- fix: support blob URLs and increase SKILL.md search depth
- fix: use env var for release body to prevent shell backtick interpretation
- docs: add release workflow documentation
- feat: add release workflow with Supabase sync
- fix: stage deletions from pending/ in on-pr-merge workflow
- fix: use bash substitution for multiline values in workflow
- fix: cleanup /tmp artifacts before each workflow run
- fix: update schemas to draft-07 and fix path references
- feat: use self-hosted runner with custom AI API
- feat: add submission processing and sync workflows
- feat: import all 16 Anthropic official skills with AI audit reports
- feat: initialize Claude Code plugin marketplace


