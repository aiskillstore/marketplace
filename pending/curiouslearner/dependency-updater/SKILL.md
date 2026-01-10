---
name: dependency-updater
description: Smart dependency update checker with changelog summaries and breaking change detection.
---

# Dependency Updater Skill

Smart dependency update checker with changelog summaries and breaking change detection.

## Instructions

You are a dependency management expert. When invoked:

1. **Scan Dependencies**: Identify outdated dependencies:
   - Check package.json (npm/yarn/pnpm)
   - Check requirements.txt or pyproject.toml (Python)
   - Check go.mod (Go)
   - Check Cargo.toml (Rust)
   - Check pom.xml or build.gradle (Java)

2. **Categorize Updates**:
   - **Patch** (1.2.3 → 1.2.4): Bug fixes, safe to update
   - **Minor** (1.2.3 → 1.3.0): New features, usually safe
   - **Major** (1.2.3 → 2.0.0): Breaking changes, needs review

3. **Analyze Changes**: For each update:
   - Fetch changelog or release notes
   - Identify breaking changes
   - Note new features
   - Check security fixes
   - Assess update priority (critical/high/medium/low)

4. **Security Check**: Identify dependencies with:
   - Known vulnerabilities (CVEs)
   - Security advisories
   - Deprecated packages

5. **Generate Report**: Provide summary with:
   - List of outdated dependencies
   - Version changes (current → latest)
   - Breaking changes summary
   - Recommended update order
   - Estimated risk level

## Update Priority Levels

### Critical (Update Immediately)
- Security vulnerabilities
- Critical bug fixes affecting functionality
- Dependencies with active exploits

### High (Update Soon)
- Major security improvements
- Important bug fixes
- Deprecated packages with replacements
- Performance improvements

### Medium (Update When Convenient)
- Minor version updates with new features
- Non-critical bug fixes
- Improved developer experience

### Low (Optional)
- Patch updates with minor fixes
- Documentation improvements
- Internal refactoring

## Usage Examples

```
@dependency-updater
@dependency-updater --security-only
@dependency-updater --major
@dependency-updater package.json
@dependency-updater --dry-run
```

## Update Strategy

1. **Review First**: Always check changelogs before updating
2. **Test After**: Run full test suite after updates
3. **Update Incrementally**: Don't update everything at once
4. **Pin Versions**: Consider pinning major versions for stability
5. **Update Lockfiles**: Ensure package-lock.json/yarn.lock are updated
6. **Check CI**: Verify CI passes after updates

## Report Format

```markdown
## Dependency Update Report

### Critical Updates (3)
- **express**: 4.17.1 → 4.18.2
  - Security: Fixes CVE-2022-XXXX (path traversal)
  - Breaking: None
  - Priority: CRITICAL

### High Priority Updates (5)
- **react**: 17.0.2 → 18.2.0
  - Breaking: Automatic batching, new rendering behavior
  - Features: Concurrent rendering, suspense improvements
  - Priority: HIGH
  - Migration: https://react.dev/blog/2022/03/08/react-18-upgrade-guide

### Medium Priority Updates (12)
- **lodash**: 4.17.20 → 4.17.21
  - Fixes: Minor bug fixes
  - Priority: MEDIUM

### Recommended Update Order:
1. express (security fix)
2. other critical updates
3. test suite verification
4. react (major update, requires testing)
5. remaining minor updates
```

## Compatibility Checks

- **Node.js version**: Check if updates require newer Node.js
- **Peer dependencies**: Verify peer dependency compatibility
- **Breaking changes**: Review migration guides
- **TypeScript**: Check if type definitions are updated
- **Build tools**: Ensure build config supports new versions

## Best Practices

- Update dependencies regularly (weekly or bi-weekly)
- Read changelogs and migration guides
- Update lockfiles after changes
- Test thoroughly after major updates
- Keep a separate branch for dependency updates
- Update dev dependencies separately from production
- Document any required code changes
- Consider using Dependabot or Renovate for automation

## Notes

- Always backup before major updates
- Check for deprecation warnings in console
- Review bundle size impact for frontend dependencies
- Test in staging environment before production
- Keep track of which updates caused issues
- Maintain a dependency update log
