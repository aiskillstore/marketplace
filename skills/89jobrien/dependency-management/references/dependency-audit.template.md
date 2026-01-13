---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: dependency-management
---

# Dependency Audit Report

**Project:** {{PROJECT_NAME}}
**Date:** {{YYYY-MM-DD}}
**Package Manager:** {{NPM|PIP|CARGO|GO}}

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Total Dependencies | {{N}} | - |
| Direct | {{N}} | - |
| Transitive | {{N}} | - |
| Outdated | {{N}} | {{WARN}} |
| Vulnerable | {{N}} | {{CRITICAL}} |
| Deprecated | {{N}} | {{WARN}} |

---

## Security Vulnerabilities

### Critical

| Package | Version | CVE | Description | Fix Version |
|---------|---------|-----|-------------|-------------|
| {{PKG}} | {{VER}} | {{CVE-XXXX}} | {{DESC}} | {{VER}} |

### High

| Package | Version | CVE | Description | Fix Version |
|---------|---------|-----|-------------|-------------|
| {{PKG}} | {{VER}} | {{CVE-XXXX}} | {{DESC}} | {{VER}} |

### Medium/Low

| Package | Severity | CVE | Fix Available |
|---------|----------|-----|---------------|
| {{PKG}} | {{SEV}} | {{CVE}} | {{YES/NO}} |

---

## Outdated Dependencies

### Major Updates Available

| Package | Current | Latest | Breaking Changes |
|---------|---------|--------|------------------|
| {{PKG}} | {{VER}} | {{VER}} | {{YES/NO}} |

### Minor Updates Available

| Package | Current | Latest | Risk |
|---------|---------|--------|------|
| {{PKG}} | {{VER}} | {{VER}} | {{LOW}} |

### Patch Updates Available

| Package | Current | Latest |
|---------|---------|--------|
| {{PKG}} | {{VER}} | {{VER}} |

---

## License Compliance

### License Distribution

| License | Count | Compliant |
|---------|-------|-----------|
| MIT | {{N}} | {{YES}} |
| Apache-2.0 | {{N}} | {{YES}} |
| GPL-3.0 | {{N}} | {{CHECK}} |
| Unknown | {{N}} | {{REVIEW}} |

### Flagged Packages

| Package | License | Issue |
|---------|---------|-------|
| {{PKG}} | {{LICENSE}} | {{ISSUE}} |

---

## Deprecated Packages

| Package | Deprecation Notice | Replacement |
|---------|-------------------|-------------|
| {{PKG}} | {{REASON}} | {{ALTERNATIVE}} |

---

## Unused Dependencies

| Package | Last Used | Safe to Remove |
|---------|-----------|----------------|
| {{PKG}} | {{DATE/NEVER}} | {{YES/NO}} |

---

## Dependency Tree Issues

### Duplicate Versions

| Package | Versions | Locations |
|---------|----------|-----------|
| {{PKG}} | {{V1}}, {{V2}} | {{PATHS}} |

### Circular Dependencies

- {{CYCLE_1}}

### Deep Nesting (>5 levels)

| Package | Depth | Path |
|---------|-------|------|
| {{PKG}} | {{N}} | {{PATH}} |

---

## Recommendations

### Immediate (Security)

1. [ ] Upgrade `{{PKG}}` to `{{VER}}` - fixes {{CVE}}
2. [ ] Upgrade `{{PKG}}` to `{{VER}}` - fixes {{CVE}}

### Short-term (Maintenance)

1. [ ] Remove unused `{{PKG}}`
2. [ ] Replace deprecated `{{PKG}}` with `{{ALT}}`

### Long-term (Health)

1. [ ] Consolidate duplicate versions of `{{PKG}}`
2. [ ] Evaluate alternatives for `{{PKG}}`

---

## Update Commands

```bash
{{UPDATE_COMMANDS}}
```

### Safe Updates (Non-breaking)

```bash
{{SAFE_UPDATE_COMMAND}}
```

### Major Updates (Review Required)

```bash
{{MAJOR_UPDATE_COMMAND}}
```

---

## Audit Commands Used

```bash
{{AUDIT_COMMANDS}}
```

---

## Quality Checklist

- [ ] All critical vulnerabilities addressed
- [ ] License compliance verified
- [ ] Unused dependencies removed
- [ ] Deprecated packages replaced
- [ ] Lock file updated
- [ ] Tests pass after updates
