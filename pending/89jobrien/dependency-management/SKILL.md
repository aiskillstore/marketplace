---
name: dependency-management
description: Dependency management specialist. Use when updating dependencies, scanning
  for vulnerabilities, analyzing dependency trees, or ensuring license compliance.
  Handles npm, pip, maven, and other package managers.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Dependency Management

This skill manages project dependencies including updates, vulnerability scanning, license compliance, and dependency tree optimization.

## When to Use This Skill

- When updating project dependencies
- When scanning for security vulnerabilities
- When analyzing dependency trees
- When ensuring license compliance
- When resolving version conflicts
- When optimizing dependency usage

## What This Skill Does

1. **Dependency Analysis**: Identifies unused dependencies and version conflicts
2. **Vulnerability Scanning**: Finds and fixes known security vulnerabilities
3. **License Compliance**: Verifies dependency licenses are compatible
4. **Safe Updates**: Updates dependencies with testing and validation
5. **Tree Optimization**: Optimizes dependency trees and reduces bloat
6. **Version Management**: Resolves version conflicts and updates

## Helper Scripts

This skill includes Python helper scripts in `scripts/`:

- **`parse_dependencies.py`**: Parses dependency files (package.json, requirements.txt, pyproject.toml). Outputs JSON with parsed dependencies and metadata.

  ```bash
  python scripts/parse_dependencies.py package.json requirements.txt
  ```

## How to Use

### Manage Dependencies

```
Update all dependencies and check for vulnerabilities
```

```
Scan dependencies for security issues
```

### Specific Tasks

```
Check license compatibility for all dependencies
```

## Management Process

### 1. Analyze Dependencies

**Using Helper Script:**

The skill includes a Python helper script for parsing dependency files:

```bash
# Parse dependency files
python scripts/parse_dependencies.py package.json requirements.txt pyproject.toml
```

**Package Manager Tools:**

- npm: `npm outdated`, `npm list`
- pip: `pip list --outdated`
- maven: `mvn versions:display-dependency-updates`
- gradle: `gradle dependencyUpdates`

### 2. Scan for Vulnerabilities

**Tools:**

- npm: `npm audit`
- pip: `pip-audit`
- maven: OWASP Dependency Check
- gradle: Dependency Check plugin

### 3. Check Licenses

**Process:**

- List all dependency licenses
- Check compatibility with project license
- Identify any incompatible licenses
- Provide license report

### 4. Update Dependencies

**Safe Update Process:**

1. Check for updates
2. Review changelogs
3. Update incrementally
4. Run tests after each update
5. Verify functionality

## Examples

### Example 1: Vulnerability Scan

**Input**: Scan for vulnerabilities

**Output**:

```markdown
## Dependency Vulnerability Scan

### Critical Vulnerabilities

**1. lodash (4.17.20)**
- **Severity**: High
- **Issue**: Prototype Pollution
- **Fix**: Update to 4.17.21
```bash
npm update lodash
```

**2. express (4.16.4)**

- **Severity**: Medium
- **Issue**: Path Traversal
- **Fix**: Update to 4.18.2

```bash
npm update express
```

### Summary

- **Total vulnerabilities**: 5
- **Critical**: 1
- **High**: 2
- **Medium**: 2

```

## Reference Files

For package manager-specific commands and patterns, load reference files as needed:

- **`references/package_managers.md`** - Commands and patterns for npm, pip, Poetry, Maven, Gradle, Cargo, and common dependency management patterns
- **`references/DEPENDENCY_AUDIT.template.md`** - Dependency audit report template with vulnerabilities, outdated packages, license compliance

When working with specific package managers, load `references/package_managers.md` and refer to the relevant package manager section.

## Best Practices

### Dependency Management

1. **Regular Updates**: Update dependencies regularly
2. **Security First**: Prioritize security updates
3. **Test After Updates**: Always test after updating
4. **Lock Files**: Use lock files (package-lock.json, yarn.lock)
5. **Version Pinning**: Pin critical dependencies

## Related Use Cases

- Dependency updates
- Security vulnerability scanning
- License compliance
- Dependency tree optimization
- Version conflict resolution
