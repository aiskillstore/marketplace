---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: documentation
---

# Changelog Generation

Guide for creating user-facing changelogs from git commits, categorizing changes, and writing clear release notes.

## Changelog Generation Process

### 1. Analyze Git History

**Scan commits from:**

- Specific time period
- Between versions/tags
- Since last release
- Custom date range

**Extract:**

- Commit messages
- Commit authors
- Commit dates
- Changed files
- Commit types (feat, fix, etc.)

### 2. Categorize Changes

**Categories:**

- **Features**: New functionality
- **Improvements**: Enhancements to existing features
- **Bug Fixes**: Bug fixes and corrections
- **Breaking Changes**: Changes that break compatibility
- **Security**: Security updates
- **Deprecations**: Deprecated features
- **Documentation**: Documentation updates
- **Internal**: Refactoring, tests, CI/CD (usually excluded)

### 3. Transform Technical → User-Friendly

**Technical Commit:**

```
fix: resolve null pointer exception in user service
```

**User-Friendly:**

```
Fixed issue where user profiles would fail to load
```

**Transformation Rules:**

- Remove technical jargon
- Focus on user impact
- Use clear, action-oriented language
- Explain what users will notice
- Group related changes

### 4. Format Professionally

**Structure:**

- Clear sections with emojis/icons
- Grouped by category
- Chronological or by importance
- Include dates/version numbers
- Link to related issues/PRs

## Changelog Format

### Standard Format

```markdown
# Changelog

## [Version] - YYYY-MM-DD

### ✨ Added
- New feature descriptions

### 🔧 Changed
- Changes to existing features

### 🐛 Fixed
- Bug fixes

### 🔒 Security
- Security updates

### ⚠️ Breaking Changes
- Breaking changes with migration notes

### 📝 Deprecated
- Deprecated features

### 🗑️ Removed
- Removed features
```

### Example: Weekly Changelog

```markdown
# Updates - Week of March 10, 2024

## ✨ New Features

- **Team Workspaces**: Create separate workspaces for different
  projects. Invite team members and keep everything organized.

- **Keyboard Shortcuts**: Press ? to see all available shortcuts.
  Navigate faster without touching your mouse.

## 🔧 Improvements

- **Faster Sync**: Files now sync 2x faster across devices
- **Better Search**: Search now includes file contents, not just titles
- **Improved Notifications**: Notifications are now grouped and easier to manage

## 🐛 Fixes

- Fixed issue where large images wouldn't upload
- Resolved timezone confusion in scheduled posts
- Corrected notification badge count
- Fixed crash when opening settings on mobile devices

## 🔒 Security

- Updated dependencies to address security vulnerabilities
- Improved password validation requirements
```

### Example: Version Release Notes

```markdown
# Release Notes - Version 2.5.0

**Release Date**: March 15, 2024

## What's New

### Team Collaboration Features

We've added powerful new collaboration features to help teams work together more effectively.

- **Team Workspaces**: Organize your work into separate workspaces for different projects or teams
- **Real-time Collaboration**: See team members' cursors and edits in real-time
- **Comments & Mentions**: Leave comments and mention team members to get their attention

### Performance Improvements

This release includes significant performance improvements:

- **2x Faster Sync**: Files now sync twice as fast across all your devices
- **Improved Search**: Search now includes file contents, making it easier to find what you need
- **Faster Load Times**: Pages load 30% faster on average

## Improvements

- Better notification grouping and management
- Improved mobile experience
- Enhanced keyboard shortcuts (press ? to see all)

## Bug Fixes

- Fixed issue where large images wouldn't upload
- Resolved timezone confusion in scheduled posts
- Corrected notification badge count
- Fixed crash when opening settings on mobile devices

## Breaking Changes

### API Changes

The `/api/v2/users` endpoint now requires authentication for all requests.
Previously, some read operations were public.

**Migration**: Add `Authorization: Bearer <token>` header to all API requests.

## Deprecated

- The legacy import format will be removed in version 3.0. Please migrate to the new format by June 1, 2024.

## Security

- Updated dependencies to address security vulnerabilities
- Improved password validation requirements
- Enhanced encryption for sensitive data

---

**Full Changelog**: [View all commits](https://github.com/example/repo/compare/v2.4.0...v2.5.0)
```

## Commit Message Analysis

### Conventional Commits Format

**Format:**

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance tasks

### Categorization Rules

**Features:**

- Commits with `feat:` type
- New functionality additions
- User-visible new capabilities

**Improvements:**

- Commits with `perf:` type
- Enhancements to existing features
- Performance optimizations
- UX improvements

**Bug Fixes:**

- Commits with `fix:` type
- Bug corrections
- Error handling improvements

**Breaking Changes:**

- Commits with `!` in type (e.g., `feat!:`)
- Footer with `BREAKING CHANGE:`
- API changes
- Configuration changes

**Security:**

- Security-related commits
- Vulnerability fixes
- Security enhancements

## Filtering and Exclusion

### Exclude Internal Commits

**Patterns to Exclude:**

- `refactor:` (unless significant)
- `test:` (unless test framework changes)
- `chore:` (unless user-visible)
- `style:` (formatting only)
- `ci:` (CI/CD changes)
- `build:` (build system changes)

### Include User-Visible Changes

**Always Include:**

- `feat:` (new features)
- `fix:` (bug fixes)
- `perf:` (performance improvements)
- Breaking changes
- Security updates

## Best Practices

### Writing User-Friendly Changelogs

1. **Focus on Impact**: What users will notice
2. **Remove Jargon**: Avoid technical terms
3. **Be Specific**: Clear, concrete descriptions
4. **Group Related**: Group similar changes
5. **Prioritize**: Most important changes first

### Changelog Maintenance

- **Regular Updates**: Update weekly or monthly
- **Version Tags**: Tag releases in git
- **Consistent Format**: Use consistent structure
- **Review Before Publishing**: Review for clarity
- **Link to Details**: Link to full commit history

### Tips

- Run from git repository root
- Specify date ranges for focused changelogs
- Use CHANGELOG_STYLE.md for consistent formatting
- Review and adjust before publishing
- Save output directly to CHANGELOG.md
- Include emojis/icons for visual scanning
- Group by category for easy reading
- Link to related issues/PRs when helpful

## Common Use Cases

### GitHub Release Notes

```markdown
## What's New in v2.5.0

[Changelog content]

**Full Changelog**: https://github.com/example/repo/compare/v2.4.0...v2.5.0
```

### App Store Updates

```markdown
What's New:
- Team workspaces for better organization
- Faster file syncing (2x speed improvement)
- Improved search with file content indexing
- Bug fixes and performance improvements
```

### Email Updates

```markdown
Subject: What's New This Week

Hi [User],

Here's what we've been working on:

✨ New Features
- Team workspaces
- Keyboard shortcuts

🔧 Improvements
- Faster sync
- Better search

🐛 Fixes
- Fixed image upload issues
- Resolved timezone problems

[Call to action]
```
