---
name: container-grype
description: >
  Container vulnerability scanning and dependency risk assessment using Grype with CVSS severity
  ratings, EPSS exploit probability, and CISA KEV indicators. Use when: (1) Scanning container
  images and filesystems for known vulnerabilities, (2) Integrating vulnerability scanning into
  CI/CD pipelines with severity thresholds, (3) Analyzing SBOMs (Syft, SPDX, CycloneDX) for
  security risks, (4) Prioritizing remediation based on threat metrics (CVSS, EPSS, KEV),
  (5) Generating vulnerability reports in multiple formats (JSON, SARIF, CycloneDX) for security
  toolchain integration.
version: 0.1.0
maintainer: SirAppSec
category: devsecops
tags: [container-security, vulnerability-scanning, sca, sbom, cvss, cve, docker, grype]
frameworks: [CWE, NIST]
dependencies:
  tools: [grype, docker]
references:
  - https://github.com/anchore/grype
  - https://www.cve.org/
  - https://nvd.nist.gov/
---

# Container Vulnerability Scanning with Grype

## Overview

Grype is an open-source vulnerability scanner that identifies known security flaws in container images,
filesystems, and Software Bill of Materials (SBOM) documents. It analyzes operating system packages
(Alpine, Ubuntu, Red Hat, Debian) and language-specific dependencies (Java, Python, JavaScript, Ruby,
Go, PHP, Rust) against vulnerability databases to detect CVEs.

Grype emphasizes actionable security insights through:
- CVSS severity ratings for risk classification
- EPSS exploit probability scores for threat assessment
- CISA Known Exploited Vulnerabilities (KEV) indicators
- Multiple output formats (table, JSON, SARIF, CycloneDX) for toolchain integration

## Quick Start

Scan a container image:
```bash
grype <image-name>
```

Examples:
```bash
# Scan official Docker image
grype alpine:latest

# Scan local Docker image
grype myapp:v1.2.3

# Scan filesystem directory
grype dir:/path/to/project

# Scan SBOM file
grype sbom:/path/to/sbom.json
```

## Core Workflow

### Basic Vulnerability Scan

1. **Identify scan target**: Determine what to scan (container image, filesystem, SBOM)
2. **Run Grype scan**: Execute `grype <target>` to analyze for vulnerabilities
3. **Review findings**: Examine CVE IDs, severity, CVSS scores, affected packages
4. **Prioritize remediation**: Focus on critical/high severity, CISA KEV, high EPSS scores
5. **Apply fixes**: Update vulnerable packages or base images
6. **Re-scan**: Verify vulnerabilities are resolved

### CI/CD Integration with Fail Thresholds

For automated pipeline security gates:

```bash
# Fail build if any critical vulnerabilities found
grype <image> --fail-on critical

# Fail on high or critical severities
grype <image> --fail-on high

# Output JSON for further processing
grype <image> -o json > results.json
```

**Pipeline integration pattern**:
1. Build container image
2. Run Grype scan with `--fail-on` threshold
3. If scan fails: Block deployment, alert security team
4. If scan passes: Continue deployment workflow
5. Archive scan results as build artifacts

### SBOM-Based Scanning

Use Grype with Syft-generated SBOMs for faster re-scanning:

```bash
# Generate SBOM with Syft (separate skill: sbom-syft)
syft <image> -o json > sbom.json

# Scan SBOM with Grype (faster than re-analyzing image)
grype sbom:sbom.json

# Pipe Syft output directly to Grype
syft <image> -o json | grype
```

**Benefits of SBOM workflow**:
- Faster re-scans without re-analyzing image layers
- Share SBOMs across security tools
- Archive SBOMs for compliance and auditing

### Risk Prioritization Workflow

Progress:
[ ] 1. Run full Grype scan with JSON output: `grype <target> -o json > results.json`
[ ] 2. Use helper script to extract high-risk CVEs: `./scripts/prioritize_cves.py results.json`
[ ] 3. Review CISA KEV matches (actively exploited vulnerabilities)
[ ] 4. Check EPSS scores (exploit probability) for non-KEV findings
[ ] 5. Prioritize remediation: KEV > High EPSS > CVSS Critical > CVSS High
[ ] 6. Document remediation plan with CVE IDs and affected packages
[ ] 7. Apply fixes and re-scan to verify

Work through each step systematically. Check off completed items.

## Output Formats

Grype supports multiple output formats for different use cases:

**Table (default)**: Human-readable console output
```bash
grype <image>
```

**JSON**: Machine-parseable for automation
```bash
grype <image> -o json
```

**SARIF**: Static Analysis Results Interchange Format for IDE integration
```bash
grype <image> -o sarif
```

**CycloneDX**: SBOM format with vulnerability data
```bash
grype <image> -o cyclonedx-json
```

**Template**: Custom output using Go templates
```bash
grype <image> -o template -t custom-template.tmpl
```

## Advanced Configuration

### Filtering and Exclusions

Exclude specific file paths:
```bash
grype <image> --exclude '/usr/share/doc/**'
```

Filter by severity:
```bash
grype <image> --only-fixed  # Only show vulnerabilities with available fixes
```

