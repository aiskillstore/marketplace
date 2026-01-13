# Checkov Suppression and Exception Handling Guide

Best practices for suppressing false positives and managing policy exceptions in Checkov.

## Suppression Methods

### Inline Suppression (Recommended)

#### Terraform

```hcl
# Single check suppression with justification
resource "aws_s3_bucket" "public_site" {
  # checkov:skip=CKV_AWS_18:Public bucket for static website hosting
  bucket = "my-public-website"
  acl    = "public-read"
}

# Multiple checks suppression
resource "aws_security_group" "legacy" {
  # checkov:skip=CKV_AWS_23:Legacy app requires open access
  # checkov:skip=CKV_AWS_24:IPv6 not supported by application
  name = "legacy-sg"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

#### Kubernetes

```yaml
# Annotation-based suppression
apiVersion: v1
kind: Pod
metadata:
  name: legacy-app
  annotations:
    checkov.io/skip: CKV_K8S_16=Legacy application requires elevated privileges
spec:
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      privileged: true
```

#### CloudFormation

```yaml
Resources:
  PublicBucket:
    Type: AWS::S3::Bucket
    Metadata:
      checkov:
        skip:
          - id: CKV_AWS_18
            comment: "Public bucket for CDN origin"
    Properties:
      BucketName: my-public-bucket
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
```

### Configuration File Suppression

#### .checkov.yaml

```yaml
# .checkov.yaml (project root)
skip-check:
  - CKV_AWS_8   # Ensure CloudWatch log groups encrypted
  - CKV_K8S_43  # Image pull policy Always

# Skip specific paths
skip-path:
  - .terraform/
  - node_modules/
  - vendor/

# Severity-based soft fail
soft-fail-on:
  - LOW
  - MEDIUM

# Hard fail on critical/high only
hard-fail-on:
  - CRITICAL
  - HIGH
```

### CLI-Based Suppression

```bash
# Skip specific checks
checkov -d ./terraform --skip-check CKV_AWS_8,CKV_AWS_21

# Skip entire frameworks
checkov -d ./infra --skip-framework secrets

# Skip paths
checkov -d ./terraform --skip-path .terraform/ --skip-path vendor/
```

## Suppression Governance

### Approval Workflow

```yaml
# .github/workflows/checkov-review.yml
name: Review Checkov Suppressions

on:
  pull_request:
    paths:
      - '**.tf'
      - '**.yaml'
      - '**.yml'

jobs:
  check-suppressions:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check for New Suppressions
        run: |
          # Count suppressions in PR
          SUPPRESSIONS=$(git diff origin/main | grep -c "checkov:skip" || true)

          if [ "$SUPPRESSIONS" -gt 0 ]; then
            echo "::warning::PR contains $SUPPRESSIONS new suppression(s)"
            echo "Security team review required"
            # Request review from security team
          fi
```

### Suppression Documentation Template

```hcl
resource "aws_security_group" "example" {
  # checkov:skip=CKV_AWS_23:TICKET-1234 - Business justification here
  # Approved by: security-team@example.com
  # Review date: 2024-01-15
  # Expiration: 2024-06-15 (review quarterly)
  #
  # Compensating controls:
  # - WAF rule blocks malicious traffic
  # - Application-level authentication required
  # - IP allow-listing at load balancer
  # - 24/7 monitoring and alerting

  name = "approved-exception"
  # ... configuration
}
```

## Suppression Best Practices

### 1. Always Provide Justification

```hcl
# ❌ BAD: No justification
resource "aws_s3_bucket" "example" {
  # checkov:skip=CKV_AWS_18
  bucket = "my-bucket"
}

# ✅ GOOD: Clear business justification
resource "aws_s3_bucket" "example" {
  # checkov:skip=CKV_AWS_18:Public bucket required for static website hosting.
  # Content is non-sensitive marketing materials. CloudFront restricts direct access.
  bucket = "marketing-website"
}
```

### 2. Document Compensating Controls

```hcl
resource "aws_security_group" "app" {
  # checkov:skip=CKV_AWS_23:Office IP range access required for developers
  #
  # Compensating controls:
  # 1. IP range limited to corporate /24 subnet (203.0.113.0/24)
  # 2. MFA required for VPN access to corporate network
  # 3. Additional application-level authentication
  # 4. Session timeout of 15 minutes
  # 5. All access logged to SIEM

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["203.0.113.0/24"]
  }
}
```

### 3. Set Expiration Dates

```hcl
resource "aws_instance" "temp" {
  # checkov:skip=CKV_AWS_8:Temporary instance for POC
  # EXPIRES: 2024-03-31
  # After expiration: Remove or apply encryption

  ami           = "ami-12345678"
  instance_type = "t3.micro"
}
```

### 4. Use Granular Suppressions

```hcl
# ❌ BAD: Suppress entire file or directory
# checkov:skip=* (Don't do this!)

