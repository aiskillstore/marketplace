package compliance.pci

import future.keywords.if

# PCI-DSS Requirement 1.2: Firewall Configuration

# Require network policies for cardholder data
deny[msg] {
    input.kind == "Namespace"
    input.metadata.labels["pci.scope"] == "in-scope"
    not input.metadata.annotations["network-policy.enabled"] == "true"
    msg := {
        "control": "PCI-DSS 1.2",
        "severity": "high",
        "violation": sprintf("PCI in-scope namespace requires network policy: %v", [input.metadata.name]),
        "remediation": "Create NetworkPolicy to restrict traffic and add annotation",
    }
}

# PCI-DSS Requirement 2.2: System Hardening

# Container hardening - read-only filesystem
deny[msg] {
    input.kind == "Pod"
    input.metadata.labels["pci.scope"] == "in-scope"
    container := input.spec.containers[_]
    not container.securityContext.readOnlyRootFilesystem
    msg := {
        "control": "PCI-DSS 2.2",
        "severity": "high",
        "violation": sprintf("PCI container requires read-only filesystem: %v", [container.name]),
        "remediation": "Set securityContext.readOnlyRootFilesystem: true",
    }
}

# Container hardening - no privilege escalation
deny[msg] {
    input.kind == "Pod"
    input.metadata.labels["pci.scope"] == "in-scope"
    container := input.spec.containers[_]
    not container.securityContext.allowPrivilegeEscalation == false
    msg := {
        "control": "PCI-DSS 2.2",
        "severity": "high",
        "violation": sprintf("PCI container allows privilege escalation: %v", [container.name]),
        "remediation": "Set securityContext.allowPrivilegeEscalation: false",
    }
}

# PCI-DSS Requirement 3.4: Encryption of Cardholder Data

# Require encryption for PCI data at rest
deny[msg] {
    input.kind == "PersistentVolumeClaim"
    input.metadata.labels["pci.scope"] == "in-scope"
    not input.metadata.annotations["volume.encryption.enabled"] == "true"
    msg := {
        "control": "PCI-DSS 3.4",
        "severity": "critical",
        "violation": sprintf("PCI volume requires encryption: %v", [input.metadata.name]),
        "remediation": "Enable volume encryption",
    }
}

# Require TLS for PCI data in transit
deny[msg] {
    input.kind == "Service"
    input.metadata.labels["pci.scope"] == "in-scope"
    not input.metadata.annotations["tls.enabled"] == "true"
    msg := {
        "control": "PCI-DSS 4.1",
        "severity": "critical",
        "violation": sprintf("PCI service requires TLS encryption: %v", [input.metadata.name]),
        "remediation": "Enable TLS for data in transit",
    }
}

# PCI-DSS Requirement 8.2.1: Strong Authentication

# Require MFA for payment endpoints
deny[msg] {
    input.kind == "Ingress"
    input.metadata.labels["payment.enabled"] == "true"
    not input.metadata.annotations["mfa.required"] == "true"
    msg := {
        "control": "PCI-DSS 8.2.1",
        "severity": "high",
        "violation": sprintf("Payment ingress requires MFA: %v", [input.metadata.name]),
        "remediation": "Enable MFA via annotation: mfa.required=true",
    }
}

# PCI-DSS Requirement 10.2: Audit Logging

# Require audit logging for PCI components
deny[msg] {
    input.kind == "Deployment"
    input.metadata.labels["pci.scope"] == "in-scope"
    not has_audit_logging(input)
    msg := {
        "control": "PCI-DSS 10.2",
        "severity": "high",
        "violation": sprintf("PCI deployment requires audit logging: %v", [input.metadata.name]),
        "remediation": "Deploy audit logging sidecar or enable centralized logging",
    }
}

has_audit_logging(resource) {
    resource.spec.template.metadata.annotations["audit.enabled"] == "true"
}

has_audit_logging(resource) {
    container := resource.spec.template.spec.containers[_]
    contains(container.name, "audit")
}

# PCI-DSS Requirement 11.3: Penetration Testing

# Require security testing evidence for PCI deployments
deny[msg] {
    input.kind == "Deployment"
    input.metadata.labels["pci.scope"] == "in-scope"
    input.metadata.namespace == "production"
    not input.metadata.annotations["security-testing.date"]
    msg := {
        "control": "PCI-DSS 11.3",
        "severity": "medium",
        "violation": sprintf("PCI deployment requires security testing evidence: %v", [input.metadata.name]),
        "remediation": "Add annotation: security-testing.date=YYYY-MM-DD",
    }
}
