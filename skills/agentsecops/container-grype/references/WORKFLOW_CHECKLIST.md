# Workflow Checklist Template

This template demonstrates workflow patterns for security operations. Copy and adapt these checklists to your specific skill needs.

## Pattern 1: Sequential Workflow Checklist

Use this pattern for operations that must be completed in order, step-by-step.

### Security Assessment Workflow

Progress:
[ ] 1. Identify application entry points and attack surface
[ ] 2. Map authentication and authorization flows
[ ] 3. Identify data flows and sensitive data handling
[ ] 4. Review existing security controls
[ ] 5. Document findings with framework references (OWASP, CWE)
[ ] 6. Prioritize findings by severity (CVSS scores)
[ ] 7. Generate report with remediation recommendations

Work through each step systematically. Check off completed items.

---

## Pattern 2: Conditional Workflow

Use this pattern when the workflow branches based on findings or conditions.

### Vulnerability Remediation Workflow

1. Identify vulnerability type
   - If SQL Injection → See [sql-injection-remediation.md](sql-injection-remediation.md)
   - If XSS (Cross-Site Scripting) → See [xss-remediation.md](xss-remediation.md)
   - If Authentication flaw → See [auth-remediation.md](auth-remediation.md)
   - If Authorization flaw → See [authz-remediation.md](authz-remediation.md)
   - If Cryptographic issue → See [crypto-remediation.md](crypto-remediation.md)

2. Assess severity using CVSS calculator
   - If CVSS >= 9.0 → Priority: Critical (immediate action)
   - If CVSS 7.0-8.9 → Priority: High (action within 24h)
   - If CVSS 4.0-6.9 → Priority: Medium (action within 1 week)
   - If CVSS < 4.0 → Priority: Low (action within 30 days)

3. Apply appropriate remediation pattern
4. Validate fix with security testing
5. Document changes and update security documentation

---

## Pattern 3: Iterative Workflow

Use this pattern for operations that repeat across multiple targets or items.

### Code Security Review Workflow

For each file in the review scope:
1. Identify security-sensitive operations (auth, data access, crypto, input handling)
2. Check against secure coding patterns for the language
3. Flag potential vulnerabilities with severity rating
4. Map findings to CWE and OWASP categories
5. Suggest specific remediation approaches
6. Document finding with code location and fix priority

Continue until all files in scope have been reviewed.

---

## Pattern 4: Feedback Loop Workflow

Use this pattern when validation and iteration are required.

### Secure Configuration Generation Workflow

1. Generate initial security configuration based on requirements
2. Run validation script: `./scripts/validate_config.py config.yaml`
3. Review validation output:
   - Note all errors (must fix)
   - Note all warnings (should fix)
   - Note all info items (consider)
4. Fix identified issues in configuration
5. Repeat steps 2-4 until validation passes with zero errors
6. Review warnings and determine if they should be addressed
7. Apply configuration once validation is clean

**Validation Loop**: Run validator → Fix errors → Repeat until clean

---

## Pattern 5: Parallel Analysis Workflow

Use this pattern when multiple independent analyses can run concurrently.

### Comprehensive Security Scan Workflow

Run these scans in parallel:

**Static Analysis**:
[ ] 1a. Run SAST scan (Semgrep/Bandit)
[ ] 1b. Run dependency vulnerability scan (Safety/npm audit)
[ ] 1c. Run secrets detection (Gitleaks/TruffleHog)
[ ] 1d. Run license compliance check

**Dynamic Analysis**:
[ ] 2a. Run DAST scan (ZAP/Burp)
[ ] 2b. Run API security testing
[ ] 2c. Run authentication/authorization testing

**Infrastructure Analysis**:
[ ] 3a. Run infrastructure-as-code scan (Checkov/tfsec)
[ ] 3b. Run container image scan (Trivy/Grype)
[ ] 3c. Run configuration review

**Consolidation**:
[ ] 4. Aggregate all findings
[ ] 5. Deduplicate and correlate findings
[ ] 6. Prioritize by risk (CVSS + exploitability + business impact)
[ ] 7. Generate unified security report

---

## Pattern 6: Research and Documentation Workflow

Use this pattern for security research and documentation tasks.

### Threat Modeling Workflow

