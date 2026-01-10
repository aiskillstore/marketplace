---
name: webapp-nikto
description: >
  Web server vulnerability scanner for identifying security issues, misconfigurations, and outdated
  software versions. Use when: (1) Conducting authorized web server security assessments, (2)
  Identifying common web vulnerabilities and misconfigurations, (3) Detecting outdated server
  software and known vulnerabilities, (4) Performing compliance scans for web server hardening,
  (5) Enumerating web server information and enabled features, (6) Validating security controls
  and patch levels.
version: 0.1.0
maintainer: sirappsec@gmail.com
category: offsec
tags: [web-security, vulnerability-scanner, nikto, server-security, web-assessment]
frameworks: [OWASP, CWE, NIST]
dependencies:
  packages: [nikto]
  tools: [perl]
references:
  - https://cirt.net/Nikto2
  - https://github.com/sullo/nikto
  - https://owasp.org/www-project-web-security-testing-guide/
---

# Nikto Web Server Scanner

## Overview

Nikto is an open-source web server scanner that performs comprehensive tests against web servers for multiple security issues including dangerous files, outdated software versions, and server misconfigurations. This skill covers authorized security assessments of web servers and applications.

**IMPORTANT**: Nikto generates significant traffic and is easily detected. Only use with proper written authorization on systems you own or have explicit permission to test.

## Quick Start

Basic web server scanning:

```bash
# Scan single host
nikto -h http://example.com

# Scan with SSL
nikto -h https://example.com

# Scan specific port
nikto -h example.com -p 8080

# Scan multiple ports
nikto -h example.com -p 80,443,8080
```

## Core Workflow

### Web Server Assessment Workflow

Progress:
[ ] 1. Verify authorization for web server testing
[ ] 2. Identify target web servers and ports
[ ] 3. Perform initial reconnaissance scan
[ ] 4. Run comprehensive vulnerability assessment
[ ] 5. Analyze and categorize findings
[ ] 6. Document vulnerabilities with remediation
[ ] 7. Generate and deliver security report
[ ] 8. Verify no testing artifacts remain

Work through each step systematically. Check off completed items.

### 1. Authorization Verification

**CRITICAL**: Before any web server scanning:
- Confirm written authorization from web server owner
- Verify scope includes web server vulnerability assessment
- Understand acceptable scanning windows
- Document emergency contact procedures
- Confirm no production impact restrictions

### 2. Basic Scanning

Perform basic web server scans:

```bash
# Standard scan
nikto -h http://example.com

# Scan with specific User-Agent
nikto -h http://example.com -useragent "Mozilla/5.0..."

# Scan through proxy
nikto -h http://example.com -useproxy http://proxy:8080

# Scan with authentication
nikto -h http://example.com -id username:password

# SSL/TLS scan
nikto -h https://example.com -ssl

# Force SSL even on non-standard ports
nikto -h example.com -p 8443 -ssl
```

### 3. Advanced Scanning Options

Customize scan behavior:

```bash
# Specify tuning options
nikto -h http://example.com -Tuning 123bde

# Enable all checks (very comprehensive)
nikto -h http://example.com -Tuning x

# Scan multiple hosts from file
nikto -h hosts.txt

# Limit to specific checks
nikto -h http://example.com -Plugins "apache_expect_xss"

# Update plugin database
nikto -update

# Display available plugins
nikto -list-plugins
```

**Tuning Options**:
- **0**: File Upload
- **1**: Interesting File/Seen in logs
- **2**: Misconfiguration/Default File
- **3**: Information Disclosure
- **4**: Injection (XSS/Script/HTML)
- **5**: Remote File Retrieval (Inside Web Root)
- **6**: Denial of Service
- **7**: Remote File Retrieval (Server Wide)
- **8**: Command Execution/Remote Shell
- **9**: SQL Injection
- **a**: Authentication Bypass
- **b**: Software Identification
- **c**: Remote Source Inclusion
- **d**: WebService
- **e**: Administrative Console
- **x**: Reverse Tuning (exclude specified)

