# Infrastructure-as-Code Security Policies

OPA policies for validating infrastructure-as-code configurations in Terraform, CloudFormation, and other IaC tools.

## Table of Contents

- [Terraform Policies](#terraform-policies)
- [AWS CloudFormation](#aws-cloudformation)
- [Azure ARM Templates](#azure-arm-templates)
- [GCP Deployment Manager](#gcp-deployment-manager)

## Terraform Policies

### S3 Bucket Security

```rego
package terraform.aws.s3

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not has_encryption(resource)

    msg := sprintf("S3 bucket must have encryption enabled: %v", [resource.name])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not has_versioning(resource)

    msg := sprintf("S3 bucket must have versioning enabled: %v", [resource.name])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket_public_access_block"
    resource.change.after.block_public_acls == false

    msg := sprintf("S3 bucket must block public ACLs: %v", [resource.name])
}

has_encryption(resource) {
    resource.change.after.server_side_encryption_configuration
}

has_versioning(resource) {
    resource.change.after.versioning[_].enabled == true
}
```

### EC2 Instance Security

```rego
package terraform.aws.ec2

# Deny instances without IMDSv2
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    not resource.change.after.metadata_options.http_tokens == "required"

    msg := sprintf("EC2 instance must use IMDSv2: %v", [resource.name])
}

# Deny instances with public IPs in production
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    resource.change.after.associate_public_ip_address == true
    is_production_environment

    msg := sprintf("Production EC2 instances cannot have public IPs: %v", [resource.name])
}

# Require monitoring
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    resource.change.after.monitoring != true

    msg := sprintf("EC2 instance must have detailed monitoring enabled: %v", [resource.name])
}

is_production_environment {
    input.variables.environment == "production"
}
```

### RDS Database Security

```rego
package terraform.aws.rds

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    not resource.change.after.storage_encrypted

    msg := sprintf("RDS instance must have encryption enabled: %v", [resource.name])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    resource.change.after.publicly_accessible == true

    msg := sprintf("RDS instance cannot be publicly accessible: %v", [resource.name])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    not resource.change.after.backup_retention_period

    msg := sprintf("RDS instance must have backup retention configured: %v", [resource.name])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    resource.change.after.backup_retention_period < 7

    msg := sprintf("RDS instance must have at least 7 days backup retention: %v", [resource.name])
}
```

### IAM Policy Security

```rego
package terraform.aws.iam

# Deny wildcard actions in IAM policies
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_iam_policy"
    statement := resource.change.after.policy.Statement[_]
    statement.Action[_] == "*"

    msg := sprintf("IAM policy cannot use wildcard actions: %v", [resource.name])
}

# Deny wildcard resources
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_iam_policy"
    statement := resource.change.after.policy.Statement[_]
    statement.Resource[_] == "*"
    statement.Effect == "Allow"

    msg := sprintf("IAM policy cannot use wildcard resources with Allow: %v", [resource.name])
}

# Deny policies without conditions for sensitive actions
sensitive_actions := [
    "iam:CreateUser",
    "iam:DeleteUser",
    "iam:AttachUserPolicy",
    "kms:Decrypt",
]

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_iam_policy"
    statement := resource.change.after.policy.Statement[_]
    action := statement.Action[_]
    sensitive_actions[_] == action
    not statement.Condition

    msg := sprintf("Sensitive IAM action requires conditions: %v in %v", [action, resource.name])
}
```

### Security Group Rules

```rego
package terraform.aws.security_groups

# Deny SSH from internet
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_security_group_rule"
    resource.change.after.type == "ingress"
    resource.change.after.from_port == 22
    resource.change.after.to_port == 22
    is_open_to_internet(resource.change.after.cidr_blocks)

    msg := sprintf("Security group rule allows SSH from internet: %v", [resource.name])
}

# Deny RDP from internet
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_security_group_rule"
    resource.change.after.type == "ingress"
    resource.change.after.from_port == 3389
    resource.change.after.to_port == 3389
    is_open_to_internet(resource.change.after.cidr_blocks)

    msg := sprintf("Security group rule allows RDP from internet: %v", [resource.name])
}

# Deny unrestricted ingress
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_security_group_rule"
    resource.change.after.type == "ingress"
    is_open_to_internet(resource.change.after.cidr_blocks)
    not is_allowed_public_port(resource.change.after.from_port)

    msg := sprintf("Security group rule allows unrestricted ingress: %v", [resource.name])
}

is_open_to_internet(cidr_blocks) {
    cidr_blocks[_] == "0.0.0.0/0"
}

# Allowed public ports (HTTP/HTTPS)
is_allowed_public_port(port) {
    port == 80
}

is_allowed_public_port(port) {
    port == 443
}
```

### KMS Key Security

```rego
package terraform.aws.kms

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_kms_key"
    not resource.change.after.enable_key_rotation

    msg := sprintf("KMS key must have automatic rotation enabled: %v", [resource.name])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_kms_key"
    not resource.change.after.deletion_window_in_days

    msg := sprintf("KMS key must have deletion window configured: %v", [resource.name])
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_kms_key"
    resource.change.after.deletion_window_in_days < 30

    msg := sprintf("KMS key deletion window must be at least 30 days: %v", [resource.name])
}
```

### CloudWatch Logging

```rego
package terraform.aws.logging

# Require CloudWatch logs for Lambda
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_lambda_function"
    not has_cloudwatch_logs(resource.name)

    msg := sprintf("Lambda function must have CloudWatch logs configured: %v", [resource.name])
}

has_cloudwatch_logs(function_name) {
    resource := input.resource_changes[_]
    resource.type == "aws_cloudwatch_log_group"
    contains(resource.change.after.name, function_name)
}
```

## AWS CloudFormation

### S3 Bucket Security

```rego
package cloudformation.aws.s3

deny[msg] {
    resource := input.Resources[name]
    resource.Type == "AWS::S3::Bucket"
    not has_bucket_encryption(resource)

    msg := sprintf("S3 bucket must have encryption: %v", [name])
}

deny[msg] {
    resource := input.Resources[name]
    resource.Type == "AWS::S3::Bucket"
    not has_versioning(resource)

    msg := sprintf("S3 bucket must have versioning enabled: %v", [name])
}

has_bucket_encryption(resource) {
    resource.Properties.BucketEncryption
}

has_versioning(resource) {
    resource.Properties.VersioningConfiguration.Status == "Enabled"
}
```

### EC2 Security Groups

```rego
package cloudformation.aws.ec2

deny[msg] {
    resource := input.Resources[name]
    resource.Type == "AWS::EC2::SecurityGroup"
    rule := resource.Properties.SecurityGroupIngress[_]
    rule.CidrIp == "0.0.0.0/0"
    rule.FromPort == 22

    msg := sprintf("Security group allows SSH from internet: %v", [name])
}

deny[msg] {
    resource := input.Resources[name]
    resource.Type == "AWS::EC2::SecurityGroup"
    rule := resource.Properties.SecurityGroupIngress[_]
    rule.CidrIp == "0.0.0.0/0"
    rule.FromPort == 3389

    msg := sprintf("Security group allows RDP from internet: %v", [name])
}
```

### RDS Database

```rego
package cloudformation.aws.rds

deny[msg] {
    resource := input.Resources[name]
    resource.Type == "AWS::RDS::DBInstance"
    not resource.Properties.StorageEncrypted

    msg := sprintf("RDS instance must have encryption enabled: %v", [name])
}

deny[msg] {
    resource := input.Resources[name]
    resource.Type == "AWS::RDS::DBInstance"
    resource.Properties.PubliclyAccessible == true

    msg := sprintf("RDS instance cannot be publicly accessible: %v", [name])
}
```

## Azure ARM Templates

### Storage Account Security

```rego
package azure.storage

deny[msg] {
    resource := input.resources[_]
    resource.type == "Microsoft.Storage/storageAccounts"
    not resource.properties.supportsHttpsTrafficOnly

    msg := sprintf("Storage account must require HTTPS: %v", [resource.name])
}

deny[msg] {
    resource := input.resources[_]
    resource.type == "Microsoft.Storage/storageAccounts"
    resource.properties.allowBlobPublicAccess == true

    msg := sprintf("Storage account must disable public blob access: %v", [resource.name])
}

deny[msg] {
    resource := input.resources[_]
    resource.type == "Microsoft.Storage/storageAccounts"
    not resource.properties.minimumTlsVersion == "TLS1_2"

    msg := sprintf("Storage account must use TLS 1.2 minimum: %v", [resource.name])
}
```

### Virtual Machine Security

```rego
package azure.compute

deny[msg] {
    resource := input.resources[_]
    resource.type == "Microsoft.Compute/virtualMachines"
    not has_managed_identity(resource)

    msg := sprintf("Virtual machine should use managed identity: %v", [resource.name])
}

deny[msg] {
    resource := input.resources[_]
    resource.type == "Microsoft.Compute/virtualMachines"
    not has_disk_encryption(resource)

    msg := sprintf("Virtual machine must have disk encryption: %v", [resource.name])
}

has_managed_identity(vm) {
    vm.identity.type
}

has_disk_encryption(vm) {
    vm.properties.storageProfile.osDisk.encryptionSettings
}
```

### Network Security Groups

```rego
package azure.network

deny[msg] {
    resource := input.resources[_]
    resource.type == "Microsoft.Network/networkSecurityGroups"
    rule := resource.properties.securityRules[_]
    rule.properties.access == "Allow"
    rule.properties.sourceAddressPrefix == "*"
    rule.properties.destinationPortRange == "22"

    msg := sprintf("NSG allows SSH from internet: %v", [resource.name])
}

deny[msg] {
    resource := input.resources[_]
    resource.type == "Microsoft.Network/networkSecurityGroups"
    rule := resource.properties.securityRules[_]
    rule.properties.access == "Allow"
    rule.properties.sourceAddressPrefix == "*"
    rule.properties.destinationPortRange == "3389"

    msg := sprintf("NSG allows RDP from internet: %v", [resource.name])
}
```

## GCP Deployment Manager

### GCS Bucket Security

```rego
package gcp.storage

deny[msg] {
    resource := input.resources[_]
    resource.type == "storage.v1.bucket"
    not has_uniform_access(resource)

    msg := sprintf("GCS bucket must use uniform bucket-level access: %v", [resource.name])
}

deny[msg] {
    resource := input.resources[_]
    resource.type == "storage.v1.bucket"
    not has_encryption(resource)

    msg := sprintf("GCS bucket must have encryption configured: %v", [resource.name])
}

has_uniform_access(bucket) {
    bucket.properties.iamConfiguration.uniformBucketLevelAccess.enabled == true
}

has_encryption(bucket) {
    bucket.properties.encryption
}
```

### Compute Instance Security

```rego
package gcp.compute

deny[msg] {
    resource := input.resources[_]
    resource.type == "compute.v1.instance"
    not has_service_account(resource)

    msg := sprintf("Compute instance should use service account: %v", [resource.name])
}

deny[msg] {
    resource := input.resources[_]
    resource.type == "compute.v1.instance"
    not has_disk_encryption(resource)

    msg := sprintf("Compute instance must have disk encryption: %v", [resource.name])
}

has_service_account(instance) {
    instance.properties.serviceAccounts
}

has_disk_encryption(instance) {
    instance.properties.disks[_].diskEncryptionKey
}
```

### Firewall Rules

```rego
package gcp.network

deny[msg] {
    resource := input.resources[_]
    resource.type == "compute.v1.firewall"
    resource.properties.direction == "INGRESS"
    "0.0.0.0/0" == resource.properties.sourceRanges[_]
    allowed := resource.properties.allowed[_]
    allowed.ports[_] == "22"

    msg := sprintf("Firewall rule allows SSH from internet: %v", [resource.name])
}

deny[msg] {
    resource := input.resources[_]
    resource.type == "compute.v1.firewall"
    resource.properties.direction == "INGRESS"
    "0.0.0.0/0" == resource.properties.sourceRanges[_]
    allowed := resource.properties.allowed[_]
    allowed.ports[_] == "3389"

    msg := sprintf("Firewall rule allows RDP from internet: %v", [resource.name])
}
```

## Conftest Integration

Example using Conftest for Terraform validation:

```bash
# Install conftest
brew install conftest

# Create policy directory
mkdir -p policy

# Write policy (policy/terraform.rego)
package main

deny[msg] {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket"
  not resource.change.after.server_side_encryption_configuration
  msg := sprintf("S3 bucket must have encryption: %v", [resource.name])
}

# Generate Terraform plan
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json

# Run conftest
conftest test tfplan.json
```

## CI/CD Integration

### GitHub Actions

```yaml
name: IaC Policy Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup OPA
        uses: open-policy-agent/setup-opa@v2

      - name: Generate Terraform Plan
        run: |
          terraform init
          terraform plan -out=tfplan.binary
          terraform show -json tfplan.binary > tfplan.json

      - name: Validate with OPA
        run: |
          opa eval --data policies/ --input tfplan.json \
            --format pretty 'data.terraform.deny' > violations.txt

          if [ -s violations.txt ]; then
            cat violations.txt
            exit 1
          fi
```

### GitLab CI

```yaml
iac-validation:
  image: openpolicyagent/opa:latest
  script:
    - terraform init
    - terraform plan -out=tfplan.binary
    - terraform show -json tfplan.binary > tfplan.json
    - opa eval --data policies/ --input tfplan.json 'data.terraform.deny'
  only:
    - merge_requests
```

## References

- [Conftest](https://www.conftest.dev/)
- [Terraform Sentinel](https://www.terraform.io/docs/cloud/sentinel/index.html)
- [AWS CloudFormation Guard](https://github.com/aws-cloudformation/cloudformation-guard)
- [Azure Policy](https://docs.microsoft.com/en-us/azure/governance/policy/)
- [Checkov](https://www.checkov.io/)
