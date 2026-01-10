package kubernetes.admission

import future.keywords.contains
import future.keywords.if

# Deny privileged containers
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged == true
    msg := sprintf("Privileged container is not allowed: %v", [container.name])
}

# Enforce non-root user
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("Container must run as non-root user: %v", [container.name])
}

# Require read-only root filesystem
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.securityContext.readOnlyRootFilesystem
    msg := sprintf("Container must use read-only root filesystem: %v", [container.name])
}

# Deny host namespaces
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

# Deny hostPath volumes
deny[msg] {
    input.request.kind.kind == "Pod"
    volume := input.request.object.spec.volumes[_]
    volume.hostPath
    msg := sprintf("hostPath volumes are not allowed: %v", [volume.name])
}

# Require dropping ALL capabilities
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not drops_all_capabilities(container)
    msg := sprintf("Container must drop ALL capabilities: %v", [container.name])
}

drops_all_capabilities(container) {
    container.securityContext.capabilities.drop[_] == "ALL"
}

# Deny dangerous capabilities
dangerous_capabilities := [
    "CAP_SYS_ADMIN",
    "CAP_NET_ADMIN",
    "CAP_SYS_PTRACE",
    "CAP_SYS_MODULE",
]

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    capability := container.securityContext.capabilities.add[_]
    dangerous_capabilities[_] == capability
    msg := sprintf("Capability %v is not allowed for container: %v", [capability, container.name])
}

# Require seccomp profile
deny[msg] {
    input.request.kind.kind == "Pod"
    not input.request.object.spec.securityContext.seccompProfile
    msg := "Pod must define a seccomp profile"
}