### 4. Output and Reporting

Generate scan reports:

```bash
# Output to text file
nikto -h http://example.com -o results.txt

# Output to HTML report
nikto -h http://example.com -o results.html -Format html

# Output to CSV
nikto -h http://example.com -o results.csv -Format csv

# Output to XML
nikto -h http://example.com -o results.xml -Format xml

# Multiple output formats
nikto -h http://example.com -o results.txt -Format txt -o results.html -Format html
```

### 5. Performance Tuning

Optimize scan performance:

```bash
# Increase timeout (default 10 seconds)
nikto -h http://example.com -timeout 20

# Limit maximum execution time
nikto -h http://example.com -maxtime 30m

# Use specific HTTP version
nikto -h http://example.com -vhost example.com

# Follow redirects
nikto -h http://example.com -followredirects

# Disable 404 guessing
nikto -h http://example.com -no404

# Pause between tests
nikto -h http://example.com -Pause 2
```

### 6. Evasion and Stealth

Evade detection (authorized testing only):

```bash
# Use random User-Agent strings
nikto -h http://example.com -useragent random

# Inject random data in requests
nikto -h http://example.com -evasion 1

# Use IDS evasion techniques
nikto -h http://example.com -evasion 12345678

# Pause between requests
nikto -h http://example.com -Pause 5

# Use session cookies
nikto -h http://example.com -cookies "session=abc123"
```

**Evasion Techniques**:
- **1**: Random URI encoding
- **2**: Directory self-reference (/./)
- **3**: Premature URL ending
- **4**: Prepend long random string
- **5**: Fake parameter
- **6**: TAB as request spacer
- **7**: Change case of URL
- **8**: Use Windows directory separator (\)

## Security Considerations

### Authorization & Legal Compliance

- **Written Permission**: Obtain explicit authorization for web server scanning
- **Scope Verification**: Only scan explicitly authorized hosts and ports
- **Detection Risk**: Nikto is noisy and will trigger IDS/IPS alerts
- **Production Impact**: Scans may impact server performance
- **Log Flooding**: Nikto generates extensive log entries

### Operational Security

- **Rate Limiting**: Use -Pause to reduce server load
- **Scan Windows**: Perform scans during approved maintenance windows
- **Session Management**: Use -maxtime to limit scan duration
- **Proxy Usage**: Route through authorized proxy if required
- **User-Agent**: Consider using custom User-Agent for tracking

### Audit Logging

Document all Nikto scanning activities:
- Target hosts and ports scanned
- Scan start and end timestamps
- Tuning options and plugins used
- Findings and vulnerability counts
- False positives identified
- Remediation priorities
- Report delivery and recipients

### Compliance

- **OWASP ASVS**: V14 Configuration Verification
- **NIST SP 800-115**: Technical Guide to Information Security Testing
- **PCI-DSS**: 6.6 and 11.3 - Vulnerability scanning
- **CWE**: Common Weakness Enumeration mapping
- **ISO 27001**: A.12.6 - Technical vulnerability management

## Common Patterns

### Pattern 1: External Perimeter Assessment

```bash
# Scan external web servers
for host in web1.example.com web2.example.com; do
  nikto -h https://$host -o nikto_${host}.html -Format html
done

# Scan common web ports
nikto -h example.com -p 80,443,8080,8443 -o external_scan.txt
```

### Pattern 2: Internal Web Application Assessment

```bash
# Comprehensive internal scan
nikto -h http://intranet.local \
  -Tuning 123456789abcde \
  -timeout 30 \
  -maxtime 2h \
  -o internal_assessment.html -Format html
```

### Pattern 3: SSL/TLS Security Assessment

```bash
# SSL-specific testing
nikto -h https://example.com \
  -Plugins "ssl" \
  -ssl \
  -o ssl_assessment.txt
```

