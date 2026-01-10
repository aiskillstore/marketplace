# CISA Known Exploited Vulnerabilities (KEV) Catalog

CISA's Known Exploited Vulnerabilities (KEV) catalog identifies CVEs with confirmed active exploitation in the wild.

## Table of Contents
- [What is KEV](#what-is-kev)
- [Why KEV Matters](#why-kev-matters)
- [KEV in Grype](#kev-in-grype)
- [Remediation Urgency](#remediation-urgency)
- [Federal Requirements](#federal-requirements)

## What is KEV

The Cybersecurity and Infrastructure Security Agency (CISA) maintains a catalog of vulnerabilities that:
1. Have **confirmed active exploitation** in real-world attacks
2. Present **significant risk** to federal enterprise and critical infrastructure
3. Require **prioritized remediation**

**Key Points**:
- KEV listings indicate **active, ongoing exploitation**, not theoretical risk
- Being in KEV catalog means attackers have weaponized the vulnerability
- KEV CVEs should be treated as **highest priority** regardless of CVSS score

## Why KEV Matters

### Active Threat Indicator

**KEV presence means**:
- Exploit code is publicly available or in active use by threat actors
- Attackers are successfully exploiting this vulnerability
- Your organization is likely a target if running vulnerable software

### Prioritization Signal

**CVSS vs KEV**:
- CVSS: Theoretical severity based on technical characteristics
- KEV: Proven real-world exploitation

**Example**:
- CVE with CVSS 6.5 (Medium) but KEV listing → **Prioritize over CVSS 9.0 (Critical) without KEV**
- Active exploitation trumps theoretical severity

### Compliance Requirement

**BOD 22-01**: Federal agencies must remediate KEV vulnerabilities within specified timeframes
- Many commercial organizations adopt similar policies
- SOC2, PCI-DSS, and other frameworks increasingly reference KEV

## KEV in Grype

### Detecting KEV in Scans

Grype includes KEV data in vulnerability assessments:

```bash
# Standard scan includes KEV indicators
grype <image> -o json > results.json

# Check for KEV matches
grep -i "kev" results.json
```

**Grype output indicators**:
- `dataSource` field may include KEV references
- Some vulnerabilities explicitly marked as CISA KEV

### Filtering KEV Vulnerabilities

Use the prioritization script to extract KEV matches:

```bash
./scripts/prioritize_cves.py results.json
```

Output shows `[KEV]` indicator for confirmed KEV vulnerabilities.

### Automated KEV Alerting

Integrate KEV detection into CI/CD:

```bash
# Fail build on any KEV vulnerability
grype <image> -o json | \
  jq '.matches[] | select(.vulnerability.dataSource | contains("KEV"))' | \
  jq -s 'if length > 0 then error("KEV vulnerabilities found") else empty end'
```

## Remediation Urgency

### BOD 22-01 Timeframes

CISA Binding Operational Directive 22-01 requires:

| Vulnerability Type | Remediation Deadline |
|-------------------|---------------------|
| KEV listed before directive | 2 weeks from BOD publication |
| Newly added KEV | 2 weeks from KEV addition |
| Critical KEV (discretionary) | Immediate (24-48 hours) |

### Commercial Best Practices

**Recommended SLAs for KEV vulnerabilities**:

1. **Immediate Response (0-24 hours)**:
   - Assess exposure and affected systems
   - Implement temporary mitigations (disable feature, block network access)
   - Notify security leadership and stakeholders

2. **Emergency Patching (24-48 hours)**:
   - Deploy patches to production systems
   - Validate remediation with re-scan
   - Document patch deployment

3. **Validation and Monitoring (48-72 hours)**:
   - Verify all instances patched
   - Check logs for exploitation attempts
   - Update detection rules and threat intelligence

### Temporary Mitigations

If immediate patching is not possible:

**Network-Level Controls**:
- Block external access to vulnerable services
- Segment vulnerable systems from critical assets
- Deploy Web Application Firewall (WAF) rules

**Application-Level Controls**:
- Disable vulnerable features or endpoints
- Implement additional authentication requirements
- Enable enhanced logging and monitoring

**Operational Controls**:
- Increase security monitoring for affected systems
- Deploy compensating detective controls
- Schedule emergency maintenance window

## Federal Requirements

### Binding Operational Directive 22-01

**Scope**: All federal civilian executive branch (FCEB) agencies

**Requirements**:
1. Remediate KEV vulnerabilities within required timeframes
2. Report remediation status to CISA
3. Document exceptions and compensating controls

**Penalties**: Non-compliance may result in:
- Required reporting to agency leadership
- Escalation to Office of Management and Budget (OMB)
- Potential security authorization impacts

### Extending to Commercial Organizations

Many commercial organizations adopt KEV-based policies:

**Rationale**:
- KEV represents highest-priority threats
- Federal government invests in threat intelligence
- Following KEV reduces actual breach risk

**Implementation**:
- Monitor KEV catalog for relevant CVEs
- Integrate KEV data into vulnerability management
- Define internal KEV remediation SLAs
- Report KEV status to leadership and audit teams

## Monitoring KEV Updates

### CISA KEV Catalog

Access the catalog:
- **Web**: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- **JSON**: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
- **CSV**: https://www.cisa.gov/sites/default/files/csv/known_exploited_vulnerabilities.csv

### Automated Monitoring

Track new KEV additions:

```bash
# Download current KEV catalog
curl -s https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json \
  -o kev-catalog.json

# Compare against previous download
diff kev-catalog-previous.json kev-catalog.json
```

**Subscribe to updates**:
- CISA cybersecurity alerts: https://www.cisa.gov/cybersecurity-alerts
- RSS feeds for KEV additions
- Security vendor threat intelligence feeds

## Response Workflow

### KEV Vulnerability Detected

Progress:
[ ] 1. **Identify** affected systems: Run Grype scan across all environments
[ ] 2. **Assess** exposure: Determine if vulnerable systems are internet-facing or critical
[ ] 3. **Contain** risk: Implement temporary mitigations (network blocks, feature disable)
[ ] 4. **Remediate**: Deploy patches or upgrades to all affected systems
[ ] 5. **Validate**: Re-scan with Grype to confirm vulnerability resolved
[ ] 6. **Monitor**: Review logs for exploitation attempts during vulnerable window
[ ] 7. **Document**: Record timeline, actions taken, and lessons learned

Work through each step systematically. Check off completed items.

### Post-Remediation Analysis

After resolving KEV vulnerability:

1. **Threat Hunting**: Search logs for indicators of compromise (IOC)
2. **Root Cause**: Determine why vulnerable software was deployed
3. **Process Improvement**: Update procedures to prevent recurrence
4. **Reporting**: Notify stakeholders and compliance teams

## References

- [CISA KEV Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [BOD 22-01: Reducing the Significant Risk of Known Exploited Vulnerabilities](https://www.cisa.gov/news-events/directives/bod-22-01-reducing-significant-risk-known-exploited-vulnerabilities)
- [KEV Catalog JSON Feed](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json)
- [CISA Cybersecurity Alerts](https://www.cisa.gov/cybersecurity-alerts)
