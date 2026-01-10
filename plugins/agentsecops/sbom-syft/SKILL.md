---
name: sbom-syft
description: >
  Software Bill of Materials (SBOM) generation using Syft for container images, filesystems, and
  archives. Detects packages across 28+ ecosystems with multi-format output support (CycloneDX,
  SPDX, syft-json). Enables vulnerability assessment, license compliance, and supply chain security.
  Use when: (1) Generating SBOMs for container images or applications, (2) Analyzing software
  dependencies and packages for vulnerability scanning, (3) Tracking license compliance across
  dependencies, (4) Integrating SBOM generation into CI/CD for supply chain security, (5) Creating
  signed SBOM attestations for software provenance.
version: 0.1.0
maintainer: SirAppSec
category: secsdlc
tags: [sbom, syft, supply-chain, dependencies, cyclonedx, spdx, vulnerability-management, license-compliance]
frameworks: [NIST, OWASP]
dependencies:
  tools: [docker]
references:
  - https://github.com/anchore/syft
  - https://anchore.com/sbom/
---

# Syft SBOM Generator

## Overview

Syft is a CLI tool and Go library for generating comprehensive Software Bills of Materials (SBOMs) from container images and filesystems. It provides visibility into packages and dependencies across 28+ ecosystems, supporting multiple SBOM formats (CycloneDX, SPDX) for vulnerability management, license compliance, and supply chain security.

## Supported Ecosystems

**Languages & Package Managers:**
Alpine (apk), C/C++ (conan), Dart (pub), Debian/Ubuntu (dpkg), Dotnet (deps.json), Go (go.mod), Java (JAR/WAR/EAR/Maven/Gradle), JavaScript (npm/yarn), PHP (composer), Python (pip/poetry/setup.py), Red Hat (RPM), Ruby (gem), Rust (cargo), Swift (cocoapods)

**Container & System:**
OCI images, Docker images, Singularity, container layers, Linux distributions

## Quick Start

Generate SBOM for container image:

```bash
# Using Docker
docker run --rm -v $(pwd):/out anchore/syft:latest <image> -o cyclonedx-json=/out/sbom.json

# Local installation
syft <image> -o cyclonedx-json=sbom.json

# Examples
syft alpine:latest -o cyclonedx-json
syft docker.io/nginx:latest -o spdx-json
syft dir:/path/to/project -o cyclonedx-json
```

## Core Workflows

### Workflow 1: Container Image SBOM Generation

For creating SBOMs of container images:

1. Identify target container image (local or registry)
2. Run Syft to generate SBOM:
   ```bash
   syft <image-name:tag> -o cyclonedx-json=sbom-cyclonedx.json
   ```
3. Optionally generate multiple formats:
   ```bash
   syft <image-name:tag> \
     -o cyclonedx-json=sbom-cyclonedx.json \
     -o spdx-json=sbom-spdx.json \
     -o syft-json=sbom-syft.json
   ```
4. Store SBOM artifacts with image for traceability
5. Use SBOM for vulnerability scanning with Grype or other tools
6. Track SBOM versions alongside image releases

### Workflow 2: CI/CD Pipeline Integration

Progress:
[ ] 1. Add Syft to build pipeline after image creation
[ ] 2. Generate SBOM in standard format (CycloneDX or SPDX)
[ ] 3. Store SBOM as build artifact
[ ] 4. Scan SBOM for vulnerabilities (using Grype or similar)
[ ] 5. Fail build on critical vulnerabilities or license violations
[ ] 6. Publish SBOM alongside container image
[ ] 7. Integrate with vulnerability management platform

Work through each step systematically. Check off completed items.

### Workflow 3: Filesystem and Application Scanning

For generating SBOMs from source code or filesystems:

1. Navigate to project root or specify path
2. Scan directory structure:
   ```bash
   syft dir:/path/to/project -o cyclonedx-json=app-sbom.json
   ```
3. Review detected packages and dependencies
4. Validate package detection accuracy (check for false positives/negatives)
5. Configure exclusions if needed (using `.syft.yaml`)
6. Generate SBOM for each release version
7. Track dependency changes between versions

### Workflow 4: SBOM Analysis and Vulnerability Scanning

Combining SBOM generation with vulnerability assessment:

1. Generate SBOM with Syft:
   ```bash
   syft <target> -o cyclonedx-json=sbom.json
   ```
2. Scan SBOM for vulnerabilities using Grype:
   ```bash
   grype sbom:sbom.json -o json --file vulnerabilities.json
   ```
3. Review vulnerability findings by severity
4. Filter by exploitability and fix availability
5. Prioritize remediation based on:
   - CVSS score
   - Active exploitation status
   - Fix availability
   - Dependency depth
6. Update dependencies and regenerate SBOM
7. Re-scan to verify vulnerability remediation

### Workflow 5: Signed SBOM Attestation

For creating cryptographically signed SBOM attestations:

