package compliance.gdpr

import future.keywords.if

# GDPR Article 25: Data Protection by Design and by Default

# Require data classification labels
deny[msg] {
    input.kind == "Deployment"
    processes_personal_data(input)
    not input.metadata.labels["data-classification"]
    msg := {
        "control": "GDPR Article 25",
        "severity": "high",
        "violation": sprintf("Deployment processing personal data requires classification: %v", [input.metadata.name]),
        "remediation": "Add label: data-classification=personal|sensitive|public",
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
        "severity": "medium",
        "violation": sprintf("Excessive replicas for personal data: %v", [input.metadata.name]),
        "remediation": "Reduce replicas or add justification annotation",
    }
}

# Require purpose limitation annotation
deny[msg] {
    input.kind == "Deployment"
    processes_personal_data(input)
    not input.metadata.annotations["data-purpose"]
    msg := {
        "control": "GDPR Article 25",
        "severity": "medium",
        "violation": sprintf("Personal data deployment requires purpose annotation: %v", [input.metadata.name]),
        "remediation": "Add annotation: data-purpose=<specific purpose>",
    }
}

processes_personal_data(resource) {
    resource.metadata.labels["data-type"] == "personal"
}

processes_personal_data(resource) {
    resource.metadata.labels["data-type"] == "pii"
}

processes_personal_data(resource) {
    contains(lower(resource.metadata.name), "user")
}

# GDPR Article 32: Security of Processing

# Require encryption for personal data volumes
deny[msg] {
    input.kind == "PersistentVolumeClaim"
    input.metadata.labels["data-type"] == "personal"
    not input.metadata.annotations["volume.encryption.enabled"] == "true"
    msg := {
        "control": "GDPR Article 32",
        "severity": "high",
        "violation": sprintf("Personal data volume requires encryption: %v", [input.metadata.name]),
        "remediation": "Enable volume encryption",
    }
}

# Require TLS for personal data services
deny[msg] {
    input.kind == "Service"
    input.metadata.labels["data-type"] == "personal"
    not input.metadata.annotations["tls.enabled"] == "true"
    msg := {
        "control": "GDPR Article 32",
        "severity": "high",
        "violation": sprintf("Personal data service requires TLS: %v", [input.metadata.name]),
        "remediation": "Enable TLS encryption",
    }
}

# Require pseudonymization or anonymization
deny[msg] {
    input.kind == "Deployment"
    processes_personal_data(input)
    not input.metadata.annotations["data-protection.method"]
    msg := {
        "control": "GDPR Article 32",
        "severity": "medium",
        "violation": sprintf("Personal data deployment requires protection method: %v", [input.metadata.name]),
        "remediation": "Add annotation: data-protection.method=pseudonymization|anonymization|encryption",
    }
}

# GDPR Article 33: Breach Notification

# Require incident response plan
deny[msg] {
    input.kind == "Deployment"
    processes_personal_data(input)
    input.metadata.namespace == "production"
    not input.metadata.annotations["incident-response.plan"]
    msg := {
        "control": "GDPR Article 33",
        "severity": "medium",
        "violation": sprintf("Production personal data deployment requires incident response plan: %v", [input.metadata.name]),
        "remediation": "Add annotation: incident-response.plan=<plan-id>",
    }
}

# GDPR Article 30: Records of Processing Activities

# Require data processing record
deny[msg] {
    input.kind == "Deployment"
    processes_personal_data(input)
    not input.metadata.annotations["dpa.record-id"]
    msg := {
        "control": "GDPR Article 30",
        "severity": "medium",
        "violation": sprintf("Personal data deployment requires processing record: %v", [input.metadata.name]),
        "remediation": "Add annotation: dpa.record-id=<record-id>",
    }
}

# GDPR Article 35: Data Protection Impact Assessment (DPIA)

# Require DPIA for high-risk processing
deny[msg] {
    input.kind == "Deployment"
    input.metadata.labels["data-type"] == "sensitive"
    not input.metadata.annotations["dpia.reference"]
    msg := {
        "control": "GDPR Article 35",
        "severity": "high",
        "violation": sprintf("Sensitive data deployment requires DPIA: %v", [input.metadata.name]),
        "remediation": "Conduct DPIA and add annotation: dpia.reference=<dpia-id>",
    }
}

# GDPR Article 17: Right to Erasure (Right to be Forgotten)

# Require data retention policy
deny[msg] {
    input.kind == "PersistentVolumeClaim"
    input.metadata.labels["data-type"] == "personal"
    not input.metadata.annotations["data-retention.days"]
    msg := {
        "control": "GDPR Article 17",
        "severity": "medium",
        "violation": sprintf("Personal data volume requires retention policy: %v", [input.metadata.name]),
        "remediation": "Add annotation: data-retention.days=<number>",
    }
}
