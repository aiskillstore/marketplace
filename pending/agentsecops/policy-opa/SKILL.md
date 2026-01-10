---
name: policy-opa
description: >
  Policy-as-code enforcement and compliance validation using Open Policy Agent (OPA).
  Use when: (1) Enforcing security and compliance policies across infrastructure and applications,
  (2) Validating Kubernetes admission control policies, (3) Implementing policy-as-code for
  compliance frameworks (SOC2, PCI-DSS, GDPR, HIPAA), (4) Testing and evaluating OPA Rego policies,
  (5) Integrating policy checks into CI/CD pipelines, (6) Auditing configuration drift against
  organizational security standards, (7) Implementing least-privilege access controls.
version: 0.1.0
maintainer: SirAppSec
category: compliance
tags: [opa, policy-as-code, compliance, rego, kubernetes, admission-control, soc2, gdpr, pci-dss, hipaa]
frameworks: [SOC2, PCI-DSS, GDPR, HIPAA, NIST, ISO27001]
dependencies:
  tools: [opa, docker, kubectl]
  packages: [jq, yq]
references:
  - https://www.openpolicyagent.org/docs/latest/
  - https://www.openpolicyagent.org/docs/latest/policy-language/
  - https://www.conftest.dev/
---

# Policy-as-Code with Open Policy Agent

## Overview

This skill enables policy-as-code enforcement using Open Policy Agent (OPA) for compliance validation, security policy enforcement, and configuration auditing. OPA provides a unified framework for policy evaluation across cloud-native environments, Kubernetes, CI/CD pipelines, and infrastructure-as-code.

Use OPA to codify security requirements, compliance controls, and organizational standards as executable policies written in Rego. Automatically validate configurations, prevent misconfigurations, and maintain continuous compliance.

## Quick Start

### Install OPA

```bash
# macOS
brew install opa

# Linux
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa

# Verify installation
opa version
```

### Basic Policy Evaluation

```bash
# Evaluate a policy against input data
opa eval --data policy.rego --input input.json 'data.example.allow'

# Test policies with unit tests
opa test policy.rego policy_test.rego --verbose

# Run OPA server for live policy evaluation
opa run --server --addr localhost:8181
```

## Core Workflow

### Step 1: Define Policy Requirements

Identify compliance requirements and security controls to enforce:
- Compliance frameworks (SOC2, PCI-DSS, GDPR, HIPAA, NIST)
- Kubernetes security policies (pod security, RBAC, network policies)
- Infrastructure-as-code policies (Terraform, CloudFormation)
- Application security policies (API authorization, data access)
- Organizational security standards

### Step 2: Write OPA Rego Policies

Create policy files in Rego language. Use the provided templates in `assets/` for common patterns:

**Example: Kubernetes Pod Security Policy**
```rego
package kubernetes.admission

import future.keywords.contains
import future.keywords.if

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged == true
    msg := sprintf("Privileged containers are not allowed: %v", [container.name])
}

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("Container must run as non-root: %v", [container.name])
}
```

**Example: Compliance Control Validation (SOC2)**
```rego
package compliance.soc2

import future.keywords.if

# CC6.1: Logical and physical access controls
deny[msg] {
    input.kind == "Deployment"
    not input.spec.template.metadata.labels["data-classification"]
    msg := "SOC2 CC6.1: All deployments must have data-classification label"
}

# CC6.6: Encryption in transit
deny[msg] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    not input.metadata.annotations["service.beta.kubernetes.io/aws-load-balancer-ssl-cert"]
    msg := "SOC2 CC6.6: LoadBalancer services must use SSL/TLS encryption"
}
```

### Step 3: Test Policies with Unit Tests

Write comprehensive tests for policy validation:

```rego
package kubernetes.admission_test

import data.kubernetes.admission

test_deny_privileged_container {
    input := {
        "request": {
            "kind": {"kind": "Pod"},
            "object": {
                "spec": {
                    "containers": [{
                        "name": "nginx",
                        "securityContext": {"privileged": true}
                    }]
                }
            }
        }
    }
    count(admission.deny) > 0
}

test_allow_unprivileged_container {
    input := {
        "request": {
            "kind": {"kind": "Pod"},
            "object": {
                "spec": {
                    "containers": [{
                        "name": "nginx",
                        "securityContext": {"privileged": false, "runAsNonRoot": true}
                    }]
                }
            }
        }
    }
    count(admission.deny) == 0
}
```

