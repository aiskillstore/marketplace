---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: documentation
---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- {{NEW_FEATURE_DESCRIPTION}}

### Changed

- {{CHANGED_BEHAVIOR_DESCRIPTION}}

### Deprecated

- {{DEPRECATED_FEATURE_DESCRIPTION}}

### Removed

- {{REMOVED_FEATURE_DESCRIPTION}}

### Fixed

- {{BUG_FIX_DESCRIPTION}}

### Security

- {{SECURITY_FIX_DESCRIPTION}}

---

## [{{VERSION}}] - {{YYYY-MM-DD}}

### Added

- New feature X that enables users to {{BENEFIT}} ([#{{ISSUE}}]({{ISSUE_URL}}))
- Support for {{NEW_CAPABILITY}}

### Changed

- Improved performance of {{COMPONENT}} by {{PERCENTAGE}}%
- Updated {{DEPENDENCY}} from {{OLD_VERSION}} to {{NEW_VERSION}}

### Deprecated

- `{{OLD_API}}` is deprecated, use `{{NEW_API}}` instead

### Removed

- Removed deprecated `{{FEATURE}}` (deprecated in {{VERSION}})

### Fixed

- Fixed issue where {{BUG_DESCRIPTION}} ([#{{ISSUE}}]({{ISSUE_URL}}))
- Resolved crash when {{SCENARIO}}

### Security

- Fixed {{CVE_ID}}: {{VULNERABILITY_DESCRIPTION}}

---

## [{{VERSION}}] - {{YYYY-MM-DD}}

### Added

- {{FEATURE_1}}
- {{FEATURE_2}}

### Changed

- {{CHANGE_1}}

### Fixed

- {{FIX_1}}
- {{FIX_2}}

---

## Entry Guidelines

### Types of Changes

| Type | Description | Example |
|------|-------------|---------|
| **Added** | New features | "Added dark mode support" |
| **Changed** | Changes in existing functionality | "Changed API response format" |
| **Deprecated** | Soon-to-be removed features | "Deprecated v1 API endpoints" |
| **Removed** | Removed features | "Removed legacy auth system" |
| **Fixed** | Bug fixes | "Fixed login redirect loop" |
| **Security** | Vulnerability fixes | "Fixed XSS vulnerability in forms" |

### Writing Good Entries

**Do:**

- Start with a verb (Added, Changed, Fixed)
- Include issue/PR references
- Explain user impact
- Group related changes

**Don't:**

- Include internal refactoring
- Use technical jargon without explanation
- Leave entries vague

### Examples

```markdown
### Added

- Added export to CSV functionality for reports ([#123](url))
- Added keyboard shortcuts for common actions (Ctrl+S to save)

### Fixed

- Fixed memory leak when processing large files ([#456](url))
- Fixed incorrect timezone display for international users
```

---

## Version Links

[Unreleased]: {{REPO_URL}}/compare/v{{LATEST}}...HEAD
[{{VERSION}}]: {{REPO_URL}}/compare/v{{PREVIOUS}}...v{{VERSION}}

---

## Quality Checklist

- [ ] All user-facing changes documented
- [ ] Breaking changes highlighted
- [ ] Issue/PR numbers linked
- [ ] Version number follows SemVer
- [ ] Date in ISO format (YYYY-MM-DD)
- [ ] Entries grouped by type
- [ ] Security fixes prominently noted