1. Install cosign (for signing):
   ```bash
   # macOS
   brew install cosign

   # Linux
   wget https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64
   chmod +x cosign-linux-amd64
   mv cosign-linux-amd64 /usr/local/bin/cosign
   ```
2. Generate SBOM:
   ```bash
   syft <image> -o cyclonedx-json=sbom.json
   ```
3. Create attestation and sign:
   ```bash
   cosign attest --predicate sbom.json --type cyclonedx <image>
   ```
4. Verify attestation:
   ```bash
   cosign verify-attestation --type cyclonedx <image>
   ```
5. Store signature alongside SBOM for provenance verification

## Output Formats

Syft supports multiple SBOM formats for different use cases:

| Format | Use Case | Specification |
|--------|----------|---------------|
| `cyclonedx-json` | Modern SBOM standard, wide tool support | CycloneDX 1.4+ |
| `cyclonedx-xml` | CycloneDX XML variant | CycloneDX 1.4+ |
| `spdx-json` | Linux Foundation standard | SPDX 2.3 |
| `spdx-tag-value` | SPDX text format | SPDX 2.3 |
| `syft-json` | Syft native format (most detail) | Syft-specific |
| `syft-text` | Human-readable console output | Syft-specific |
| `github-json` | GitHub dependency submission | GitHub-specific |
| `template` | Custom Go template output | User-defined |

Specify with `-o` flag:
```bash
syft <target> -o cyclonedx-json=output.json
```

## Configuration

Create `.syft.yaml` in project root or home directory:

```yaml
# Cataloger configuration
package:
  cataloger:
    enabled: true
    scope: all-layers  # Options: all-layers, squashed

  search:
    unindexed-archives: false
    indexed-archives: true

# Exclusions
exclude:
  - "**/test/**"
  - "**/node_modules/**"
  - "**/.git/**"

# Registry authentication
registry:
  insecure-skip-tls-verify: false
  auth:
    - authority: registry.example.com
      username: user
      password: pass

# Output format defaults
output: cyclonedx-json

# Log level
log:
  level: warn  # Options: error, warn, info, debug, trace
```

## Common Patterns

### Pattern 1: Multi-Architecture Image Scanning

Scan all architectures of multi-platform images:

```bash
# Scan specific architecture
syft --platform linux/amd64 <image> -o cyclonedx-json=sbom-amd64.json
syft --platform linux/arm64 <image> -o cyclonedx-json=sbom-arm64.json

# Or scan manifest list (all architectures)
syft <image> --platform all -o cyclonedx-json
```

### Pattern 2: Private Registry Authentication

Access images from private registries:

```bash
# Using Docker credentials
docker login registry.example.com
syft registry.example.com/private/image:tag -o cyclonedx-json

# Using environment variables
export SYFT_REGISTRY_AUTH_AUTHORITY=registry.example.com
export SYFT_REGISTRY_AUTH_USERNAME=user
export SYFT_REGISTRY_AUTH_PASSWORD=pass
syft registry.example.com/private/image:tag -o cyclonedx-json

# Using config file (recommended)
# Add credentials to .syft.yaml
```

### Pattern 3: OCI Archive Scanning

Scan saved container images (OCI or Docker format):

```bash
# Save image to archive
docker save nginx:latest -o nginx.tar

# Scan archive
syft oci-archive:nginx.tar -o cyclonedx-json=sbom.json

# Or scan Docker archive
syft docker-archive:nginx.tar -o cyclonedx-json=sbom.json
```

### Pattern 4: Comparing SBOMs Between Versions

Track dependency changes across releases:

```bash
# Generate SBOMs for two versions
syft myapp:v1.0 -o syft-json=sbom-v1.0.json
syft myapp:v2.0 -o syft-json=sbom-v2.0.json

# Compare with jq
jq -s '{"added": (.[1].artifacts - .[0].artifacts), "removed": (.[0].artifacts - .[1].artifacts)}' \
  sbom-v1.0.json sbom-v2.0.json
```

### Pattern 5: Filtering SBOM Output

Extract specific package information:

```bash
# Generate detailed SBOM
syft <target> -o syft-json=full-sbom.json

# Extract only Python packages
cat full-sbom.json | jq '.artifacts[] | select(.type == "python")'

# Extract packages with specific licenses
cat full-sbom.json | jq '.artifacts[] | select(.licenses[].value == "MIT")'

# Count packages by ecosystem
cat full-sbom.json | jq '.artifacts | group_by(.type) | map({type: .[0].type, count: length})'
```

## Security Considerations

- **Sensitive Data Handling**: SBOMs may contain internal package names and versions. Store SBOMs securely and restrict access to authorized personnel
- **Access Control**: Limit SBOM generation and access to build systems. Use read-only credentials for registry access
- **Audit Logging**: Log SBOM generation events, distribution, and access for compliance tracking
- **Compliance**: SBOMs support compliance with Executive Order 14028 (Software Supply Chain Security), NIST guidelines, and OWASP recommendations
- **Safe Defaults**: Use signed attestations for production SBOMs to ensure integrity and provenance

