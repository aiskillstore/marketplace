package compliance.soc2

import future.keywords.if

# SOC2 CC6.1: Logical and Physical Access Controls

# Deny overly permissive RBAC
deny[msg] {
    input.kind == "RoleBinding"
    input.roleRef.name == "cluster-admin"
    not startswith(input.subjects[_].name, "system:")
    msg := {
        "control": "SOC2 CC6.1",
        "severity": "high",
        "violation": sprintf("Overly permissive cluster-admin binding: %v", [input.metadata.name]),
        "remediation": "Use least-privilege roles instead of cluster-admin",
    }
}

# Require authentication for external services
deny[msg] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    not input.metadata.annotations["auth.required"] == "true"
    msg := {
        "control": "SOC2 CC6.1",
        "severity": "medium",
        "violation": sprintf("External service without authentication: %v", [input.metadata.name]),
        "remediation": "Add annotation: auth.required=true",
    }
}

# SOC2 CC6.6: Encryption in Transit

# Require TLS for Ingress
deny[msg] {
    input.kind == "Ingress"
    not input.spec.tls
    msg := {
        "control": "SOC2 CC6.6",
        "severity": "high",
        "violation": sprintf("Ingress without TLS: %v", [input.metadata.name]),
        "remediation": "Configure spec.tls with valid certificates",
    }
}

# Require TLS for LoadBalancer
deny[msg] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    not input.metadata.annotations["service.beta.kubernetes.io/aws-load-balancer-ssl-cert"]
    msg := {
        "control": "SOC2 CC6.6",
        "severity": "high",
        "violation": sprintf("LoadBalancer without SSL/TLS: %v", [input.metadata.name]),
        "remediation": "Add SSL certificate annotation",
    }
}

# SOC2 CC6.7: Encryption at Rest

# Require encrypted volumes for confidential data
deny[msg] {
    input.kind == "PersistentVolumeClaim"
    input.metadata.labels["data-classification"] == "confidential"
    not input.metadata.annotations["volume.beta.kubernetes.io/storage-encrypted"] == "true"
    msg := {
        "control": "SOC2 CC6.7",
        "severity": "high",
        "violation": sprintf("Unencrypted volume for confidential data: %v", [input.metadata.name]),
        "remediation": "Enable volume encryption annotation",
    }
}

# SOC2 CC7.2: System Monitoring

# Require audit logging for critical systems
deny[msg] {
    input.kind == "Deployment"
    input.metadata.labels["critical-system"] == "true"
    not has_audit_logging(input)
    msg := {
        "control": "SOC2 CC7.2",
        "severity": "medium",
        "violation": sprintf("Critical system without audit logging: %v", [input.metadata.name]),
        "remediation": "Enable audit logging via sidecar or annotations",
    }
}

has_audit_logging(resource) {
    resource.spec.template.metadata.annotations["audit.enabled"] == "true"
}

# SOC2 CC8.1: Change Management

# Require approval for production changes
deny[msg] {
    input.kind == "Deployment"
    input.metadata.namespace == "production"
    not input.metadata.annotations["change-request.id"]
    msg := {
        "control": "SOC2 CC8.1",
        "severity": "medium",
        "violation": sprintf("Production deployment without change request: %v", [input.metadata.name]),
        "remediation": "Add annotation: change-request.id=CR-XXXX",
    }
}