# ✅ GOOD: Suppress specific checks on specific resources
resource "aws_s3_bucket" "example" {
  # checkov:skip=CKV_AWS_18:Specific reason for this resource only
  bucket = "specific-bucket"
}
```

## Exception Categories

### Legitimate Exceptions

#### 1. Public Resources by Design

```hcl
resource "aws_s3_bucket" "website" {
  # checkov:skip=CKV_AWS_18:Public bucket for static website
  # checkov:skip=CKV_AWS_93:Public access required by design
  # Content: Marketing materials (non-sensitive)
  # Access: Read-only via CloudFront

  bucket = "company-website"
}
```

#### 2. Legacy System Constraints

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: legacy-app
  annotations:
    checkov.io/skip: CKV_K8S_16=Legacy app built before containers, requires host access
    # Migration plan: TICKET-5678
    # Target date: Q2 2024
spec:
  hostNetwork: true
  containers:
  - name: legacy
    image: legacy-app:1.0
```

#### 3. Development/Testing Environments

```hcl
resource "aws_db_instance" "dev_db" {
  # checkov:skip=CKV_AWS_17:Dev environment - backups not required
  # checkov:skip=CKV_AWS_61:Dev environment - encryption overhead not needed
  # Environment: Non-production only
  # Data: Synthetic test data (no PII/PHI)

  identifier = "dev-database"
  backup_retention_period = 0
  storage_encrypted = false

  tags = {
    Environment = "development"
  }
}
```

### Temporary Exceptions

```hcl
resource "aws_rds_cluster" "temp_unencrypted" {
  # checkov:skip=CKV_AWS_96:Temporary exception during migration
  # TICKET: INFRA-1234
  # EXPIRES: 2024-02-15
  # PLAN: Enable encryption at rest in Phase 2 migration
  # OWNER: platform-team@example.com

  cluster_identifier = "migration-temp"
  storage_encrypted = false
}
```

## Suppression Anti-Patterns

### ❌ Don't: Blanket Suppressions

```yaml
# BAD: Suppress all checks
skip-check:
  - "*"
```

### ❌ Don't: Suppress Without Documentation

```hcl
# BAD: No explanation
resource "aws_s3_bucket" "example" {
  # checkov:skip=CKV_AWS_18
  bucket = "my-bucket"
}
```

### ❌ Don't: Permanent Suppressions for Production

```hcl
# BAD: Permanent suppression of critical security control
resource "aws_rds_cluster" "prod" {
  # checkov:skip=CKV_AWS_96:Too expensive
  # ^ This is unacceptable for production!

  cluster_identifier = "production-db"
  storage_encrypted = false
}
```

### ❌ Don't: Suppress High/Critical Without Review

```hcl
# DANGEROUS: Suppressing critical finding without security review
resource "aws_security_group" "prod" {
  # checkov:skip=CKV_AWS_23:Need access from anywhere
  # ^ Requires security team approval!

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

## Monitoring Suppressions

### Track Suppression Metrics

```bash
# Count suppressions by type
grep -r "checkov:skip" ./terraform | \
  sed 's/.*checkov:skip=\([^:]*\).*/\1/' | \
  sort | uniq -c | sort -rn

# Find suppressions without justification
grep -r "checkov:skip=" ./terraform | \
  grep -v "checkov:skip=.*:.*"
```

### Suppression Audit Report

```python
#!/usr/bin/env python3
"""Generate suppression audit report."""

import re
import sys
from pathlib import Path
from datetime import datetime

def find_suppressions(directory):
    """Find all Checkov suppressions."""
    suppressions = []

    for file_path in Path(directory).rglob('*.tf'):
        with open(file_path) as f:
            content = f.read()

        # Find suppressions
        matches = re.findall(
            r'#\s*checkov:skip=([^:]+):(.*)',
            content
        )

        for check_id, reason in matches:
            suppressions.append({
                'file': str(file_path),
                'check_id': check_id.strip(),
                'reason': reason.strip()
            })

    return suppressions

def generate_report(suppressions):
    """Generate markdown report."""
    print("# Checkov Suppression Audit Report")
    print(f"\nGenerated: {datetime.now().isoformat()}")
    print(f"\nTotal Suppressions: {len(suppressions)}\n")

    print("## Suppressions by Check")
    check_counts = {}
    for s in suppressions:
        check_counts[s['check_id']] = check_counts.get(s['check_id'], 0) + 1

    for check_id, count in sorted(check_counts.items(), key=lambda x: -x[1]):
        print(f"- {check_id}: {count}")

    print("\n## All Suppressions")
    for s in suppressions:
        print(f"\n### {s['file']}")
        print(f"**Check:** {s['check_id']}")
        print(f"**Reason:** {s['reason'] or '(no justification provided)'}")

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else './terraform'
    suppressions = find_suppressions(directory)
    generate_report(suppressions)
```

## Quarterly Review Process

1. **Generate Suppression Report**: List all active suppressions
2. **Review Expirations**: Check for expired temporary suppressions
3. **Validate Justifications**: Ensure reasons still apply
4. **Verify Compensating Controls**: Confirm controls are still in place
5. **Update or Remove**: Update suppressions or fix underlying issues

## Additional Resources

- [Checkov Suppression Documentation](https://www.checkov.io/2.Basics/Suppressing%20and%20Skipping%20Policies.html)
- [Security Exception Management Best Practices](https://owasp.org/www-community/Security_Exception_Management)
