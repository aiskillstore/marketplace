# Supply Chain Security Checklist

Based on SLSA and OpenSSF Scorecard frameworks.

## Dependency Management

- [ ] Dependencies pinned to exact versions
- [ ] Lock files committed (package-lock.json, Cargo.lock, etc.)
- [ ] Integrity hashes verified (npm integrity, cargo checksums)
- [ ] Minimal dependency footprint
- [ ] Abandoned/unmaintained deps identified
- [ ] Transitive dependencies audited

## Vulnerability Scanning

- [ ] Automated CVE scanning in CI
- [ ] Dependabot/Renovate configured
- [ ] Critical vuln SLA defined (e.g., 24h for critical)
- [ ] False positive triage process
- [ ] Vulnerability disclosure policy

## Source Integrity

- [ ] Branch protection on main/release branches
- [ ] Required reviews before merge
- [ ] Signed commits encouraged/required
- [ ] Force push disabled on protected branches
- [ ] Delete branch on merge

## Build Integrity (SLSA Levels)

### SLSA Level 1

- [ ] Build process documented
- [ ] Provenance generated (who, what, when)

### SLSA Level 2

- [ ] Build service used (not local machine)
- [ ] Provenance authenticated (signed)

### SLSA Level 3

- [ ] Hardened build platform
- [ ] Non-falsifiable provenance
- [ ] Isolated builds

### SLSA Level 4

- [ ] Two-party review
- [ ] Hermetic builds
- [ ] Reproducible builds

## CI/CD Security

- [ ] Pipeline-as-code (versioned workflow files)
- [ ] Workflow changes require review
- [ ] Secrets in protected contexts only
- [ ] Least privilege for CI runners
- [ ] Self-hosted runner isolation
- [ ] Artifact signing
- [ ] No secrets in logs

## OpenSSF Scorecard Checks

- [ ] Branch-Protection
- [ ] Code-Review
- [ ] Dangerous-Workflow (no script injection)
- [ ] Dependency-Update-Tool
- [ ] Maintained (recent activity)
- [ ] Pinned-Dependencies
- [ ] Security-Policy (SECURITY.md)
- [ ] Signed-Releases
- [ ] Token-Permissions (minimal)
- [ ] Vulnerabilities (no known vulns)

## Release Process

- [ ] Release branches protected
- [ ] Changelog maintained
- [ ] Semantic versioning
- [ ] Signed releases/tags
- [ ] Release artifacts checksummed
- [ ] Provenance attestation published

## Third-Party Code Review

Before adding a dependency:

- [ ] Maintainer reputation
- [ ] Download count / usage
- [ ] Recent commits / active maintenance
- [ ] Security track record
- [ ] License compatibility
- [ ] Scorecard rating

## Incident Response

- [ ] Compromised dependency playbook
- [ ] Ability to quickly patch/replace deps
- [ ] Communication plan for downstream users
- [ ] Rollback capability

## Container/Image Security

- [ ] Base image from trusted source
- [ ] Image scanning enabled
- [ ] Minimal image (distroless/alpine)
- [ ] No secrets baked in
- [ ] Image signing (cosign, Notary)
- [ ] SBOM generated

## Common Supply Chain Attacks

| Attack                  | Mitigation                           |
| ----------------------- | ------------------------------------ |
| Typosquatting           | Verify package names                 |
| Dependency confusion    | Namespace scoping                    |
| Compromised maintainer  | Pin versions, audit updates          |
| Build system compromise | Hermetic builds, provenance          |
| Malicious PR            | Review process, signed commits       |
| CI secret exfiltration  | Minimal permissions, secret rotation |
