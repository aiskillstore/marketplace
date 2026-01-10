# Checkov Compliance Framework Mapping

Mapping of Checkov checks to CIS, PCI-DSS, HIPAA, SOC2, NIST, and GDPR compliance requirements.

## CIS Benchmarks

### CIS AWS Foundations Benchmark v1.4

| Check ID | CIS Control | Description | Severity |
|----------|-------------|-------------|----------|
| CKV_AWS_19 | 2.1.1 | Ensure S3 bucket encryption at rest | HIGH |
| CKV_AWS_21 | 2.1.3 | Ensure S3 bucket versioning enabled | MEDIUM |
| CKV_AWS_18 | 2.1.5 | Ensure S3 bucket access logging | MEDIUM |
| CKV_AWS_23 | 4.1 | Security group ingress not 0.0.0.0/0 | HIGH |
| CKV_AWS_24 | 4.2 | Security group ingress not ::/0 | HIGH |
| CKV_AWS_40 | 1.16 | IAM policies no wildcard actions | HIGH |
| CKV_AWS_61 | 2.3.1 | RDS encryption at rest enabled | HIGH |
| CKV_AWS_16 | 2.3.1 | RDS storage encrypted | HIGH |
| CKV_AWS_17 | 2.3.2 | RDS backup retention period | MEDIUM |
| CKV_AWS_7 | 2.9 | EBS encryption by default | HIGH |
| CKV_AWS_93 | 2.4.1 | S3 bucket public access blocked | CRITICAL |

### CIS Kubernetes Benchmark v1.6

| Check ID | CIS Control | Description | Severity |
|----------|-------------|-------------|----------|
| CKV_K8S_16 | 5.2.1 | Container not privileged | HIGH |
| CKV_K8S_22 | 5.2.6 | Read-only root filesystem | HIGH |
| CKV_K8S_28 | 5.2.7 | Minimize capabilities | HIGH |
| CKV_K8S_10 | 5.2.13 | CPU requests configured | MEDIUM |
| CKV_K8S_11 | 5.2.13 | CPU limits configured | MEDIUM |
| CKV_K8S_12 | 5.2.14 | Memory requests configured | MEDIUM |
| CKV_K8S_13 | 5.2.14 | Memory limits configured | MEDIUM |
| CKV_K8S_8 | 5.2.15 | Liveness probe configured | MEDIUM |
| CKV_K8S_9 | 5.2.15 | Readiness probe configured | MEDIUM |

## PCI-DSS v3.2.1

### Requirement 2: Do not use vendor-supplied defaults

| Check ID | PCI Requirement | Description |
|----------|-----------------|-------------|
| CKV_AWS_41 | 2.1 | EKS encryption enabled |
| CKV_AWS_58 | 2.2 | EKS public access restricted |
| CKV_K8S_14 | 2.3 | Image tag not :latest |

### Requirement 3: Protect stored cardholder data

| Check ID | PCI Requirement | Description |
|----------|-----------------|-------------|
| CKV_AWS_19 | 3.4 | S3 bucket encrypted |
| CKV_AWS_61 | 3.4 | RDS encrypted at rest |
| CKV_AWS_7 | 3.4 | EBS encryption enabled |
| CKV_AWS_89 | 3.4 | DynamoDB encryption |

### Requirement 6: Develop and maintain secure systems

| Check ID | PCI Requirement | Description |
|----------|-----------------|-------------|
| CKV_AWS_23 | 6.2 | Security groups not open |
| CKV_AWS_40 | 6.5 | IAM no wildcard permissions |
| CKV_K8S_16 | 6.5 | No privileged containers |

### Requirement 10: Track and monitor all access

| Check ID | PCI Requirement | Description |
|----------|-----------------|-------------|
| CKV_AWS_18 | 10.2 | S3 access logging enabled |
| CKV_AWS_51 | 10.3 | ECR image scanning |
| CKV_AWS_46 | 10.5 | ECS task logging |

## HIPAA Security Rule

### Administrative Safeguards (§164.308)

| Check ID | HIPAA Control | Description |
|----------|---------------|-------------|
| CKV_AWS_40 | §164.308(a)(3) | IAM access controls |
| CKV_AWS_49 | §164.308(a)(4) | CloudTrail logging |
| CKV_AWS_38 | §164.308(a)(5) | EKS RBAC enabled |

### Physical Safeguards (§164.310)

| Check ID | HIPAA Control | Description |
|----------|---------------|-------------|
| CKV_AWS_19 | §164.310(d)(1) | Encryption at rest (S3) |
| CKV_AWS_7 | §164.310(d)(1) | Encryption at rest (EBS) |
| CKV_AWS_61 | §164.310(d)(1) | Encryption at rest (RDS) |

### Technical Safeguards (§164.312)

| Check ID | HIPAA Control | Description |
|----------|---------------|-------------|
| CKV_AWS_23 | §164.312(a)(1) | Access control (network) |
| CKV_AWS_18 | §164.312(b) | Audit logging (S3) |
| CKV_AWS_27 | §164.312(c)(1) | SQS encryption |
| CKV_AWS_20 | §164.312(e)(1) | S3 SSL/TLS enforced |

## SOC 2 Trust Service Criteria