Run tests:
```bash
opa test . --verbose
```

### Step 4: Evaluate Policies Against Configuration

Use the bundled evaluation script for policy validation:

```bash
# Evaluate single file
./scripts/evaluate_policy.py --policy policies/ --input config.yaml

# Evaluate directory of configurations
./scripts/evaluate_policy.py --policy policies/ --input configs/ --recursive

# Output results in JSON format for CI/CD integration
./scripts/evaluate_policy.py --policy policies/ --input config.yaml --format json
```

Or use OPA directly:
```bash
# Evaluate with formatted output
opa eval --data policies/ --input config.yaml --format pretty 'data.compliance.violations'

# Bundle evaluation for complex policies
opa eval --bundle policies.tar.gz --input config.yaml 'data'
```

### Step 5: Integrate with CI/CD Pipelines

Add policy validation to your CI/CD workflow:

**GitHub Actions Example:**
```yaml
- name: Validate Policies
  uses: open-policy-agent/setup-opa@v2
  with:
    version: latest

- name: Run Policy Tests
  run: opa test policies/ --verbose

- name: Evaluate Configuration
  run: |
    opa eval --data policies/ --input deployments/ \
      --format pretty 'data.compliance.violations' > violations.json

    if [ $(jq 'length' violations.json) -gt 0 ]; then
      echo "Policy violations detected!"
      cat violations.json
      exit 1
    fi
```

**GitLab CI Example:**
```yaml
policy-validation:
  image: openpolicyagent/opa:latest
  script:
    - opa test policies/ --verbose
    - opa eval --data policies/ --input configs/ --format pretty 'data.compliance.violations'
  artifacts:
    reports:
      junit: test-results.xml
```

### Step 6: Deploy as Kubernetes Admission Controller

Enforce policies at cluster level using OPA Gatekeeper:

```bash
# Install OPA Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml

# Apply constraint template
kubectl apply -f assets/k8s-constraint-template.yaml

# Apply constraint
kubectl apply -f assets/k8s-constraint.yaml

# Test admission control
kubectl apply -f test-pod.yaml  # Should be denied if violates policy
```

### Step 7: Monitor Policy Compliance

Generate compliance reports using the bundled reporting script:

```bash
# Generate compliance report
./scripts/generate_report.py --policy policies/ --audit-logs audit.json --output compliance-report.html

# Export violations for SIEM integration
./scripts/generate_report.py --policy policies/ --audit-logs audit.json --format json --output violations.json
```

## Security Considerations

- **Policy Versioning**: Store policies in version control with change tracking and approval workflows
- **Least Privilege**: Grant minimal permissions for policy evaluation - OPA should run with read-only access to configurations
- **Sensitive Data**: Avoid embedding secrets in policies - use external data sources or encrypted configs
- **Audit Logging**: Log all policy evaluations, violations, and exceptions for compliance auditing
- **Policy Testing**: Maintain comprehensive test coverage (>80%) for all policy rules
- **Separation of Duties**: Separate policy authors from policy enforcers; require peer review for policy changes
- **Compliance Mapping**: Map policies to specific compliance controls (SOC2 CC6.1, PCI-DSS 8.2.1) for audit traceability

## Bundled Resources

### Scripts (`scripts/`)

- `evaluate_policy.py` - Evaluate OPA policies against configuration files with formatted output
- `generate_report.py` - Generate compliance reports from policy evaluation results
- `test_policies.sh` - Run OPA policy unit tests with coverage reporting

### References (`references/`)

- `rego-patterns.md` - Common Rego patterns for security and compliance policies
- `compliance-frameworks.md` - Policy templates mapped to SOC2, PCI-DSS, GDPR, HIPAA controls
- `kubernetes-security.md` - Kubernetes security policies and admission control patterns
- `iac-policies.md` - Infrastructure-as-code policy validation for Terraform, CloudFormation

### Assets (`assets/`)

