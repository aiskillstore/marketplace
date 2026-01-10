---
name: sca-blackduck
description: >
  Software Composition Analysis (SCA) using Synopsys Black Duck for identifying open source
  vulnerabilities, license compliance risks, and supply chain security threats with CVE,
  CWE, and OWASP framework mapping. Use when: (1) Scanning dependencies for known
  vulnerabilities and security risks, (2) Analyzing open source license compliance and
  legal risks, (3) Identifying outdated or unmaintained dependencies, (4) Integrating
  SCA into CI/CD pipelines for continuous dependency monitoring, (5) Providing remediation
  guidance for vulnerable dependencies with CVE and CWE mappings, (6) Assessing supply
  chain security risks and third-party component threats.
version: 0.1.0
maintainer: SirAppSec
category: appsec
tags: [sca, blackduck, dependency-scanning, vulnerability-management, license-compliance, supply-chain, cve, owasp]
frameworks: [OWASP, CWE, NIST, SOC2, PCI-DSS]
dependencies:
  tools: [docker, git, detect]
  access: [blackduck-url, api-token]
references:
  - https://sig-product-docs.synopsys.com/bundle/bd-hub/page/Welcome.html
  - https://owasp.org/www-project-dependency-check/
  - https://nvd.nist.gov/
  - https://www.cisa.gov/sbom
---

# Software Composition Analysis with Black Duck

## Overview

Perform comprehensive Software Composition Analysis (SCA) using Synopsys Black Duck to identify
security vulnerabilities, license compliance risks, and supply chain threats in open source
dependencies. This skill provides automated dependency scanning, vulnerability detection with
CVE mapping, license risk analysis, and remediation guidance aligned with OWASP and NIST standards.

## Quick Start

Scan a project for dependency vulnerabilities:

```bash
# Using Black Duck Detect (recommended)
bash <(curl -s -L https://detect.synopsys.com/detect.sh) \
  --blackduck.url=$BLACKDUCK_URL \
  --blackduck.api.token=$BLACKDUCK_TOKEN \
  --detect.project.name="MyProject" \
  --detect.project.version.name="1.0.0"
```

Scan with policy violation enforcement:

```bash
# Fail build on policy violations
bash <(curl -s -L https://detect.synopsys.com/detect.sh) \
  --blackduck.url=$BLACKDUCK_URL \
  --blackduck.api.token=$BLACKDUCK_TOKEN \
  --detect.policy.check.fail.on.severities=BLOCKER,CRITICAL
```

## Core Workflows

### Workflow 1: Initial Dependency Security Assessment

Progress:
[ ] 1. Identify package managers and dependency manifests in codebase
[ ] 2. Run `scripts/blackduck_scan.py` with project detection
[ ] 3. Analyze vulnerability findings categorized by severity (CRITICAL, HIGH, MEDIUM, LOW)
[ ] 4. Map CVE findings to CWE and OWASP Top 10 categories
[ ] 5. Review license compliance risks and policy violations
[ ] 6. Generate prioritized remediation report with upgrade recommendations

Work through each step systematically. Check off completed items.

### Workflow 2: Vulnerability Remediation

1. Review scan results and identify critical/high severity vulnerabilities
2. For each vulnerability:
   - Check if fixed version is available
   - Review breaking changes in upgrade path
   - Consult `references/remediation_strategies.md` for vulnerability-specific guidance
3. Apply dependency updates using package manager
4. Re-scan to validate fixes
5. Document any vulnerabilities accepted as risk with justification

### Workflow 3: License Compliance Analysis

1. Run Black Duck scan with license risk detection enabled
2. Review components flagged with license compliance issues
3. Categorize by risk level:
   - **High Risk**: GPL, AGPL (copyleft licenses)
   - **Medium Risk**: LGPL, MPL (weak copyleft)
   - **Low Risk**: Apache, MIT, BSD (permissive)
4. Consult legal team for high-risk license violations
5. Document license decisions and create policy exceptions if approved

### Workflow 4: CI/CD Integration

1. Add Black Duck Detect to CI/CD pipeline using `assets/ci_integration/`
2. Configure environment variables for Black Duck URL and API token
3. Set policy thresholds (fail on CRITICAL/HIGH vulnerabilities)
4. Enable SBOM generation for supply chain transparency
5. Configure alerts for new vulnerabilities in production dependencies

### Workflow 5: Supply Chain Risk Assessment

1. Identify direct and transitive dependencies
2. Analyze component quality metrics:
   - Maintenance activity (last update, commit frequency)
   - Community health (contributors, issue resolution)
   - Security track record (historical CVEs)
3. Flag high-risk components (unmaintained, few maintainers, security issues)
4. Review alternative components with better security posture
5. Document supply chain risks and mitigation strategies

## Security Considerations

- **Sensitive Data Handling**: Black Duck scans require API tokens with read/write access.
  Store credentials securely in secrets management (Vault, AWS Secrets Manager).
  Never commit tokens to version control.

- **Access Control**: Limit Black Duck access to authorized security and development teams.
  Use role-based access control (RBAC) for scan result visibility and policy management.

