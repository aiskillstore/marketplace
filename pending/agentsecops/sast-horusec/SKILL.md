---
name: sast-horusec
description: >
  Multi-language static application security testing using Horusec with support for 18+ programming
  languages and 20+ security analysis tools. Performs SAST scans, secret detection in git history,
  and provides vulnerability findings with severity classification. Use when: (1) Analyzing code
  for security vulnerabilities across multiple languages simultaneously, (2) Detecting exposed
  secrets and credentials in git history, (3) Integrating SAST into CI/CD pipelines for secure SDLC,
  (4) Performing comprehensive security analysis during development, (5) Managing false positives
  and prioritizing security findings.
version: 0.1.0
maintainer: asrour
category: secsdlc
tags: [sast, horusec, vulnerability-scanning, multi-language, secrets-detection, static-analysis, secure-sdlc]
frameworks: [OWASP, CWE]
dependencies:
  tools: [docker, git]
references:
  - https://github.com/ZupIT/horusec
  - https://docs.horusec.io/
---

# Horusec SAST Scanner

## Overview

Horusec is an open-source security analysis tool that performs static code analysis across 18+ programming languages using 20+ integrated security tools. It identifies vulnerabilities during development, scans git history for exposed secrets, and integrates seamlessly into CI/CD pipelines for secure SDLC practices.

## Supported Languages

C#, Java, Kotlin, Python, Ruby, Golang, Terraform, JavaScript, TypeScript, Kubernetes, PHP, C, HTML, JSON, Dart, Elixir, Shell, Nginx

## Quick Start

Run Horusec scan on current project:

```bash
# Using Docker (recommended)
docker run -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/src horuszup/horusec-cli:latest horusec start -p /src -P $(pwd)

# Local installation
horusec start -p ./path/to/project
```

## Core Workflows

### Workflow 1: Local Security Scan

For developers performing pre-commit security analysis:

1. Navigate to project directory
2. Run Horusec scan:
   ```bash
   horusec start -p . -o json -O horusec-report.json
   ```
3. Review JSON output for vulnerabilities
4. Filter by severity (HIGH, MEDIUM, LOW, INFO)
5. Address critical and high-severity findings
6. Re-scan to validate fixes

### Workflow 2: CI/CD Pipeline Integration

Progress:
[ ] 1. Add Horusec to CI/CD pipeline configuration
[ ] 2. Configure output format (JSON for automated processing)
[ ] 3. Set severity threshold for build failures
[ ] 4. Run scan on each commit or pull request
[ ] 5. Parse results and fail build on high-severity findings
[ ] 6. Generate security reports for audit trail
[ ] 7. Track remediation progress over time

Work through each step systematically. Check off completed items.

### Workflow 3: Git History Secret Scanning

For detecting exposed credentials and secrets:

1. Run Horusec with git history analysis enabled:
   ```bash
   horusec start -p . --enable-git-history-analysis
   ```
2. Review detected secrets and credentials
3. Rotate compromised credentials immediately
4. Add detected patterns to `.gitignore` and `.horusec/config.json`
5. Use git-filter-branch or BFG Repo-Cleaner to remove from history (if needed)
6. Document incident and update security procedures

### Workflow 4: False Positive Management

When managing scan results and reducing noise:

1. Run initial scan and export results:
   ```bash
   horusec start -p . -o json -O results.json
   ```
2. Review findings and identify false positives
3. Create or update `.horusec/config.json` with ignore rules:
   ```json
   {
     "horusecCliRiskAcceptHashes": ["hash1", "hash2"],
     "horusecCliFilesOrPathsToIgnore": ["**/test/**", "**/vendor/**"]
   }
   ```
4. Re-run scan to verify false positives are suppressed
5. Document risk acceptance decisions for compliance
6. Periodically review ignored findings

## Configuration

Create `.horusec/config.json` in project root for custom configuration:

```json
{
  "horusecCliCertInsecureSkipVerify": false,
  "horusecCliCertPath": "",
  "horusecCliContainerBindProjectPath": "",
  "horusecCliCustomImages": {},
  "horusecCliCustomRulesPath": "",
  "horusecCliDisableDocker": false,
  "horusecCliFalsePositiveHashes": [],
  "horusecCliFilesOrPathsToIgnore": [
    "**/node_modules/**",
    "**/vendor/**",
    "**/*_test.go",
    "**/test/**"
  ],
  "horusecCliHeaders": {},
  "horusecCliHorusecApiUri": "",
  "horusecCliJsonOutputFilePath": "./horusec-report.json",
  "horusecCliLogFilePath": "./horusec.log",
  "horusecCliMonitorRetryInSeconds": 15,
  "horusecCliPrintOutputType": "text",
  "horusecCliProjectPath": ".",
  "horusecCliRepositoryAuthorization": "",
  "horusecCliRepositoryName": "",
  "horusecCliReturnErrorIfFoundVulnerability": false,
  "horusecCliRiskAcceptHashes": [],
  "horusecCliTimeoutInSecondsAnalysis": 600,
  "horusecCliTimeoutInSecondsRequest": 300,
  "horusecCliToolsConfig": {},
  "horusecCliWorkDir": ".horusec"
}
```

## Output Formats

Horusec supports multiple output formats for different use cases:

- `text` - Human-readable console output (default)
- `json` - Structured JSON for CI/CD integration
- `sonarqube` - SonarQube-compatible format