### CC6.1: Logical and Physical Access Controls

| Check ID | TSC | Description |
|----------|-----|-------------|
| CKV_AWS_40 | CC6.1 | IAM least privilege |
| CKV_AWS_23 | CC6.1 | Network segmentation |
| CKV_K8S_21 | CC6.1 | Namespace defined |

### CC6.6: Encryption

| Check ID | TSC | Description |
|----------|-----|-------------|
| CKV_AWS_19 | CC6.6 | S3 encryption |
| CKV_AWS_7 | CC6.6 | EBS encryption |
| CKV_AWS_61 | CC6.6 | RDS encryption |
| CKV_AWS_20 | CC6.6 | S3 SSL enforced |

### CC7.2: System Monitoring

| Check ID | TSC | Description |
|----------|-----|-------------|
| CKV_AWS_18 | CC7.2 | S3 access logging |
| CKV_AWS_49 | CC7.2 | CloudTrail enabled |
| CKV_K8S_8 | CC7.2 | Liveness probe |

## NIST 800-53 Rev 5

### AC (Access Control)

| Check ID | NIST Control | Description |
|----------|--------------|-------------|
| CKV_AWS_40 | AC-3 | IAM least privilege |
| CKV_AWS_23 | AC-4 | Network access control |
| CKV_K8S_16 | AC-6 | Least privilege (containers) |

### AU (Audit and Accountability)

| Check ID | NIST Control | Description |
|----------|--------------|-------------|
| CKV_AWS_18 | AU-2 | S3 access logging |
| CKV_AWS_49 | AU-12 | CloudTrail logging |
| CKV_K8S_35 | AU-9 | Audit log protection |

### SC (System and Communications Protection)

| Check ID | NIST Control | Description |
|----------|--------------|-------------|
| CKV_AWS_19 | SC-28 | Encryption at rest (S3) |
| CKV_AWS_20 | SC-8 | Encryption in transit (S3) |
| CKV_AWS_7 | SC-28 | Encryption at rest (EBS) |

## GDPR

### Article 32: Security of Processing

| Check ID | GDPR Article | Description |
|----------|--------------|-------------|
| CKV_AWS_19 | Art. 32(1)(a) | Encryption of personal data |
| CKV_AWS_7 | Art. 32(1)(a) | EBS encryption |
| CKV_AWS_61 | Art. 32(1)(a) | RDS encryption |
| CKV_AWS_21 | Art. 32(1)(b) | Data backup (S3 versioning) |
| CKV_AWS_18 | Art. 32(1)(d) | Access logging |

### Article 25: Data Protection by Design

| Check ID | GDPR Article | Description |
|----------|--------------|-------------|
| CKV_AWS_93 | Art. 25 | S3 public access block |
| CKV_AWS_23 | Art. 25 | Network isolation |
| CKV_AWS_20 | Art. 25 | Secure transmission |

## Usage Examples

### Scan for CIS Compliance

```bash
# CIS AWS Benchmark
checkov -d ./terraform --check CIS_AWS

# CIS Azure Benchmark
checkov -d ./terraform --check CIS_AZURE

# CIS Kubernetes Benchmark
checkov -d ./k8s --framework kubernetes --check CIS_KUBERNETES
```

### Scan for PCI-DSS Compliance

```bash
# Focus on encryption requirements (Req 3.4)
checkov -d ./terraform \
  --check CKV_AWS_19,CKV_AWS_61,CKV_AWS_7,CKV_AWS_89

# Network security (Req 1, 2)
checkov -d ./terraform \
  --check CKV_AWS_23,CKV_AWS_24,CKV_AWS_40
```

### Scan for HIPAA Compliance

```bash
# HIPAA-focused scan
checkov -d ./terraform \
  --check CKV_AWS_19,CKV_AWS_7,CKV_AWS_61,CKV_AWS_20,CKV_AWS_18,CKV_AWS_40
```

### Generate Compliance Report

```bash
# Comprehensive compliance report
checkov -d ./terraform \
  -o json --output-file-path ./compliance-report \
  --repo-id healthcare-infra \
  --check CIS_AWS,PCI_DSS,HIPAA
```

## Compliance Matrix

| Framework | Checkov Support | Common Checks | Report Format |
|-----------|-----------------|---------------|---------------|
| CIS AWS | ✓ Full | 100+ checks | JSON, CLI, SARIF |
| CIS Azure | ✓ Full | 80+ checks | JSON, CLI, SARIF |
| CIS Kubernetes | ✓ Full | 50+ checks | JSON, CLI, SARIF |
| PCI-DSS 3.2.1 | ✓ Partial | 30+ checks | JSON, CLI |
| HIPAA | ✓ Partial | 40+ checks | JSON, CLI |
| SOC 2 | ✓ Partial | 35+ checks | JSON, CLI |
| NIST 800-53 | ✓ Mapping | 60+ checks | JSON, CLI |
| GDPR | ✓ Mapping | 25+ checks | JSON, CLI |

## Additional Resources

- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [PCI Security Standards](https://www.pcisecuritystandards.org/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [AICPA SOC 2](https://www.aicpa.org/soc4so)
- [NIST 800-53](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [GDPR Portal](https://gdpr.eu/)
