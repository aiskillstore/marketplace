# CHANGELOG Formats Cookbook

Guidelines for writing CHANGELOG entries in different formats.

## Format Detection

Detect the format by examining the existing CHANGELOG.md:

| Pattern | Format |
|---------|--------|
| `## [Unreleased]` + `### Added/Changed/Fixed` | Keep a Changelog |
| `## [version] - date` + conventional sections | Conventional Changelog |
| `# Changelog` + bullet points | Simple |
| GitHub Releases only | Auto-generate from commits |

## Keep a Changelog Format

Based on [keepachangelog.com](https://keepachangelog.com/)

### Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features go here

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed

### Removed
- Features that were removed

### Fixed
- Bug fixes

### Security
- Security-related changes

## [1.0.0] - 2025-01-15

### Added
- Initial release features
```

### Section Guidelines

**Added:** New features
```markdown
### Added
- Add user authentication with OAuth2 support
- Add bulk import endpoint for CSV files
- Add rate limiting middleware
```

**Changed:** Changes to existing features
```markdown
### Changed
- Improve database query performance by 40%
- Update minimum Python version to 3.10
- Change default timeout from 30s to 60s
```

**Deprecated:** Features to be removed
```markdown
### Deprecated
- Deprecate `old_function()` in favor of `new_function()`
- Deprecate XML export format (use JSON instead)
```

**Removed:** Features that were removed
```markdown
### Removed
- Remove Python 3.8 support
- Remove legacy v1 API endpoints
```

**Fixed:** Bug fixes
```markdown
### Fixed
- Fix memory leak in connection pool (#234)
- Fix incorrect timezone handling in date parser
- Fix crash when input is empty
```

**Security:** Security fixes
```markdown
### Security
- Fix XSS vulnerability in user input handling
- Update dependencies with known vulnerabilities
- Add CSRF protection to all endpoints
```

## Conventional Changelog Format

Based on [Conventional Commits](https://www.conventionalcommits.org/)

### Structure

```markdown
# Changelog

## [Unreleased]

### Features

* **auth:** add OAuth2 authentication ([#123](link))
* **api:** add bulk import endpoint ([#124](link))

### Bug Fixes

* **database:** fix connection pool leak ([#125](link))
* **parser:** handle empty input gracefully ([#126](link))

### Performance Improvements

* **query:** optimize database queries ([#127](link))

### BREAKING CHANGES

* **api:** change response format for /users endpoint

## [1.0.0] (2025-01-15)

### Features

* initial release
```

### Entry Format

```
* **scope:** description ([#issue](link))
```

Where:
- `scope` is the affected module/component
- `description` starts lowercase, no period
- Link to PR/issue when available

## Simple Format

For smaller projects:

```markdown
# Changelog

## Unreleased

- Add user authentication
- Fix memory leak in worker pool
- Update dependencies

## 1.0.0 (2025-01-15)

- Initial release
- Basic CRUD operations
- REST API with OpenAPI docs
```

## Writing Good Entries

### Do

- Write from the user's perspective
- Be specific about what changed
- Link to issues/PRs when available
- Group related changes together
- Use consistent verb tense (imperative: "Add", "Fix", "Update")

### Don't

- Include internal implementation details
- Write vague entries ("Various bug fixes")
- Include changes that don't affect users
- Mix different types of changes

### Examples

**Good:**
```markdown
- Add rate limiting with configurable limits per endpoint (#123)
- Fix crash when uploading files larger than 10MB (#124)
- Improve startup time by lazy-loading plugins
```

**Bad:**
```markdown
- Fixed stuff
- Refactored the database module
- Updated some dependencies
- Various improvements
```

## Mapping Commits to Entries

| Commit Message | CHANGELOG Entry |
|----------------|-----------------|
| `feat(auth): add OAuth2 login` | Added: Add OAuth2 login support |
| `fix(api): handle null response` | Fixed: Fix crash on null API response |
| `perf(db): add query caching` | Changed: Improve query performance with caching |
| `BREAKING CHANGE: remove v1 API` | Removed: Remove deprecated v1 API endpoints |
| `docs: update README` | (skip - docs only) |
| `test: add integration tests` | (skip - tests only) |
| `chore: update CI config` | (skip - infrastructure) |

## Release Process

When cutting a release:

1. Move entries from `[Unreleased]` to new version section
2. Add release date
3. Add comparison links at bottom

```markdown
## [Unreleased]
<!-- New changes go here -->

## [1.1.0] - 2025-02-01

### Added
- (entries moved from Unreleased)

## [1.0.0] - 2025-01-15
...

[Unreleased]: https://github.com/user/repo/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/user/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

## Automating CHANGELOG Updates

For projects with consistent commit messages:

```bash
# Generate from conventional commits
npx conventional-changelog -p angular -i CHANGELOG.md -s

# Or with git-cliff
git cliff --unreleased --prepend CHANGELOG.md
```

But always review automated entries for clarity and relevance.
