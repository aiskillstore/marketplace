# Common Rego Patterns for Security and Compliance

This reference provides common Rego patterns for implementing security and compliance policies in OPA.

## Table of Contents

- [Basic Patterns](#basic-patterns)
- [Security Patterns](#security-patterns)
- [Compliance Patterns](#compliance-patterns)
- [Advanced Patterns](#advanced-patterns)

## Basic Patterns

### Deny Rules

Most common pattern - deny when condition is met:

```rego
package example

deny[msg] {
    condition_is_true
    msg := "Descriptive error message"
}
```

### Allow Rules

Whitelist pattern - allow specific cases:

```rego
package example

default allow = false

allow {
    input.user.role == "admin"
}

allow {
    input.user.id == input.resource.owner
}
```

### Array Iteration

Iterate over arrays to check conditions:

```rego
package example

deny[msg] {
    container := input.spec.containers[_]
    container.image == "vulnerable:latest"
    msg := sprintf("Vulnerable image detected: %v", [container.name])
}
```

### Object Key Checking

Verify required keys exist:

```rego
package example

required_labels := ["app", "environment", "owner"]

deny[msg] {
    missing := required_labels[_]
    not input.metadata.labels[missing]
    msg := sprintf("Missing required label: %v", [missing])
}
```

## Security Patterns

### Privileged Container Check

Deny privileged containers:

```rego
package kubernetes.security

deny[msg] {
    container := input.spec.containers[_]
    container.securityContext.privileged == true
    msg := sprintf("Privileged container not allowed: %v", [container.name])
}
```

### Host Path Volume Check

Prevent hostPath volumes:

```rego
package kubernetes.security

deny[msg] {
    volume := input.spec.volumes[_]
    volume.hostPath
    msg := sprintf("hostPath volumes not allowed: %v", [volume.name])
}
```

### Image Registry Whitelist

Allow only approved registries:

```rego
package kubernetes.security

allowed_registries := [
    "gcr.io/company",
    "docker.io/company",
]

deny[msg] {
    container := input.spec.containers[_]
    image := container.image
    not startswith_any(image, allowed_registries)
    msg := sprintf("Image from unauthorized registry: %v", [image])
}

startswith_any(str, prefixes) {
    startswith(str, prefixes[_])
}
```

### Network Policy Enforcement

Require network policies for namespaces:

```rego
package kubernetes.security

deny[msg] {
    input.kind == "Namespace"
    not input.metadata.labels["network-policy"]
    msg := "Namespace must have network-policy label"
}
```

### Secret in Environment Variables

Prevent secrets in environment variables:

```rego
package kubernetes.security

deny[msg] {
    container := input.spec.containers[_]
    env := container.env[_]
    contains(lower(env.name), "password")
    env.value  # Direct value, not from secret
    msg := sprintf("Secret in environment variable: %v", [env.name])
}
```

## Compliance Patterns

### SOC2 CC6.1: Access Control

```rego
package compliance.soc2

# Deny cluster-admin for non-system accounts
deny[msg] {
    input.kind == "RoleBinding"
    input.roleRef.name == "cluster-admin"
    not startswith(input.subjects[_].name, "system:")
    msg := sprintf("SOC2 CC6.1: cluster-admin role binding not allowed for %v", [input.metadata.name])
}

# Require authentication labels
deny[msg] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    not input.metadata.annotations["auth.required"]
    msg := "SOC2 CC6.1: LoadBalancer services must require authentication"
}
```

### PCI-DSS 8.2.1: Strong Authentication

```rego
package compliance.pci

# Require MFA annotation
deny[msg] {
    input.kind == "Ingress"
    input.metadata.annotations["payment.enabled"] == "true"
    not input.metadata.annotations["mfa.required"] == "true"
    msg := "PCI-DSS 8.2.1: Payment endpoints must require MFA"
}

# Password complexity requirements
deny[msg] {
    input.kind == "ConfigMap"
    input.data["password.minLength"]
    to_number(input.data["password.minLength"]) < 12
    msg := "PCI-DSS 8.2.1: Minimum password length must be 12"
}
```

### GDPR Article 25: Data Protection by Design

```rego
package compliance.gdpr

# Require data classification
deny[msg] {
    input.kind == "Deployment"
    processes_personal_data(input)
    not input.metadata.labels["data-classification"]
    msg := "GDPR Art25: Deployments processing personal data must have data-classification label"
}

# Require encryption for personal data
deny[msg] {
    input.kind == "PersistentVolumeClaim"
    input.metadata.labels["data-type"] == "personal"
    not input.metadata.annotations["volume.encryption.enabled"] == "true"
    msg := "GDPR Art25: Personal data volumes must use encryption"
}

processes_personal_data(resource) {
    resource.metadata.labels["data-type"] == "personal"
}

processes_personal_data(resource) {
    contains(lower(resource.metadata.name), "user")
}
```

### HIPAA 164.312: Technical Safeguards

```rego
package compliance.hipaa

# Require encryption in transit
deny[msg] {
    input.kind == "Service"
    input.metadata.labels["phi-data"] == "true"
    not input.metadata.annotations["tls.enabled"] == "true"
    msg := "HIPAA 164.312: Services handling PHI must use TLS encryption"
}

# Audit logging requirement
deny[msg] {
    input.kind == "Deployment"
    input.metadata.labels["phi-data"] == "true"
    not has_audit_logging(input)
    msg := "HIPAA 164.312: PHI deployments must enable audit logging"
}

has_audit_logging(resource) {
    resource.spec.template.metadata.annotations["audit.enabled"] == "true"
}
```

## Advanced Patterns

### Helper Functions

Create reusable helper functions:

```rego
package helpers

# Check if string starts with any prefix
startswith_any(str, prefixes) {
    startswith(str, prefixes[_])
}

# Check if array contains value
array_contains(arr, val) {
    arr[_] == val
}

# Get all containers (including init containers)
all_containers[container] {
    container := input.spec.containers[_]
}

all_containers[container] {
    container := input.spec.initContainers[_]
}

# Safe label access with default
get_label(resource, key, default_val) = val {
    val := resource.metadata.labels[key]
} else = default_val
```

### Multi-Framework Mapping

Map single policy to multiple frameworks:

```rego
package multi_framework

deny[msg] {
    container := input.spec.containers[_]
    not container.securityContext.readOnlyRootFilesystem

    msg := {
        "violation": "Container filesystem must be read-only",
        "container": container.name,
        "frameworks": {
            "SOC2": "CC6.1",
            "PCI-DSS": "2.2",
            "NIST": "CM-7",
        }
    }
}
```

### Severity Levels

Add severity to violations:

```rego
package severity

violations[violation] {
    container := input.spec.containers[_]
    container.securityContext.privileged == true

    violation := {
        "message": sprintf("Privileged container: %v", [container.name]),
        "severity": "critical",
        "remediation": "Set securityContext.privileged to false"
    }
}

violations[violation] {
    not input.spec.securityContext.runAsNonRoot

    violation := {
        "message": "Pod does not enforce non-root user",
        "severity": "high",
        "remediation": "Set spec.securityContext.runAsNonRoot to true"
    }
}
```

### Exception Handling

Allow policy exceptions with justification:

```rego
package exceptions

default allow = false

# Check for valid exception
has_exception {
    input.metadata.annotations["policy.exception"] == "true"
    input.metadata.annotations["policy.justification"]
    input.metadata.annotations["policy.approver"]
}

deny[msg] {
    violates_policy
    not has_exception
    msg := "Policy violation - no valid exception found"
}

deny[msg] {
    violates_policy
    has_exception
    not is_valid_approver
    msg := "Policy exception requires valid approver"
}
```

### Data Validation

Validate external data sources:

```rego
package data_validation

import data.approved_images

deny[msg] {
    container := input.spec.containers[_]
    not image_approved(container.image)
    msg := sprintf("Image not in approved list: %v", [container.image])
}

image_approved(image) {
    approved_images[_] == image
}

# Validate with external API (requires OPA bundle with data)
deny[msg] {
    input.kind == "Deployment"
    namespace := input.metadata.namespace
    not data.namespaces[namespace].approved
    msg := sprintf("Deployment to unapproved namespace: %v", [namespace])
}
```

### Testing Patterns

Write comprehensive tests:

```rego
package example_test

import data.example

# Test deny rule
test_deny_privileged {
    input := {
        "spec": {
            "containers": [{
                "name": "app",
                "securityContext": {"privileged": true}
            }]
        }
    }
    count(example.deny) > 0
}

# Test allow case
test_allow_unprivileged {
    input := {
        "spec": {
            "containers": [{
                "name": "app",
                "securityContext": {"privileged": false}
            }]
        }
    }
    count(example.deny) == 0
}

# Test with multiple containers
test_multiple_containers {
    input := {
        "spec": {
            "containers": [
                {"name": "app1", "securityContext": {"privileged": false}},
                {"name": "app2", "securityContext": {"privileged": true}}
            ]
        }
    }
    count(example.deny) == 1
}
```

## Performance Optimization

### Index Data Structures

Use indexed data for faster lookups:

```rego
# Slow - iterates every time
approved_images := ["image1:v1", "image2:v1", "image3:v1"]

deny[msg] {
    container := input.spec.containers[_]
    not array_contains(approved_images, container.image)
    msg := "Image not approved"
}

# Fast - uses indexing
approved_images_set := {
    "image1:v1",
    "image2:v1",
    "image3:v1"
}

deny[msg] {
    container := input.spec.containers[_]
    not approved_images_set[container.image]
    msg := "Image not approved"
}
```

### Partial Evaluation

Use comprehensions for efficiency:

```rego
# Collect all violations at once
all_violations := [msg |
    container := input.spec.containers[_]
    violates_policy(container)
    msg := format_message(container)
]

deny[msg] {
    msg := all_violations[_]
}
```

## References

- [Rego Language Reference](https://www.openpolicyagent.org/docs/latest/policy-reference/)
- [OPA Best Practices](https://www.openpolicyagent.org/docs/latest/policy-performance/)
- [Rego Style Guide](https://github.com/open-policy-agent/opa/blob/main/docs/content/policy-language.md)
