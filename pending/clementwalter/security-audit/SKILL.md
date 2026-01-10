# Security Researcher

Senior-grade security review guidelines anchored on canonical control frameworks: NIST CSF 2.0, CIS Controls v8, NIST SSDF, OWASP ASVS, OWASP Top 10, MITRE ATT&CK, SLSA, and OpenSSF Scorecard.

## When to Use

- Security review or audit of code, architecture, or infrastructure
- Threat modeling sessions
- Reviewing PRs for security implications
- Assessing supply chain security
- Smart contract or ZK circuit security reviews

## Frameworks Reference

| Framework            | Purpose                       |
| -------------------- | ----------------------------- |
| NIST CSF 2.0         | Org-wide risk outcomes        |
| CIS Controls v8      | Practical enterprise controls |
| NIST SSDF SP 800-218 | Secure development lifecycle  |
| OWASP ASVS           | App security requirements     |
| OWASP Top 10 (2025)  | Common web app failures       |
| MITRE ATT&CK         | Adversary techniques mapping  |
| SLSA + OpenSSF       | Supply chain integrity        |

## Non-Negotiables

Before any deep review, verify these fundamentals:

1. **Asset inventory** - Systems, repos, secrets locations, dependencies, owners
2. **MFA everywhere** - Hardware keys for admins, no shared accounts
3. **Patch management** - Continuous vuln scanning (OS, containers, deps)
4. **Centralized logging** - Auth, privilege changes, egress, CI/CD, key access
5. **Tested backups** - Restore drills, immutable where possible
6. **Incident response** - Runbooks, on-call, break-glass procedures

## Review Methodology

### 1. Threat Model First

Use STRIDE categories:

- **S**poofing - Can attacker impersonate?
- **T**ampering - Can data be modified?
- **R**epudiation - Can actions be denied?
- **I**nformation disclosure - Data leaks?
- **D**enial of service - Availability attacks?
- **E**levation of privilege - Unauthorized access?

Document for each trust boundary:

- Auth strategy
- Data classification
- Rate limits
- Audit requirements

**Assume compromise review:**

- If one service key leaks, what's the blast radius?
- If one dependency is malicious, what stops it?

### 2. Identity & Access (Root Cause #1)

Broken access control is the most common vulnerability.

Check:

- Default-deny authorization (by resource, not just endpoint)
- Short-lived sessions, secure cookies, CSRF protection
- Separation: authentication ≠ authorization ≠ accounting
- Step-up auth for high-risk actions
- RBAC/ABAC with explicit admin boundaries

Protect against:

- Credential stuffing (rate limits, breached password checks)
- Account takeover (MFA, risky-login alerts)
- Session fixation/replay (rotation, binding, nonce/jti)

### 3. Secrets & Keys

- **No secrets in git** - Pre-receive hooks, CI secret detectors
- **Dedicated KMS/HSM** - Least privilege, rotate keys
- **Environment separation** - Dev/stage/prod with separate creds
- **Short-lived credentials** - OIDC to cloud, not static keys
- **Track usage** - Who/what accessed, from where, when
- **Compromise playbook** - Rotate, revoke, invalidate, postmortem

### 4. Cryptography

- Use modern primitives (AEAD, not raw AES modes)
- Never roll your own crypto
- CSPRNG for randomness (no time-based seeds)
- Unique nonces where required
- Constant-time ops for secret-dependent paths
- Domain separation for hashes
- Passwords: argon2/bcrypt/scrypt, per-user salt

### 5. Input Handling & Injection

- Strict allowlists, schema validation at boundaries
- Parameterized queries (no string concatenation)
- Contextual output encoding (HTML/JS/URL)
- SSRF prevention: egress allowlists, metadata IP blocks
- Deserialization: avoid unsafe deserializers, type allowlists
- File uploads: content-type defense, store outside web root

### 6. Infrastructure

- Asset inventory + secure baseline (golden images)
- Patch SLAs with emergency path
- Network segmentation (prod ≠ CI/CD ≠ corp)
- mTLS for service-to-service
- Rate limits, quotas, circuit breakers
- No public admin panels (VPN + MFA + IP allowlists)

### 7. CI/CD & Supply Chain

Protect the build pipeline like prod:

- Least privilege runners
- Secrets only in protected contexts
- Reviews for workflow changes

Dependencies:

- Pin versions, verify integrity, monitor CVEs
- Remove abandoned libs

Supply chain:

- Signed build provenance
- OpenSSF Scorecard checks
- SLSA levels adoption

### 8. Detection & Response

Log with context:

- Auth events, privilege changes, key access
- Config changes, CI/CD events, unusual egress

Protect logs:

- Append-only/immutable, restricted access

Alerting:

- Brute force, impossible travel, new admin grants
- Anomalous token use

Readiness:

- Tabletop exercises, forensic snapshots, kill switches
- Post-incident RCA, patch bug classes

### 9. Verification

- Code review with security checklists
- SAST + dependency + secret scanning in CI
- DAST for critical surfaces
- Fuzzers on parsers, codecs, serialization
- Abuse case testing (rate limits, replay, permission boundaries)
- External audits for high-risk components
- Bug bounty when mature

## Blockchain/Smart Contract Specifics

### Protocol & Contracts

- **Invariant-first design** - Define safety properties, check continuously
- **Upgradeability** - Timelocks, emergency pause, clear admin key story
- **Oracle/bridge threats** - Assume counterpart compromise, minimize trust
- **Economic attacks** - MEV, sandwiching, griefing, liquidity manipulation
- **Replay protection** - Chain-id, contract address, nonce, EIP-712
- **Key custody** - Multisig, HSM, threshold signing

### ZK Circuits/Provers

- **Soundness** - Constraints fully bind witness, no unchecked values
- **Transcript binding** - All public inputs in Fiat-Shamir transcript
- **Range/overflow** - Explicit range constraints, no wrap assumptions
- **Challenges** - Derive from transcript, never external mutable sources
- **Trusted setup** - Ceremony hygiene, reproducible parameters
- **Side-channels** - Constant-time for secrets, isolate prover infra

## Operationalization

1. **Pick baselines**: CIS v8 + NIST SSDF + OWASP ASVS
2. **Map to ATT&CK**: What you can't detect, redesign
3. **Supply chain**: SLSA + Scorecard for repos
4. **Loop**: Threat model → Controls → Test → Monitor → Drills

## Output Format

When conducting a review, structure findings as:

```text
## Finding: [Title]
**Severity**: Critical / High / Medium / Low / Info
**Category**: [STRIDE category or framework reference]
**Location**: [File:line or component]

### Description
[What's wrong]

### Impact
[What could happen]

### Recommendation
[How to fix]

### References
[Framework links, CVE, etc.]
```

See `references/` for detailed checklists by domain.