## Integration Points

### CI/CD Integration

**GitHub Actions:**
```yaml
- name: Generate SBOM with Syft
  uses: anchore/sbom-action@v0
  with:
    image: ${{ env.IMAGE_NAME }}:${{ github.sha }}
    format: cyclonedx-json
    output-file: sbom.json

- name: Upload SBOM
  uses: actions/upload-artifact@v3
  with:
    name: sbom
    path: sbom.json
```

**GitLab CI:**
```yaml
sbom-generation:
  image: anchore/syft:latest
  script:
    - syft $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -o cyclonedx-json=sbom.json
  artifacts:
    reports:
      cyclonedx: sbom.json
```

**Jenkins:**
```groovy
stage('Generate SBOM') {
  steps {
    sh 'syft ${IMAGE_NAME}:${BUILD_NUMBER} -o cyclonedx-json=sbom.json'
    archiveArtifacts artifacts: 'sbom.json'
  }
}
```

### Vulnerability Scanning

Integrate with Grype for vulnerability scanning:

```bash
# Generate SBOM and scan in one pipeline
syft <target> -o cyclonedx-json=sbom.json
grype sbom:sbom.json
```

### SBOM Distribution

Attach SBOMs to container images:

```bash
# Using ORAS
oras attach <image> --artifact-type application/vnd.cyclonedx+json sbom.json

# Using Docker manifest
# Store SBOM as additional layer or separate artifact
```

## Advanced Usage

### Custom Template Output

Create custom output formats using Go templates:

```bash
# Create template file
cat > custom-template.tmpl <<'EOF'
{{- range .Artifacts}}
{{.Name}}@{{.Version}} ({{.Type}})
{{- end}}
EOF

# Use template
syft <target> -o template -t custom-template.tmpl
```

### Scanning Specific Layers

Analyze specific layers in container images:

```bash
# Squashed view (default - final filesystem state)
syft <image> --scope squashed -o cyclonedx-json

# All layers (every layer's packages)
syft <image> --scope all-layers -o cyclonedx-json
```

### Environment Variable Configuration

Configure Syft via environment variables:

```bash
export SYFT_SCOPE=all-layers
export SYFT_OUTPUT=cyclonedx-json
export SYFT_LOG_LEVEL=debug
export SYFT_EXCLUDE="**/test/**,**/node_modules/**"

syft <target>
```

## Troubleshooting

### Issue: Missing Packages in SBOM

**Solution**: Enable all-layers scope or check for package manager files:
```bash
syft <target> --scope all-layers -o syft-json
```

Verify package manifest files exist (package.json, requirements.txt, go.mod, etc.)

### Issue: Registry Authentication Failure

**Solution**: Ensure Docker credentials are configured or use explicit auth:
```bash
docker login <registry>
# Then run syft
syft <registry>/<image> -o cyclonedx-json
```

### Issue: Large SBOM Size

**Solution**: Use squashed scope and exclude test/dev dependencies:
```yaml
# In .syft.yaml
package:
  cataloger:
    scope: squashed
exclude:
  - "**/test/**"
  - "**/node_modules/**"
  - "**/.git/**"
```

### Issue: Slow Scanning Performance

**Solution**: Disable unindexed archive scanning for faster results:
```yaml
# In .syft.yaml
package:
  search:
    unindexed-archives: false
```

## License Compliance

Extract license information from SBOM:

```bash
# Generate SBOM
syft <target> -o syft-json=sbom.json

# Extract unique licenses
cat sbom.json | jq -r '.artifacts[].licenses[].value' | sort -u

# Find packages with specific licenses
cat sbom.json | jq '.artifacts[] | select(.licenses[].value | contains("GPL"))'

# Generate license report
cat sbom.json | jq -r '.artifacts[] | "\(.name):\(.licenses[].value)"' | sort
```

## Vulnerability Management Workflow

Complete workflow integrating SBOM generation with vulnerability management:

Progress:
[ ] 1. Generate SBOM for application/container
[ ] 2. Scan SBOM for known vulnerabilities
[ ] 3. Classify vulnerabilities by severity and exploitability
[ ] 4. Check for available patches and updates
[ ] 5. Update vulnerable dependencies
[ ] 6. Regenerate SBOM after updates
[ ] 7. Re-scan to confirm vulnerability remediation
[ ] 8. Document accepted risks for unfixable vulnerabilities
[ ] 9. Schedule periodic SBOM regeneration and scanning

Work through each step systematically. Check off completed items.

## References

- [Syft GitHub Repository](https://github.com/anchore/syft)
- [Anchore SBOM Documentation](https://anchore.com/sbom/)
- [CycloneDX Specification](https://cyclonedx.org/)
- [SPDX Specification](https://spdx.dev/)
- [NIST Software Supply Chain Security](https://www.nist.gov/itl/executive-order-improving-nations-cybersecurity/software-supply-chain-security-guidance)
- [OWASP Software Component Verification Standard](https://owasp.org/www-project-software-component-verification-standard/)