Research Progress:
[ ] 1. Identify system components and boundaries
[ ] 2. Map data flows between components
[ ] 3. Identify trust boundaries
[ ] 4. Enumerate assets (data, services, credentials)
[ ] 5. Apply STRIDE framework to each component:
     - Spoofing threats
     - Tampering threats
     - Repudiation threats
     - Information disclosure threats
     - Denial of service threats
     - Elevation of privilege threats
[ ] 6. Map threats to MITRE ATT&CK techniques
[ ] 7. Identify existing mitigations
[ ] 8. Document residual risks
[ ] 9. Recommend additional security controls
[ ] 10. Generate threat model document

Work through each step systematically. Check off completed items.

---

## Pattern 7: Compliance Validation Workflow

Use this pattern for compliance checks against security standards.

### Security Compliance Audit Workflow

**SOC 2 Controls Review**:
[ ] 1. Review access control policies (CC6.1, CC6.2, CC6.3)
[ ] 2. Verify logical access controls implementation (CC6.1)
[ ] 3. Review authentication mechanisms (CC6.1)
[ ] 4. Verify encryption implementation (CC6.1, CC6.7)
[ ] 5. Review audit logging configuration (CC7.2)
[ ] 6. Verify security monitoring (CC7.2, CC7.3)
[ ] 7. Review incident response procedures (CC7.3, CC7.4)
[ ] 8. Verify backup and recovery processes (A1.2, A1.3)

**Evidence Collection**:
[ ] 9. Collect policy documents
[ ] 10. Collect configuration screenshots
[ ] 11. Collect audit logs
[ ] 12. Document control gaps
[ ] 13. Generate compliance report

---

## Pattern 8: Incident Response Workflow

Use this pattern for security incident handling.

### Security Incident Response Workflow

**Detection and Analysis**:
[ ] 1. Confirm security incident (rule out false positive)
[ ] 2. Determine incident severity (SEV1/2/3/4)
[ ] 3. Identify affected systems and data
[ ] 4. Preserve evidence (logs, memory dumps, network captures)

**Containment**:
[ ] 5. Isolate affected systems (network segmentation)
[ ] 6. Disable compromised accounts
[ ] 7. Block malicious indicators (IPs, domains, hashes)
[ ] 8. Implement temporary compensating controls

**Eradication**:
[ ] 9. Identify root cause
[ ] 10. Remove malicious artifacts (malware, backdoors, webshells)
[ ] 11. Patch vulnerabilities exploited
[ ] 12. Reset compromised credentials

**Recovery**:
[ ] 13. Restore systems from clean backups (if needed)
[ ] 14. Re-enable systems with monitoring
[ ] 15. Verify system integrity
[ ] 16. Resume normal operations

**Post-Incident**:
[ ] 17. Document incident timeline
[ ] 18. Identify lessons learned
[ ] 19. Update security controls to prevent recurrence
[ ] 20. Update incident response procedures
[ ] 21. Communicate with stakeholders

---

## Usage Guidelines

### When to Use Workflow Checklists

✅ **Use checklists for**:
- Complex multi-step operations
- Operations requiring specific order
- Security assessments and audits
- Incident response procedures
- Compliance validation tasks

❌ **Don't use checklists for**:
- Simple single-step operations
- Highly dynamic exploratory work
- Operations that vary significantly each time

### Adapting This Template

1. **Copy relevant pattern** to your skill's SKILL.md or create new reference file
2. **Customize steps** to match your specific security tool or process
3. **Add framework references** (OWASP, CWE, NIST) where applicable
4. **Include tool-specific commands** for automation
5. **Add decision points** where manual judgment is required

### Checklist Best Practices

- **Be specific**: "Run semgrep --config=auto ." not "Scan the code"
- **Include success criteria**: "Validation passes with 0 errors"
- **Reference standards**: Link to OWASP, CWE, NIST where relevant
- **Show progress**: Checkbox format helps track completion
- **Provide escape hatches**: "If validation fails, see troubleshooting.md"

### Integration with Feedback Loops

Combine checklists with validation scripts for maximum effectiveness:

1. Create checklist for the workflow
2. Provide validation script that checks quality
3. Include "run validator" step in checklist
4. Loop: Complete step → Validate → Fix issues → Re-validate

This pattern dramatically improves output quality through systematic validation.