- `k8s-pod-security.rego` - Kubernetes pod security policy template
- `k8s-constraint-template.yaml` - OPA Gatekeeper constraint template
- `k8s-constraint.yaml` - Example Gatekeeper constraint configuration
- `soc2-compliance.rego` - SOC2 compliance controls as OPA policies
- `pci-dss-compliance.rego` - PCI-DSS requirements as OPA policies
- `gdpr-compliance.rego` - GDPR data protection policies
- `terraform-security.rego` - Terraform security best practices policies
- `ci-cd-pipeline.yaml` - CI/CD integration examples (GitHub Actions, GitLab CI)

## Common Patterns

### Pattern 1: Kubernetes Admission Control

Enforce security policies at pod creation time:
```rego
package kubernetes.admission

deny[msg] {
    input.request.kind.kind == "Pod"
    not input.request.object.spec.securityContext.runAsNonRoot
    msg := "Pods must run as non-root user"
}
```

### Pattern 2: Infrastructure-as-Code Validation

Validate Terraform configurations before apply:
```rego
package terraform.security

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not resource.change.after.server_side_encryption_configuration
    msg := sprintf("S3 bucket %v must have encryption enabled", [resource.name])
}
```

### Pattern 3: Compliance Framework Mapping

Map policies to specific compliance controls:
```rego
package compliance.soc2

# SOC2 CC6.1: Logical and physical access controls
cc6_1_violations[msg] {
    input.kind == "RoleBinding"
    input.roleRef.name == "cluster-admin"
    msg := sprintf("SOC2 CC6.1 VIOLATION: cluster-admin binding for %v", [input.metadata.name])
}
```

### Pattern 4: Data Classification Enforcement

Enforce data handling policies based on classification:
```rego
package data.classification

deny[msg] {
    input.metadata.labels["data-classification"] == "restricted"
    input.spec.template.spec.volumes[_].hostPath
    msg := "Restricted data cannot use hostPath volumes"
}
```

### Pattern 5: API Authorization Policies

Implement attribute-based access control (ABAC):
```rego
package api.authz

import future.keywords.if

allow if {
    input.method == "GET"
    input.path[0] == "public"
}

allow if {
    input.method == "GET"
    input.user.role == "admin"
}

allow if {
    input.method == "POST"
    input.user.role == "editor"
    input.resource.owner == input.user.id
}
```

## Integration Points

- **CI/CD Pipelines**: GitHub Actions, GitLab CI, Jenkins, CircleCI - validate policies before deployment
- **Kubernetes**: OPA Gatekeeper admission controller for runtime policy enforcement
- **Terraform/IaC**: Pre-deployment validation using `conftest` or OPA CLI
- **API Gateways**: Kong, Envoy, NGINX - authorize requests using OPA policies
- **Monitoring/SIEM**: Export policy violations to Splunk, ELK, Datadog for security monitoring
- **Compliance Tools**: Integrate with compliance platforms for control validation and audit trails

## Troubleshooting

### Issue: Policy Evaluation Returns Unexpected Results

**Solution**:
- Enable trace mode: `opa eval --data policy.rego --input input.json --explain full 'data.example.allow'`
- Validate input data structure matches policy expectations
- Check for typos in policy rules or variable names
- Use `opa fmt` to format policies and catch syntax errors

### Issue: Kubernetes Admission Control Not Blocking Violations

**Solution**:
- Verify Gatekeeper is running: `kubectl get pods -n gatekeeper-system`
- Check constraint status: `kubectl get constraints`
- Review audit logs: `kubectl logs -n gatekeeper-system -l control-plane=controller-manager`
- Ensure constraint template is properly defined and matches policy expectations

### Issue: Policy Tests Failing

**Solution**:
- Run tests with verbose output: `opa test . --verbose`
- Check test input data matches expected format
- Verify policy package names match between policy and test files
- Use `print()` statements in Rego for debugging

### Issue: Performance Degradation with Large Policy Sets

**Solution**:
- Use policy bundles: `opa build policies/ -o bundle.tar.gz`
- Enable partial evaluation for complex policies
- Optimize policy rules to reduce computational complexity
- Index data for faster lookups using `input.key` patterns
- Consider splitting large policy sets into separate evaluation domains

## References

- [OPA Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Rego Language Reference](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/website/)
- [Conftest](https://www.conftest.dev/)
- [OPA Kubernetes Tutorial](https://www.openpolicyagent.org/docs/latest/kubernetes-tutorial/)
- [SOC2 Security Controls](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report.html)
- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/)
- [GDPR Compliance Guide](https://gdpr.eu/)