- **Audit Logging**: Log all scan executions with timestamps, user, project version, and
  findings count for compliance auditing. Enable Black Duck's built-in audit trail.

- **Compliance**: SCA scanning supports SOC2, PCI-DSS, GDPR, and HIPAA compliance by
  tracking third-party component risks. Generate SBOM for regulatory requirements.

- **Safe Defaults**: Configure policies to fail builds on CRITICAL and HIGH severity
  vulnerabilities. Use allowlists sparingly with documented business justification.

## Supported Package Managers

Black Duck Detect automatically identifies and scans:

- **JavaScript/Node**: npm, yarn, pnpm
- **Python**: pip, pipenv, poetry
- **Java**: Maven, Gradle
- **Ruby**: Bundler, gem
- **.NET**: NuGet
- **Go**: go modules
- **PHP**: Composer
- **Rust**: Cargo
- **C/C++**: Conan, vcpkg
- **Docker**: Container image layers

## Bundled Resources

### Scripts

- `scripts/blackduck_scan.py` - Full-featured scanning with CVE/CWE mapping and reporting
- `scripts/analyze_results.py` - Parse Black Duck results and generate remediation report
- `scripts/sbom_generator.sh` - Generate SBOM (CycloneDX/SPDX) from scan results
- `scripts/policy_checker.py` - Validate compliance with organizational security policies

### References

- `references/cve_cwe_owasp_mapping.md` - CVE to CWE and OWASP Top 10 mapping
- `references/remediation_strategies.md` - Vulnerability remediation patterns and upgrade strategies
- `references/license_risk_guide.md` - License compliance risk assessment and legal guidance
- `references/supply_chain_threats.md` - Common supply chain attack patterns and mitigations

### Assets

- `assets/ci_integration/github_actions.yml` - GitHub Actions workflow for Black Duck scanning
- `assets/ci_integration/gitlab_ci.yml` - GitLab CI configuration for SCA
- `assets/ci_integration/jenkins_pipeline.groovy` - Jenkins pipeline with Black Duck integration
- `assets/policy_templates/` - Pre-configured security and compliance policies
- `assets/blackduck_config.yml` - Recommended Black Duck Detect configuration

## Common Patterns

### Pattern 1: Daily Dependency Security Baseline

```bash
# Run comprehensive scan and generate SBOM
scripts/blackduck_scan.py \
  --project "MyApp" \
  --version "1.0.0" \
  --output results.json \
  --generate-sbom \
  --severity CRITICAL HIGH
```

### Pattern 2: Pull Request Dependency Gate

```bash
# Scan PR changes, fail on new high-severity vulnerabilities
bash <(curl -s -L https://detect.synopsys.com/detect.sh) \
  --blackduck.url=$BLACKDUCK_URL \
  --blackduck.api.token=$BLACKDUCK_TOKEN \
  --detect.policy.check.fail.on.severities=CRITICAL,HIGH \
  --detect.wait.for.results=true
```

### Pattern 3: License Compliance Audit

```bash
# Generate license compliance report
scripts/blackduck_scan.py \
  --project "MyApp" \
  --version "1.0.0" \
  --report-type license \
  --output license-report.pdf
```

### Pattern 4: Vulnerability Research and Triage

```bash
# Extract CVE details and remediation guidance
scripts/analyze_results.py \
  --input scan-results.json \
  --filter-severity CRITICAL HIGH \
  --include-remediation \
  --output vulnerability-report.md
```

### Pattern 5: SBOM Generation for Compliance

```bash
# Generate Software Bill of Materials (CycloneDX format)
scripts/sbom_generator.sh \
  --project "MyApp" \
  --version "1.0.0" \
  --format cyclonedx \
  --output sbom.json
```

## Integration Points

### CI/CD Integration

- **GitHub Actions**: Use `synopsys-sig/detect-action@v1` with policy enforcement
- **GitLab CI**: Run as security scanning job with dependency scanning template
- **Jenkins**: Execute Detect as pipeline step with quality gates
- **Azure DevOps**: Integrate using Black Duck extension from marketplace

See `assets/ci_integration/` for ready-to-use pipeline configurations.

### Security Tool Integration

- **SIEM/SOAR**: Export findings in JSON/CSV for ingestion into Splunk, ELK
- **Vulnerability Management**: Integrate with Jira, ServiceNow, DefectDojo
- **Secret Scanning**: Combine with Gitleaks, TruffleHog for comprehensive security
- **SAST Tools**: Use alongside Semgrep, Bandit for defense-in-depth

### SDLC Integration

- **Requirements Phase**: Define acceptable license and vulnerability policies
- **Development**: IDE plugins provide real-time dependency security feedback
- **Code Review**: Automated dependency review in PR workflow
- **Testing**: Validate security of third-party components
- **Deployment**: Final dependency gate before production release
- **Operations**: Continuous monitoring for new vulnerabilities in production

## Severity Classification

Black Duck classifies vulnerabilities by CVSS score and severity:

