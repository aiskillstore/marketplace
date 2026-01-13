---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: dependency-management
---

# Package Manager Reference

Reference guide for different package managers and their commands for dependency management.

## npm (Node.js)

### Dependency Commands

**List dependencies:**

```bash
npm list                    # Show dependency tree
npm list --depth=0          # Show only top-level
npm outdated                # Show outdated packages
```

**Update dependencies:**

```bash
npm update                  # Update all within semver
npm update <package>        # Update specific package
npm install <package>@latest  # Update to latest version
```

**Security:**

```bash
npm audit                   # Check for vulnerabilities
npm audit fix               # Fix vulnerabilities automatically
npm audit fix --force       # Force fixes (may break things)
```

**License checking:**

```bash
npm list --json | jq '.dependencies | to_entries | map({name: .key, license: .value.license})'
```

## pip (Python)

### Dependency Commands

**List dependencies:**

```bash
pip list                    # List installed packages
pip list --outdated         # Show outdated packages
pip show <package>          # Show package info
```

**Update dependencies:**

```bash
pip install --upgrade <package>  # Update specific package
pip install --upgrade -r requirements.txt  # Update from file
```

**Security:**

```bash
pip-audit                   # Check for vulnerabilities
pip-audit --fix             # Fix vulnerabilities
```

**Freeze dependencies:**

```bash
pip freeze > requirements.txt  # Generate requirements file
```

## Poetry (Python)

### Dependency Commands

**List dependencies:**

```bash
poetry show                 # Show installed packages
poetry show --tree          # Show dependency tree
poetry show --outdated      # Show outdated packages
```

**Update dependencies:**

```bash
poetry update               # Update all dependencies
poetry update <package>     # Update specific package
poetry add <package>@latest # Add/update to latest
```

**Security:**

```bash
poetry audit                # Check for vulnerabilities
```

## Maven (Java)

### Dependency Commands

**List dependencies:**

```bash
mvn dependency:tree         # Show dependency tree
mvn versions:display-dependency-updates  # Show outdated
mvn dependency:list         # List all dependencies
```

**Update dependencies:**

```bash
mvn versions:use-latest-versions  # Update to latest
mvn versions:use-latest-releases  # Update to latest releases
```

**Security:**

```bash
mvn org.owasp:dependency-check-maven:check  # OWASP check
```

## Gradle (Java/Kotlin)

### Dependency Commands

**List dependencies:**

```bash
./gradlew dependencies      # Show dependency tree
./gradlew dependencyUpdates # Show outdated dependencies
```

**Update dependencies:**

```bash
./gradlew dependencyUpdates --refresh-dependencies
```

**Security:**

```bash
./gradlew dependencyCheckAnalyze  # OWASP check
```

## Cargo (Rust)

### Dependency Commands

**List dependencies:**

```bash
cargo tree                 # Show dependency tree
cargo outdated             # Show outdated packages
```

**Update dependencies:**

```bash
cargo update                # Update Cargo.lock
cargo update <package>      # Update specific package
```

## Common Patterns

### Checking for Updates

**All package managers:**

- Check for outdated packages regularly
- Review changelogs before updating
- Test updates in development first
- Update incrementally

### Security Scanning

**Tools:**

- npm: npm audit
- pip: pip-audit
- Maven/Gradle: OWASP Dependency Check
- General: Snyk, Dependabot

### License Compliance

**Process:**

1. List all dependencies
2. Check each license
3. Verify compatibility with project license
4. Document license decisions
5. Include license file if required

### Version Pinning Strategies

**Exact versions:**

- Most secure but requires frequent updates
- Use for critical dependencies

**Semver ranges:**

- Balance between security and flexibility
- Use for most dependencies

**Latest:**

- Easiest but least secure
- Use only for development dependencies
