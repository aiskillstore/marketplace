# Changelog

All notable changes to the AI Skillstore marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## [0.2.0] - 2025-12-31

### Summary

AI Skillstore marketplace v0.2.0 expands the catalog with 38 newly added plugins (26 total available), covering agent/command and skill development, MCP integration and builder tools, frontend and theme workflows, document creation (PDF/DOCX/PPTX/XLSX), and Slack utilities. This release gives users a broader, more practical set of ready-to-use building blocks to speed up common automation and content workflows with less setup. 

### Statistics

- Total plugins: 26
- New plugins: 38
- Updated plugins: 0

### New Plugins

- `agent-development`
- `claude-opus-4-5-migration`
- `command-development`
- `frontend-design`
- `hook-development`
- `mcp-integration`
- `plugin-settings`
- `plugin-structure`
- `skill-development`
- `writing-hookify-rules`
- `algorithmic-art`
- `brand-guidelines`
- `canvas-design`
- `doc-coauthoring`
- `docx`
- `frontend-design`
- `internal-comms`
- `mcp-builder`
- `pdf`
- `pptx`
- `skill-creator`
- `slack-gif-creator`
- `template-skill`
- `theme-factory`
- `web-artifacts-builder`
- `webapp-testing`
- `xlsx`
- `agent-development`
- `claude-opus-4-5-migration`
- `command-development`
- `algorithmic-art`
- `brand-guidelines`
- `skill-creator`
- `writing-hookify-rules`
- `writing-hookify-rules`
- `writing-hookify-rules`
- `writing-hookify-rules`
- `writing-hookify-rules`

### Infrastructure Changes

- chore: reset version to 0.1.0 for clean v0.2.0 release
- release: v0.3.0
- release: v0.2.1
- fix: remove broken JSON.parse on CHANGELOG.md in release sync
- release: v0.2.0
- fix: uncomment package-lock.json in .gitignore to include it in version control
- fix: validate plugins/ skill-report.json and migrate legacy format
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


## [0.1.0] - 2025-12-29

### Summary

Initial beta release of the AI Skillstore marketplace with 16 curated plugins from Anthropic's official skills collection.

### Statistics

- Total plugins: 16
- New plugins: 16
- Updated plugins: 0

### New Plugins

- `algorithmic-art` - Create generative art using p5.js with seeded randomness
- `brand-guidelines` - Apply Anthropic brand colors and typography
- `canvas-design` - Design visual artifacts with HTML Canvas
- `doc-coauthoring` - Collaborative document editing with AI
- `docx` - Generate and manipulate Word documents
- `frontend-design` - Create beautiful frontend interfaces
- `internal-comms` - Draft internal communications and memos
- `mcp-builder` - Build Model Context Protocol servers
- `pdf` - Generate and process PDF documents
- `pptx` - Create PowerPoint presentations programmatically
- `skill-creator` - Create new AI skills from scratch
- `slack-gif-creator` - Generate animated GIFs for Slack
- `theme-factory` - Create consistent design themes
- `web-artifacts-builder` - Build interactive web artifacts
- `webapp-testing` - Test web applications with AI assistance
- `xlsx` - Generate and manipulate Excel spreadsheets

### Infrastructure

- Initial marketplace structure with plugin catalog
- Automated submission workflow via skillstore.io
- Security analysis pipeline for all submissions
- Supabase sync for website integration
- GitHub Actions for CI/CD automation