- **CRITICAL** (CVSS 9.0-10.0): Remotely exploitable with severe impact (RCE, SQLi)
- **HIGH** (CVSS 7.0-8.9): Significant security risks requiring immediate attention
- **MEDIUM** (CVSS 4.0-6.9): Moderate security weaknesses needing remediation
- **LOW** (CVSS 0.1-3.9): Minor security issues or defense-in-depth improvements
- **NONE** (CVSS 0.0): Informational findings

## Policy Management

### Creating Security Policies

1. Define organizational risk thresholds (e.g., fail on CVSS >= 7.0)
2. Configure license compliance rules using `assets/policy_templates/`
3. Set component usage policies (blocklists for known malicious packages)
4. Enable operational risk policies (unmaintained dependencies, age thresholds)
5. Document policy exceptions with business justification and expiration dates

### Policy Enforcement

```bash
# Enforce custom policy during scan
bash <(curl -s -L https://detect.synopsys.com/detect.sh) \
  --blackduck.url=$BLACKDUCK_URL \
  --blackduck.api.token=$BLACKDUCK_TOKEN \
  --detect.policy.check.fail.on.severities=BLOCKER,CRITICAL \
  --detect.wait.for.results=true
```

## Performance Optimization

For large projects with many dependencies:

```bash
# Use intelligent scan mode (incremental)
bash <(curl -s -L https://detect.synopsys.com/detect.sh) \
  --detect.detector.search.depth=3 \
  --detect.blackduck.signature.scanner.snippet.matching=SNIPPET_MATCHING \
  --detect.parallel.processors=4

# Exclude test and development dependencies
bash <(curl -s -L https://detect.synopsys.com/detect.sh) \
  --detect.excluded.detector.types=PIP,NPM_PACKAGE_LOCK \
  --detect.npm.include.dev.dependencies=false
```

## Troubleshooting

### Issue: Too Many False Positives

**Solution**:
- Review vulnerability applicability (is vulnerable code path used?)
- Use vulnerability suppression with documented justification
- Configure component matching precision in Black Duck settings
- Verify component identification accuracy (check for misidentified packages)

### Issue: License Compliance Violations

**Solution**:
- Review component licenses in Black Duck dashboard
- Consult `references/license_risk_guide.md` for risk assessment
- Replace high-risk licensed components with permissive alternatives
- Obtain legal approval and document policy exceptions

### Issue: Scan Not Detecting Dependencies

**Solution**:
- Verify package manager files are present (package.json, requirements.txt, pom.xml)
- Check Black Duck Detect logs for detector failures
- Ensure dependencies are installed before scanning (run npm install, pip install)
- Use `--detect.detector.search.depth` to increase search depth

### Issue: Slow Scan Performance

**Solution**:
- Use snippet matching instead of full file matching
- Increase `--detect.parallel.processors` for multi-core systems
- Exclude test directories and development dependencies
- Use intelligent/rapid scan mode for faster feedback

## Advanced Usage

### Vulnerability Analysis

For detailed vulnerability research, consult `references/remediation_strategies.md`.

Key remediation strategies:
1. **Upgrade**: Update to fixed version (preferred)
2. **Patch**: Apply security patch if upgrade not feasible
3. **Replace**: Switch to alternative component without vulnerability
4. **Mitigate**: Implement workarounds or compensating controls
5. **Accept**: Document risk acceptance with business justification

### Supply Chain Security

See `references/supply_chain_threats.md` for comprehensive coverage of:
- Dependency confusion attacks
- Typosquatting and malicious packages
- Compromised maintainer accounts
- Backdoored dependencies
- Unmaintained and abandoned projects

### SBOM Generation and Management

Black Duck supports standard SBOM formats:
- **CycloneDX**: Modern, machine-readable format for vulnerability management
- **SPDX**: ISO/IEC standard for software package data exchange

Use SBOMs for:
- Supply chain transparency
- Regulatory compliance (Executive Order 14028)
- Incident response (rapid vulnerability identification)
- M&A due diligence

## Best Practices

1. **Shift Left**: Integrate SCA early in development lifecycle
2. **Policy-Driven**: Define clear policies for vulnerabilities and licenses
3. **Continuous Monitoring**: Run scans on every commit and nightly for production
4. **Remediation Prioritization**: Focus on exploitable vulnerabilities first
5. **SBOM Management**: Maintain up-to-date SBOM for all production applications
6. **Supply Chain Hygiene**: Regularly review dependency health and maintainability
7. **License Compliance**: Establish license approval process before adoption
8. **Defense in Depth**: Combine SCA with SAST, DAST, and security testing

## References

- [Black Duck Documentation](https://sig-product-docs.synopsys.com/bundle/bd-hub/page/Welcome.html)
- [Black Duck Detect](https://sig-product-docs.synopsys.com/bundle/integrations-detect/page/introduction.html)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [National Vulnerability Database](https://nvd.nist.gov/)
- [SBOM Standards (CISA)](https://www.cisa.gov/sbom)
- [CycloneDX SBOM Standard](https://cyclonedx.org/)
- [SPDX License List](https://spdx.org/licenses/)