### Custom Ignore Rules

Create `.grype.yaml` to suppress false positives:

```yaml
ignore:
  # Ignore specific CVE
  - vulnerability: CVE-YYYY-XXXXX
    reason: "False positive - component not used"

  # Ignore CVE for specific package
  - vulnerability: CVE-YYYY-ZZZZZ
    package:
      name: example-lib
      version: 1.2.3
    reason: "Risk accepted - mitigation controls in place"
```

### Database Management

Update vulnerability database:
```bash
grype db update
```

Check database status:
```bash
grype db status
```

Use specific database location:
```bash
grype <image> --db /path/to/database
```

## Security Considerations

- **Sensitive Data Handling**: Scan results may contain package names and versions that reveal
  application architecture. Store results securely and limit access to authorized security personnel.

- **Access Control**: Grype requires Docker socket access when scanning container images.
  Restrict permissions to prevent unauthorized image access.

- **Audit Logging**: Log all Grype scans with timestamps, target details, and operator identity
  for compliance and incident response. Archive scan results for historical vulnerability tracking.

- **Compliance**: Regular vulnerability scanning supports SOC2, PCI-DSS, NIST 800-53, and ISO 27001
  requirements. Document scan frequency and remediation SLAs.

- **Safe Defaults**: Use `--fail-on critical` as minimum threshold for production deployments.
  Configure automated scans in CI/CD to prevent vulnerable images from reaching production.

## Bundled Resources

### Scripts (`scripts/`)

- **prioritize_cves.py** - Parse Grype JSON output and prioritize CVEs by threat metrics (KEV, EPSS, CVSS)
- **grype_scan.sh** - Wrapper script for consistent Grype scans with logging and threshold configuration

### References (`references/`)

- **cvss_guide.md** - CVSS severity rating system and score interpretation
- **cisa_kev.md** - CISA Known Exploited Vulnerabilities catalog and remediation urgency
- **vulnerability_remediation.md** - Common remediation patterns for dependency vulnerabilities

### Assets (`assets/`)

- **grype-ci-config.yml** - CI/CD pipeline configuration for Grype vulnerability scanning
- **grype-config.yaml** - Example Grype configuration with common ignore patterns

## Common Patterns

### Pattern 1: Pre-Production Scanning

Scan before pushing images to registry:

```bash
# Build image
docker build -t myapp:latest .

# Scan locally before push
grype myapp:latest --fail-on critical

# If scan passes, push to registry
docker push myapp:latest
```

### Pattern 2: Scheduled Scanning

Re-scan existing images for newly disclosed vulnerabilities:

```bash
# Scan all production images daily
for image in $(docker images --format '{{.Repository}}:{{.Tag}}' | grep prod); do
  grype $image -o json >> daily-scan-$(date +%Y%m%d).json
done
```

### Pattern 3: Base Image Selection

Compare base images to choose least vulnerable option:

```bash
# Compare Alpine versions
grype alpine:3.18
grype alpine:3.19

# Compare distros
grype ubuntu:22.04
grype debian:12-slim
grype alpine:3.19
```

## Integration Points

- **CI/CD**: Integrate with GitHub Actions, GitLab CI, Jenkins, CircleCI using `--fail-on` thresholds
- **Container Registries**: Scan images from Docker Hub, ECR, GCR, ACR, Harbor
- **Security Tools**: Export SARIF for GitHub Security, JSON for SIEM ingestion, CycloneDX for DependencyTrack
- **SDLC**: Scan during build (shift-left), before deployment (quality gate), and scheduled (continuous monitoring)

## Troubleshooting

### Issue: Database Update Fails

**Symptoms**: `grype db update` fails with network errors

**Solution**:
- Check network connectivity and proxy settings
- Verify firewall allows access to Grype database sources
- Use `grype db update --verbose` for detailed error messages
- Consider using offline database: `grype db import /path/to/database.tar.gz`

### Issue: False Positives

**Symptoms**: Grype reports vulnerabilities in unused code or misidentified packages

**Solution**:
- Create `.grype.yaml` ignore file with specific CVE suppressions
- Document justification for each ignored vulnerability
- Periodically review ignored CVEs (quarterly) to reassess risk
- Use `--only-fixed` to focus on actionable findings

### Issue: Slow Scans

**Symptoms**: Grype scans take excessive time on large images

**Solution**:
- Use SBOM workflow: Generate SBOM once with Syft, re-scan SBOM with Grype
- Exclude unnecessary paths: `--exclude '/usr/share/doc/**'`
- Use local database cache: `grype db update` before batch scans
- Scan base images separately to identify inherited vulnerabilities

## References

- [Grype GitHub Repository](https://github.com/anchore/grype)
- [Grype Documentation](https://github.com/anchore/grype#getting-started)
- [NIST National Vulnerability Database](https://nvd.nist.gov/)
- [CISA Known Exploited Vulnerabilities](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [FIRST EPSS (Exploit Prediction Scoring System)](https://www.first.org/epss/)
- [CVSS Specification](https://www.first.org/cvss/specification-document)