### Pattern 4: Authenticated Scanning

```bash
# Scan with authentication
nikto -h http://example.com \
  -id admin:password \
  -cookies "sessionid=abc123" \
  -Tuning 123456789 \
  -o authenticated_scan.html -Format html
```

### Pattern 5: Bulk Scanning

```bash
# Create host file
cat > web_servers.txt <<EOF
http://web1.example.com
https://web2.example.com:8443
http://web3.example.com:8080
EOF

# Scan all hosts
nikto -h web_servers.txt -o bulk_scan.csv -Format csv
```

## Integration Points

### CI/CD Integration

```bash
#!/bin/bash
# ci_nikto_scan.sh - Automated web security scanning

TARGET_URL="$1"
OUTPUT_DIR="nikto_results/$(date +%Y%m%d_%H%M%S)"

mkdir -p "$OUTPUT_DIR"

# Run Nikto scan
nikto -h "$TARGET_URL" \
  -Tuning 123456789 \
  -maxtime 30m \
  -o "$OUTPUT_DIR/nikto_report.xml" -Format xml

# Check for critical findings
if grep -i "OSVDB" "$OUTPUT_DIR/nikto_report.xml"; then
  echo "CRITICAL: Vulnerabilities detected!"
  exit 1
fi

echo "Scan completed successfully"
exit 0
```

### SIEM Integration

```bash
# Export findings to JSON for SIEM
nikto -h http://example.com -o findings.xml -Format xml

# Parse XML to JSON (requires xmlstarlet or similar)
xmlstarlet sel -t -m "//item" -v "concat(@id,',',description,','
,uri)" -n findings.xml > findings.csv
```

## Troubleshooting

### Issue: Scan Takes Too Long

**Solutions**:
```bash
# Limit scan duration
nikto -h http://example.com -maxtime 15m

# Reduce tuning scope
nikto -h http://example.com -Tuning 123

# Disable 404 checking
nikto -h http://example.com -no404
```

### Issue: SSL/TLS Errors

**Solutions**:
```bash
# Force SSL
nikto -h example.com -ssl -p 443

# Ignore SSL certificate errors
nikto -h https://example.com -ssl -nossl

# Specify SSL version
nikto -h https://example.com -ssl
```

### Issue: Too Many False Positives

**Solutions**:
- Manually verify findings
- Use -Tuning to focus on specific vulnerability types
- Review and update Nikto database with -update
- Exclude known false positives from reports

### Issue: WAF Blocking Scans

**Solutions**:
```bash
# Use evasion techniques
nikto -h http://example.com -evasion 1234567

# Add delays
nikto -h http://example.com -Pause 10

# Use custom User-Agent
nikto -h http://example.com -useragent "legitimate-browser-string"
```

## Defensive Considerations

Protect web servers against Nikto scanning:

**Web Application Firewall Rules**:
- Detect and block Nikto User-Agent strings
- Implement rate limiting
- Block known Nikto attack patterns
- Monitor for scan signatures

**Server Hardening**:
- Remove default files and directories
- Disable directory listing
- Remove server version banners
- Apply security patches regularly
- Follow CIS benchmarks for web server hardening

**Detection and Monitoring**:
- Monitor for rapid sequential requests
- Alert on multiple 404 errors from single source
- Detect common vulnerability probes
- Log and correlate scan patterns
- Implement honeypot files/directories

Common Nikto detection signatures:
- User-Agent contains "Nikto"
- Requests to known vulnerable paths
- Sequential URI enumeration
- Specific HTTP header patterns

## References

- [Nikto Official Documentation](https://cirt.net/Nikto2)
- [Nikto GitHub Repository](https://github.com/sullo/nikto)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [NIST SP 800-115: Technical Security Testing](https://csrc.nist.gov/publications/detail/sp/800-115/final)
- [CIS Web Server Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