Specify with `-o` flag:
```bash
horusec start -p . -o json -O report.json
```

## Common Patterns

### Pattern 1: Fail Build on High Severity

Configure CI/CD to fail on critical findings:

```bash
horusec start -p . \
  --return-error-if-found-vulnerability \
  --severity-threshold="MEDIUM"
```

Exit code will be non-zero if vulnerabilities at or above threshold are found.

### Pattern 2: Multi-Project Monorepo Scanning

Scan multiple projects in monorepo structure:

```bash
# Scan specific subdirectories
for project in service1 service2 service3; do
  horusec start -p ./$project -o json -O horusec-$project.json
done
```

### Pattern 3: Custom Rules Integration

Add custom security rules:

1. Create custom rules file (YAML format)
2. Configure path in `.horusec/config.json`:
   ```json
   {
     "horusecCliCustomRulesPath": "./custom-rules.yaml"
   }
   ```
3. Run scan with custom rules applied

## Security Considerations

- **Sensitive Data Handling**: Horusec scans for exposed secrets. Ensure scan results are stored securely and access is restricted to authorized personnel only
- **Access Control**: Limit access to Horusec configuration files and scan results. Use read-only mounts in Docker for source code scanning
- **Audit Logging**: Log all scan executions, findings, and risk acceptance decisions for compliance auditing
- **Compliance**: Integrates with SOC2, PCI-DSS, and GDPR compliance by identifying vulnerabilities and tracking remediation
- **Safe Defaults**: Configure severity thresholds appropriate for your risk tolerance. Start with MEDIUM or HIGH to reduce noise

## Integration Points

### CI/CD Integration

**GitHub Actions:**
```yaml
- name: Run Horusec Security Scan
  run: |
    docker run -v /var/run/docker.sock:/var/run/docker.sock \
      -v $(pwd):/src horuszup/horusec-cli:latest \
      horusec start -p /src -o json -O horusec-report.json \
      --return-error-if-found-vulnerability
```

**GitLab CI:**
```yaml
horusec-scan:
  image: horuszup/horusec-cli:latest
  script:
    - horusec start -p . -o json -O horusec-report.json
  artifacts:
    reports:
      horusec: horusec-report.json
```

**Jenkins:**
```groovy
stage('Security Scan') {
  steps {
    sh 'docker run -v $(pwd):/src horuszup/horusec-cli:latest horusec start -p /src'
  }
}
```

### VS Code Extension

Horusec provides a VS Code extension for real-time security analysis during development. Install from VS Code marketplace.

### Vulnerability Management

Horusec can integrate with centralized vulnerability management platforms via:
- JSON output parsing
- Horusec Platform (separate web-based management tool)
- Custom integrations using API

## Troubleshooting

### Issue: Docker Socket Permission Denied

**Solution**: Ensure Docker socket has proper permissions:
```bash
sudo chmod 666 /var/run/docker.sock
# Or run with sudo (not recommended for CI/CD)
```

### Issue: False Positives in Test Files

**Solution**: Exclude test directories in configuration:
```json
{
  "horusecCliFilesOrPathsToIgnore": ["**/test/**", "**/*_test.go", "**/tests/**"]
}
```

### Issue: Scan Timeout on Large Repositories

**Solution**: Increase timeout values in configuration:
```json
{
  "horusecCliTimeoutInSecondsAnalysis": 1200,
  "horusecCliTimeoutInSecondsRequest": 600
}
```

### Issue: Missing Vulnerabilities for Specific Language

**Solution**: Verify language is supported and Docker images are available:
```bash
horusec version --check-for-updates
docker pull horuszup/horusec-cli:latest
```

## Advanced Usage

### Running Without Docker

Install Horusec CLI directly (requires all security tool dependencies):

```bash
# macOS
brew install horusec

# Linux
curl -fsSL https://raw.githubusercontent.com/ZupIT/horusec/main/deployments/scripts/install.sh | bash

# Windows
# Download from GitHub releases
```

Then run:
```bash
horusec start -p . --disable-docker
```

**Note**: Running without Docker requires manual installation of all security analysis tools (Bandit, Brakeman, GoSec, etc.)

### Severity Filtering

Filter results by severity in output:

```bash
# Only show HIGH and CRITICAL
horusec start -p . --severity-threshold="HIGH"

# Show all findings
horusec start -p . --severity-threshold="INFO"
```

### Custom Docker Images

Override default security tool images in configuration:

```json
{
  "horusecCliCustomImages": {
    "python": "my-registry/custom-bandit:latest",
    "go": "my-registry/custom-gosec:latest"
  }
}
```

## Report Analysis

Parse JSON output for automated processing:

```bash
# Extract high-severity findings
cat horusec-report.json | jq '.analysisVulnerabilities[] | select(.severity == "HIGH")'

# Count vulnerabilities by language
cat horusec-report.json | jq '.analysisVulnerabilities | group_by(.language) | map({language: .[0].language, count: length})'

# List unique CWE IDs
cat horusec-report.json | jq '[.analysisVulnerabilities[].securityTool] | unique'
```

## References

- [Horusec GitHub Repository](https://github.com/ZupIT/horusec)
- [Horusec Documentation](https://docs.horusec.io/)
- [OWASP Top 10](https://owasp.org/Top10/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)
