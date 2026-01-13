# Compliance Framework Policy Templates

Policy templates mapped to specific compliance framework controls for SOC2, PCI-DSS, GDPR, HIPAA, and NIST.

## Table of Contents

- [SOC2 Trust Services Criteria](#soc2-trust-services-criteria)
- [PCI-DSS Requirements](#pci-dss-requirements)
- [GDPR Data Protection](#gdpr-data-protection)
- [HIPAA Security Rules](#hipaa-security-rules)
- [NIST Cybersecurity Framework](#nist-cybersecurity-framework)

## SOC2 Trust Services Criteria

### CC6.1: Logical and Physical Access Controls

**Control**: The entity implements logical access security software, infrastructure, and architectures over protected information assets to protect them from security events.

```rego
package compliance.soc2.cc6_1

# Deny overly permissive RBAC
deny[msg] {
    input.kind == "RoleBinding"
    input.roleRef.name == "cluster-admin"
    not startswith(input.subjects[_].name, "system:")
    msg := {
        "control": "SOC2 CC6.1",
        "violation": sprintf("Overly permissive cluster-admin binding: %v", [input.metadata.name]),
        "remediation": "Use least-privilege roles instead of cluster-admin"
    }
}

# Require authentication for external services
deny[msg] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    not input.metadata.annotations["auth.required"] == "true"
    msg := {
        "control": "SOC2 CC6.1",
        "violation": sprintf("External service without authentication: %v", [input.metadata.name]),
        "remediation": "Add auth.required=true annotation"
    }
}

# Require MFA for admin access
deny[msg] {
    input.kind == "RoleBinding"
    contains(input.roleRef.name, "admin")
    not input.metadata.annotations["mfa.required"] == "true"
    msg := {
        "control": "SOC2 CC6.1",
        "violation": sprintf("Admin role without MFA requirement: %v", [input.metadata.name]),
        "remediation": "Add mfa.required=true annotation"
    }
}
```

### CC6.6: Encryption in Transit

**Control**: The entity protects information transmitted to external parties during transmission.

```rego
package compliance.soc2.cc6_6

# Require TLS for external services
deny[msg] {
    input.kind == "Ingress"
    not input.spec.tls
    msg := {
        "control": "SOC2 CC6.6",
        "violation": sprintf("Ingress without TLS: %v", [input.metadata.name]),
        "remediation": "Configure spec.tls with valid certificates"
    }
}

# Require TLS for LoadBalancer services
deny[msg] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    not input.metadata.annotations["service.beta.kubernetes.io/aws-load-balancer-ssl-cert"]
    msg := {
        "control": "SOC2 CC6.6",
        "violation": sprintf("LoadBalancer without SSL/TLS: %v", [input.metadata.name]),
        "remediation": "Add SSL certificate annotation"
    }
}
```

### CC6.7: Encryption at Rest

**Control**: The entity protects information at rest.

```rego
package compliance.soc2.cc6_7

# Require encrypted volumes
deny[msg] {
    input.kind == "PersistentVolumeClaim"
    input.metadata.labels["data-classification"] == "confidential"
    not input.metadata.annotations["volume.beta.kubernetes.io/storage-encrypted"] == "true"
    msg := {
        "control": "SOC2 CC6.7",
        "violation": sprintf("Unencrypted volume for confidential data: %v", [input.metadata.name]),
        "remediation": "Enable volume encryption annotation"
    }
}
```

### CC7.2: System Monitoring

**Control**: The entity monitors system components and the operation of those components for anomalies.

```rego
package compliance.soc2.cc7_2

# Require audit logging
deny[msg] {
    input.kind == "Deployment"
    input.metadata.labels["critical-system"] == "true"
    not has_audit_logging(input)
    msg := {
        "control": "SOC2 CC7.2",
        "violation": sprintf("Critical system without audit logging: %v", [input.metadata.name]),
        "remediation": "Enable audit logging via sidecar or annotations"
    }
}

has_audit_logging(resource) {
    resource.spec.template.metadata.annotations["audit.enabled"] == "true"
}
```

## PCI-DSS Requirements

### Requirement 1.2: Firewall Configuration

**Control**: Build firewall and router configurations that restrict connections between untrusted networks.

```rego
package compliance.pci.req1_2

# Require network policies for cardholder data
deny[msg] {
    input.kind == "Namespace"
    input.metadata.labels["pci.scope"] == "in-scope"
    not has_network_policy(input.metadata.name)
    msg := {
        "control": "PCI-DSS 1.2",
        "violation": sprintf("PCI in-scope namespace without network policy: %v", [input.metadata.name]),
        "remediation": "Create NetworkPolicy to restrict traffic"
    }
}

has_network_policy(namespace) {
    # Check if NetworkPolicy exists in data (requires external data)
    data.network_policies[namespace]
}
```

### Requirement 2.2: System Hardening

**Control**: Develop configuration standards for all system components.

```rego
package compliance.pci.req2_2

# Container hardening requirements
deny[msg] {
    input.kind == "Pod"
    input.metadata.labels["pci.scope"] == "in-scope"
    container := input.spec.containers[_]

    not container.securityContext.readOnlyRootFilesystem
    msg := {
        "control": "PCI-DSS 2.2",
        "violation": sprintf("PCI container without read-only filesystem: %v", [container.name]),
        "remediation": "Set securityContext.readOnlyRootFilesystem: true"
    }
}

deny[msg] {
    input.kind == "Pod"
    input.metadata.labels["pci.scope"] == "in-scope"
    container := input.spec.containers[_]

    not container.securityContext.allowPrivilegeEscalation == false
    msg := {
        "control": "PCI-DSS 2.2",
        "violation": sprintf("PCI container allows privilege escalation: %v", [container.name]),
        "remediation": "Set securityContext.allowPrivilegeEscalation: false"
    }
}
```

### Requirement 8.2.1: Strong Authentication

**Control**: Render all authentication credentials unreadable during transmission and storage.

```rego
package compliance.pci.req8_2_1

# Require MFA for payment endpoints
deny[msg] {
    input.kind == "Ingress"
    input.metadata.labels["payment.enabled"] == "true"
    not input.metadata.annotations["mfa.required"] == "true"
    msg := {
        "control": "PCI-DSS 8.2.1",
        "violation": sprintf("Payment ingress without MFA: %v", [input.metadata.name]),
        "remediation": "Enable MFA via annotation: mfa.required=true"
    }
}

# Password strength requirements
deny[msg] {
    input.kind == "ConfigMap"
    input.metadata.name == "auth-config"
    to_number(input.data["password.minLength"]) < 12
    msg := {
        "control": "PCI-DSS 8.2.1",
        "violation": "Password minimum length below requirement",
        "remediation": "Set password.minLength to at least 12"
    }
}
```

### Requirement 10.2: Audit Logging

**Control**: Implement automated audit trails for all system components.

```rego
package compliance.pci.req10_2

# Require audit logging for PCI components
deny[msg] {
    input.kind == "Deployment"
    input.metadata.labels["pci.scope"] == "in-scope"
    not has_audit_sidecar(input)
    msg := {
        "control": "PCI-DSS 10.2",
        "violation": sprintf("PCI deployment without audit logging: %v", [input.metadata.name]),
        "remediation": "Deploy audit logging sidecar"
    }
}

has_audit_sidecar(resource) {
    container := resource.spec.template.spec.containers[_]
    contains(container.name, "audit")
}
```

## GDPR Data Protection

### Article 25: Data Protection by Design

**Control**: The controller shall implement appropriate technical and organizational measures.

```rego
package compliance.gdpr.art25

# Require data classification labels
deny[msg] {
    input.kind == "Deployment"
    processes_personal_data(input)
    not input.metadata.labels["data-classification"]
    msg := {
        "control": "GDPR Article 25",
        "violation": sprintf("Deployment processing personal data without classification: %v", [input.metadata.name]),
        "remediation": "Add data-classification label"
    }
}

# Data minimization - limit replicas for personal data
deny[msg] {
    input.kind == "Deployment"
    input.metadata.labels["data-type"] == "personal"
    input.spec.replicas > 3
    not input.metadata.annotations["gdpr.justification"]
    msg := {
        "control": "GDPR Article 25",
        "violation": sprintf("Excessive replicas for personal data: %v", [input.metadata.name]),
        "remediation": "Reduce replicas or add justification annotation"
    }
}

processes_personal_data(resource) {
    resource.metadata.labels["data-type"] == "personal"
}

processes_personal_data(resource) {
    contains(lower(resource.metadata.name), "user")
}
```

### Article 32: Security of Processing

**Control**: Implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk.

```rego
package compliance.gdpr.art32

# Require encryption for personal data
deny[msg] {
    input.kind == "PersistentVolumeClaim"
    input.metadata.labels["data-type"] == "personal"
    not input.metadata.annotations["volume.encryption.enabled"] == "true"
    msg := {
        "control": "GDPR Article 32",
        "violation": sprintf("Personal data volume without encryption: %v", [input.metadata.name]),
        "remediation": "Enable volume encryption"
    }
}

# Require TLS for personal data services
deny[msg] {
    input.kind == "Service"
    input.metadata.labels["data-type"] == "personal"
    not input.metadata.annotations["tls.enabled"] == "true"
    msg := {
        "control": "GDPR Article 32",
        "violation": sprintf("Personal data service without TLS: %v", [input.metadata.name]),
        "remediation": "Enable TLS encryption"
    }
}
```

## HIPAA Security Rules

### 164.308: Administrative Safeguards

**Control**: Implement policies and procedures to prevent, detect, contain, and correct security violations.

```rego
package compliance.hipaa.admin

# Require access control policies
deny[msg] {
    input.kind == "Namespace"
    input.metadata.labels["phi-data"] == "true"
    not input.metadata.annotations["access-control.policy"]
    msg := {
        "control": "HIPAA 164.308",
        "violation": sprintf("PHI namespace without access control policy: %v", [input.metadata.name]),
        "remediation": "Document access control policy in annotation"
    }
}
```

### 164.312: Technical Safeguards

**Control**: Implement technical policies and procedures for electronic information systems.

```rego
package compliance.hipaa.technical

# Encryption in transit for PHI
deny[msg] {
    input.kind == "Service"
    input.metadata.labels["phi-data"] == "true"
    not input.metadata.annotations["tls.enabled"] == "true"
    msg := {
        "control": "HIPAA 164.312",
        "violation": sprintf("PHI service without TLS: %v", [input.metadata.name]),
        "remediation": "Enable TLS for data in transit"
    }
}

# Audit logging for PHI access
deny[msg] {
    input.kind == "Deployment"
    input.metadata.labels["phi-data"] == "true"
    not has_audit_logging(input)
    msg := {
        "control": "HIPAA 164.312",
        "violation": sprintf("PHI deployment without audit logging: %v", [input.metadata.name]),
        "remediation": "Enable audit logging for all PHI access"
    }
}

has_audit_logging(resource) {
    resource.spec.template.metadata.annotations["audit.enabled"] == "true"
}

# Authentication controls
deny[msg] {
    input.kind == "Ingress"
    input.metadata.labels["phi-data"] == "true"
    not input.metadata.annotations["auth.method"]
    msg := {
        "control": "HIPAA 164.312",
        "violation": sprintf("PHI ingress without authentication: %v", [input.metadata.name]),
        "remediation": "Configure authentication method"
    }
}
```

## NIST Cybersecurity Framework

### PR.AC-4: Access Control

**Control**: Access permissions and authorizations are managed, incorporating the principles of least privilege and separation of duties.

```rego
package compliance.nist.pr_ac_4

# Least privilege - no wildcard permissions
deny[msg] {
    input.kind == "Role"
    rule := input.rules[_]
    rule.verbs[_] == "*"
    msg := {
        "control": "NIST PR.AC-4",
        "violation": sprintf("Wildcard permissions in role: %v", [input.metadata.name]),
        "remediation": "Specify explicit verb permissions"
    }
}

deny[msg] {
    input.kind == "Role"
    rule := input.rules[_]
    rule.resources[_] == "*"
    msg := {
        "control": "NIST PR.AC-4",
        "violation": sprintf("Wildcard resources in role: %v", [input.metadata.name]),
        "remediation": "Specify explicit resource permissions"
    }
}
```

### PR.DS-1: Data-at-Rest Protection

**Control**: Data-at-rest is protected.

```rego
package compliance.nist.pr_ds_1

# Require encryption for sensitive data
deny[msg] {
    input.kind == "PersistentVolumeClaim"
    input.metadata.labels["data-sensitivity"] == "high"
    not input.metadata.annotations["volume.encryption"] == "enabled"
    msg := {
        "control": "NIST PR.DS-1",
        "violation": sprintf("Sensitive data volume without encryption: %v", [input.metadata.name]),
        "remediation": "Enable volume encryption for data-at-rest protection"
    }
}
```

### PR.DS-2: Data-in-Transit Protection

**Control**: Data-in-transit is protected.

```rego
package compliance.nist.pr_ds_2

# Require TLS for external traffic
deny[msg] {
    input.kind == "Ingress"
    not input.spec.tls
    msg := {
        "control": "NIST PR.DS-2",
        "violation": sprintf("Ingress without TLS: %v", [input.metadata.name]),
        "remediation": "Configure TLS for data-in-transit protection"
    }
}
```

## Multi-Framework Compliance

Example policy that maps to multiple frameworks:

```rego
package compliance.multi_framework

# Encryption requirement - maps to multiple frameworks
deny[msg] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    not has_tls_encryption(input)

    msg := {
        "violation": sprintf("External service without TLS encryption: %v", [input.metadata.name]),
        "remediation": "Enable TLS/SSL for external services",
        "frameworks": {
            "SOC2": "CC6.6 - Encryption in Transit",
            "PCI-DSS": "4.1 - Use strong cryptography",
            "GDPR": "Article 32 - Security of Processing",
            "HIPAA": "164.312 - Technical Safeguards",
            "NIST": "PR.DS-2 - Data-in-Transit Protection"
        }
    }
}

has_tls_encryption(service) {
    service.metadata.annotations["service.beta.kubernetes.io/aws-load-balancer-ssl-cert"]
}
```

## References

- [SOC2 Trust Services Criteria](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report.html)
- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/document_library)
- [GDPR Official Text](https://gdpr.eu/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
