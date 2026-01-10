# Kubernetes Security Policies

Comprehensive OPA policies for Kubernetes security best practices and admission control.

## Table of Contents

- [Pod Security](#pod-security)
- [RBAC Security](#rbac-security)
- [Network Security](#network-security)
- [Image Security](#image-security)
- [Secret Management](#secret-management)

## Pod Security

### Privileged Containers

Deny privileged containers:

```rego
package kubernetes.admission.privileged_containers

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged == true

    msg := sprintf("Privileged container is not allowed: %v", [container.name])
}

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.initContainers[_]
    container.securityContext.privileged == true

    msg := sprintf("Privileged init container is not allowed: %v", [container.name])
}
```

### Run as Non-Root

Enforce containers run as non-root:

```rego
package kubernetes.admission.non_root

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.securityContext.runAsNonRoot

    msg := sprintf("Container must run as non-root user: %v", [container.name])
}

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    container.securityContext.runAsUser == 0

    msg := sprintf("Container cannot run as UID 0 (root): %v", [container.name])
}
```

### Read-Only Root Filesystem

Require read-only root filesystem:

```rego
package kubernetes.admission.readonly_root

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.securityContext.readOnlyRootFilesystem

    msg := sprintf("Container must use read-only root filesystem: %v", [container.name])
}
```

### Capabilities

Restrict Linux capabilities:

```rego
package kubernetes.admission.capabilities

# Denied capabilities
denied_capabilities := [
    "CAP_SYS_ADMIN",
    "CAP_NET_ADMIN",
    "CAP_SYS_PTRACE",
    "CAP_SYS_MODULE",
]

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    capability := container.securityContext.capabilities.add[_]
    denied_capabilities[_] == capability

    msg := sprintf("Capability %v is not allowed for container: %v", [capability, container.name])
}

# Require dropping ALL capabilities by default
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not drops_all_capabilities(container)

    msg := sprintf("Container must drop ALL capabilities: %v", [container.name])
}

drops_all_capabilities(container) {
    container.securityContext.capabilities.drop[_] == "ALL"
}
```

### Host Namespaces

Prevent use of host namespaces:

```rego
package kubernetes.admission.host_namespaces

deny[msg] {
    input.request.kind.kind == "Pod"
    input.request.object.spec.hostPID == true

    msg := "Sharing the host PID namespace is not allowed"
}

deny[msg] {
    input.request.kind.kind == "Pod"
    input.request.object.spec.hostIPC == true

    msg := "Sharing the host IPC namespace is not allowed"
}

deny[msg] {
    input.request.kind.kind == "Pod"
    input.request.object.spec.hostNetwork == true

    msg := "Sharing the host network namespace is not allowed"
}
```

### Host Paths

Restrict hostPath volumes:

```rego
package kubernetes.admission.host_path

# Allowed host paths (if any)
allowed_host_paths := [
    "/var/log/pods",  # Example: log collection
]

deny[msg] {
    input.request.kind.kind == "Pod"
    volume := input.request.object.spec.volumes[_]
    volume.hostPath
    not is_allowed_host_path(volume.hostPath.path)

    msg := sprintf("hostPath volume is not allowed: %v", [volume.hostPath.path])
}

is_allowed_host_path(path) {
    allowed_host_paths[_] == path
}
```

### Security Context

Comprehensive pod security context validation:

```rego
package kubernetes.admission.security_context

deny[msg] {
    input.request.kind.kind == "Pod"
    not input.request.object.spec.securityContext

    msg := "Pod must define a security context"
}

deny[msg] {
    input.request.kind.kind == "Pod"
    pod_security := input.request.object.spec.securityContext
    not pod_security.runAsNonRoot

    msg := "Pod security context must set runAsNonRoot: true"
}

deny[msg] {
    input.request.kind.kind == "Pod"
    pod_security := input.request.object.spec.securityContext
    not pod_security.seccompProfile

    msg := "Pod must define a seccomp profile"
}
```

## RBAC Security

### Wildcard Permissions

Prevent wildcard RBAC permissions:

```rego
package kubernetes.rbac.wildcards

deny[msg] {
    input.request.kind.kind == "Role"
    rule := input.request.object.rules[_]
    rule.verbs[_] == "*"

    msg := sprintf("Role contains wildcard verb permission in rule: %v", [rule])
}

deny[msg] {
    input.request.kind.kind == "Role"
    rule := input.request.object.rules[_]
    rule.resources[_] == "*"

    msg := sprintf("Role contains wildcard resource permission in rule: %v", [rule])
}

deny[msg] {
    input.request.kind.kind == "ClusterRole"
    rule := input.request.object.rules[_]
    rule.verbs[_] == "*"

    msg := sprintf("ClusterRole contains wildcard verb permission in rule: %v", [rule])
}
```

### Cluster Admin

Restrict cluster-admin usage:

```rego
package kubernetes.rbac.cluster_admin

# System accounts allowed to use cluster-admin
allowed_system_accounts := [
    "system:kube-controller-manager",
    "system:kube-scheduler",
]

deny[msg] {
    input.request.kind.kind == "ClusterRoleBinding"
    input.request.object.roleRef.name == "cluster-admin"
    subject := input.request.object.subjects[_]
    not is_allowed_system_account(subject)

    msg := sprintf("cluster-admin binding not allowed for subject: %v", [subject.name])
}

is_allowed_system_account(subject) {
    allowed_system_accounts[_] == subject.name
}
```

### Service Account Token Mounting

Control service account token auto-mounting:

```rego
package kubernetes.rbac.service_account_tokens

deny[msg] {
    input.request.kind.kind == "Pod"
    input.request.object.spec.automountServiceAccountToken == true
    not requires_service_account(input.request.object)

    msg := "Pod should not auto-mount service account token unless required"
}

requires_service_account(pod) {
    pod.metadata.annotations["requires-service-account"] == "true"
}
```

## Network Security

### Network Policies Required

Require network policies for namespaces:

```rego
package kubernetes.network.policies_required

# Check if namespace has network policies (requires admission controller data)
deny[msg] {
    input.request.kind.kind == "Namespace"
    not has_network_policy_annotation(input.request.object)

    msg := sprintf("Namespace must have network policy annotation: %v", [input.request.object.metadata.name])
}

has_network_policy_annotation(namespace) {
    namespace.metadata.annotations["network-policy.enabled"] == "true"
}
```

### Deny Default Network Policy

Implement default-deny network policy:

```rego
package kubernetes.network.default_deny

deny[msg] {
    input.request.kind.kind == "NetworkPolicy"
    not is_default_deny(input.request.object)
    input.request.object.metadata.labels["policy-type"] == "default"

    msg := "Default network policy must be deny-all"
}

is_default_deny(network_policy) {
    # Check for empty ingress rules (deny all ingress)
    not network_policy.spec.ingress
    # Check for ingress type
    network_policy.spec.policyTypes[_] == "Ingress"
}
```

### Service Type LoadBalancer

Restrict external LoadBalancer services:

```rego
package kubernetes.network.loadbalancer

deny[msg] {
    input.request.kind.kind == "Service"
    input.request.object.spec.type == "LoadBalancer"
    not is_approved_for_external_exposure(input.request.object)

    msg := sprintf("LoadBalancer service requires approval annotation: %v", [input.request.object.metadata.name])
}

is_approved_for_external_exposure(service) {
    service.metadata.annotations["external-exposure.approved"] == "true"
}
```

## Image Security

### Image Registry Whitelist

Allow only approved image registries:

```rego
package kubernetes.images.registry_whitelist

approved_registries := [
    "gcr.io/my-company",
    "docker.io/my-company",
    "quay.io/my-company",
]

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not is_approved_registry(container.image)

    msg := sprintf("Image from unapproved registry: %v", [container.image])
}

is_approved_registry(image) {
    startswith(image, approved_registries[_])
}
```

### Image Tags

Prevent latest tag and require specific tags:

```rego
package kubernetes.images.tags

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    endswith(container.image, ":latest")

    msg := sprintf("Container uses 'latest' tag: %v", [container.name])
}

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not contains(container.image, ":")

    msg := sprintf("Container image must specify a tag: %v", [container.name])
}
```

### Image Vulnerability Scanning

Require vulnerability scan results:

```rego
package kubernetes.images.vulnerability_scanning

deny[msg] {
    input.request.kind.kind == "Pod"
    not has_scan_annotation(input.request.object)

    msg := "Pod must have vulnerability scan results annotation"
}

deny[msg] {
    input.request.kind.kind == "Pod"
    scan_result := input.request.object.metadata.annotations["vulnerability-scan.result"]
    scan_result == "failed"

    msg := "Pod image failed vulnerability scan"
}

has_scan_annotation(pod) {
    pod.metadata.annotations["vulnerability-scan.result"]
}
```

## Secret Management

### Environment Variable Secrets

Prevent secrets in environment variables:

```rego
package kubernetes.secrets.env_vars

sensitive_keywords := [
    "password",
    "token",
    "apikey",
    "secret",
    "credential",
]

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    env := container.env[_]
    is_sensitive_name(env.name)
    env.value  # Direct value, not from secret

    msg := sprintf("Sensitive data in environment variable: %v in container %v", [env.name, container.name])
}

is_sensitive_name(name) {
    lower_name := lower(name)
    contains(lower_name, sensitive_keywords[_])
}
```

### Secret Volume Permissions

Restrict secret volume mount permissions:

```rego
package kubernetes.secrets.volume_permissions

deny[msg] {
    input.request.kind.kind == "Pod"
    volume := input.request.object.spec.volumes[_]
    volume.secret
    volume_mount := input.request.object.spec.containers[_].volumeMounts[_]
    volume_mount.name == volume.name
    not volume_mount.readOnly

    msg := sprintf("Secret volume mount must be read-only: %v", [volume.name])
}
```

### External Secrets

Require use of external secret management:

```rego
package kubernetes.secrets.external

deny[msg] {
    input.request.kind.kind == "Secret"
    input.request.object.metadata.labels["environment"] == "production"
    not input.request.object.metadata.annotations["external-secret.enabled"] == "true"

    msg := sprintf("Production secrets must use external secret management: %v", [input.request.object.metadata.name])
}
```

## Admission Control Integration

Example OPA Gatekeeper ConstraintTemplate:

```yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8spodsecsecurity
spec:
  crd:
    spec:
      names:
        kind: K8sPodSecSecurity
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8spodsecurity

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          container.securityContext.privileged == true
          msg := sprintf("Privileged container not allowed: %v", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.securityContext.runAsNonRoot
          msg := sprintf("Container must run as non-root: %v", [container.name])
        }
```

Example Constraint:

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sPodSecSecurity
metadata:
  name: pod-security-policy
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces:
      - "production"
      - "staging"
```

## References

- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [OPA Gatekeeper Library](https://github.com/open-policy-agent/gatekeeper-library)
- [NSA Kubernetes Hardening Guide](https://www.nsa.gov/Press-Room/News-Highlights/Article/Article/2716980/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
