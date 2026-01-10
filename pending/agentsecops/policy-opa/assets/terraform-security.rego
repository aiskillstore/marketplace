package terraform.security

import future.keywords.if

# AWS S3 Bucket Security

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not has_encryption(resource)
    msg := {
        "resource": resource.name,
        "type": "aws_s3_bucket",
        "severity": "high",
        "violation": "S3 bucket must have encryption enabled",
        "remediation": "Add server_side_encryption_configuration block",
    }
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not has_versioning(resource)
    msg := {
        "resource": resource.name,
        "type": "aws_s3_bucket",
        "severity": "medium",
        "violation": "S3 bucket should have versioning enabled",
        "remediation": "Add versioning configuration with enabled = true",
    }
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket_public_access_block"
    resource.change.after.block_public_acls == false
    msg := {
        "resource": resource.name,
        "type": "aws_s3_bucket_public_access_block",
        "severity": "high",
        "violation": "S3 bucket must block public ACLs",
        "remediation": "Set block_public_acls = true",
    }
}

has_encryption(resource) {
    resource.change.after.server_side_encryption_configuration
}

has_versioning(resource) {
    resource.change.after.versioning[_].enabled == true
}

# AWS EC2 Security

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    not resource.change.after.metadata_options.http_tokens == "required"
    msg := {
        "resource": resource.name,
        "type": "aws_instance",
        "severity": "high",
        "violation": "EC2 instance must use IMDSv2",
        "remediation": "Set metadata_options.http_tokens = required",
    }
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    resource.change.after.associate_public_ip_address == true
    is_production
    msg := {
        "resource": resource.name,
        "type": "aws_instance",
        "severity": "high",
        "violation": "Production EC2 instances cannot have public IPs",
        "remediation": "Set associate_public_ip_address = false",
    }
}

is_production {
    input.variables.environment == "production"
}

# AWS RDS Security

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    not resource.change.after.storage_encrypted
    msg := {
        "resource": resource.name,
        "type": "aws_db_instance",
        "severity": "high",
        "violation": "RDS instance must have encryption enabled",
        "remediation": "Set storage_encrypted = true",
    }
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    resource.change.after.publicly_accessible == true
    msg := {
        "resource": resource.name,
        "type": "aws_db_instance",
        "severity": "critical",
        "violation": "RDS instance cannot be publicly accessible",
        "remediation": "Set publicly_accessible = false",
    }
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    backup_retention := resource.change.after.backup_retention_period
    backup_retention < 7
    msg := {
        "resource": resource.name,
        "type": "aws_db_instance",
        "severity": "medium",
        "violation": "RDS instance must have at least 7 days backup retention",
        "remediation": "Set backup_retention_period >= 7",
    }
}

# AWS IAM Security

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_iam_policy"
    statement := resource.change.after.policy.Statement[_]
    statement.Action[_] == "*"
    msg := {
        "resource": resource.name,
        "type": "aws_iam_policy",
        "severity": "high",
        "violation": "IAM policy cannot use wildcard actions",
        "remediation": "Specify explicit actions instead of *",
    }
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_iam_policy"
    statement := resource.change.after.policy.Statement[_]
    statement.Resource[_] == "*"
    statement.Effect == "Allow"
    msg := {
        "resource": resource.name,
        "type": "aws_iam_policy",
        "severity": "high",
        "violation": "IAM policy cannot use wildcard resources with Allow",
        "remediation": "Specify explicit resource ARNs",
    }
}

# AWS Security Group Rules

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_security_group_rule"
    resource.change.after.type == "ingress"
    resource.change.after.from_port == 22
    is_open_to_internet(resource.change.after.cidr_blocks)
    msg := {
        "resource": resource.name,
        "type": "aws_security_group_rule",
        "severity": "critical",
        "violation": "Security group allows SSH from internet",
        "remediation": "Restrict SSH access to specific IP ranges",
    }
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_security_group_rule"
    resource.change.after.type == "ingress"
    resource.change.after.from_port == 3389
    is_open_to_internet(resource.change.after.cidr_blocks)
    msg := {
        "resource": resource.name,
        "type": "aws_security_group_rule",
        "severity": "critical",
        "violation": "Security group allows RDP from internet",
        "remediation": "Restrict RDP access to specific IP ranges",
    }
}

is_open_to_internet(cidr_blocks) {
    cidr_blocks[_] == "0.0.0.0/0"
}

# AWS KMS Security

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_kms_key"
    not resource.change.after.enable_key_rotation
    msg := {
        "resource": resource.name,
        "type": "aws_kms_key",
        "severity": "medium",
        "violation": "KMS key must have automatic rotation enabled",
        "remediation": "Set enable_key_rotation = true",
    }
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_kms_key"
    deletion_window := resource.change.after.deletion_window_in_days
    deletion_window < 30
    msg := {
        "resource": resource.name,
        "type": "aws_kms_key",
        "severity": "medium",
        "violation": "KMS key deletion window must be at least 30 days",
        "remediation": "Set deletion_window_in_days >= 30",
    }
}
