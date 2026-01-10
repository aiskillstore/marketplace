# Checkov Custom Policy Development Guide

Complete guide for creating organization-specific security policies in Python and YAML.

## Overview

Custom policies allow you to enforce organization-specific security requirements beyond Checkov's built-in checks. Policies can be written in:

- **Python**: Full programmatic control, graph-based analysis
- **YAML**: Simple attribute checks, easy to maintain

## Python-Based Custom Policies

### Basic Resource Check

```python
# custom_checks/require_resource_tags.py
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class RequireResourceTags(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all resources have required tags"
        id = "CKV_AWS_CUSTOM_001"
        supported_resources = ['aws_*']  # All AWS resources
        categories = [CheckCategories.CONVENTION]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """Check if resource has required tags."""
        required_tags = ['Environment', 'Owner', 'CostCenter']

        tags = conf.get('tags')
        if not tags or not isinstance(tags, list):
            return CheckResult.FAILED

        tag_dict = tags[0] if tags else {}

        for required_tag in required_tags:
            if required_tag not in tag_dict:
                self.evaluated_keys = ['tags']
                return CheckResult.FAILED

        return CheckResult.PASSED

check = RequireResourceTags()
```

### Graph-Based Policy

```python
# custom_checks/s3_bucket_policy_public.py
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class S3BucketPolicyNotPublic(BaseResourceCheck):
    def __init__(self):
        name = "Ensure S3 bucket policy doesn't allow public access"
        id = "CKV_AWS_CUSTOM_002"
        supported_resources = ['aws_s3_bucket_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """Scan S3 bucket policy for public access."""
        policy = conf.get('policy')
        if not policy:
            return CheckResult.PASSED

        import json
        try:
            policy_doc = json.loads(policy[0]) if isinstance(policy, list) else json.loads(policy)
        except (json.JSONDecodeError, TypeError):
            return CheckResult.UNKNOWN

        statements = policy_doc.get('Statement', [])
        for statement in statements:
            effect = statement.get('Effect')
            principal = statement.get('Principal', {})

            # Check for public access
            if effect == 'Allow':
                if principal == '*' or principal.get('AWS') == '*':
                    return CheckResult.FAILED

        return CheckResult.PASSED

check = S3BucketPolicyNotPublic()
```

### Connection-Aware Check (Graph)

```python
# custom_checks/ec2_in_private_subnet.py
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class EC2InPrivateSubnet(BaseResourceCheck):
    def __init__(self):
        name = "Ensure EC2 instances are in private subnets"
        id = "CKV_AWS_CUSTOM_003"
        supported_resources = ['aws_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf, entity_type):
        """Check if EC2 instance is in private subnet."""
        subnet_id = conf.get('subnet_id')
        if not subnet_id:
            return CheckResult.PASSED

        # Use graph to find connected subnet
        # This requires access to the graph context
        # Implementation depends on Checkov version

        return CheckResult.UNKNOWN  # Implement graph logic

check = EC2InPrivateSubnet()
```

## YAML-Based Custom Policies

### Simple Attribute Check

```yaml
# custom_checks/s3_lifecycle.yaml
metadata:
  id: "CKV_AWS_CUSTOM_004"
  name: "Ensure S3 buckets have lifecycle policies"
  category: "BACKUP_AND_RECOVERY"
  severity: "MEDIUM"

definition:
  cond_type: "attribute"
  resource_types:
    - "aws_s3_bucket"
  attribute: "lifecycle_rule"
  operator: "exists"
```

### Complex Logic

```yaml
# custom_checks/rds_multi_az.yaml
metadata:
  id: "CKV_AWS_CUSTOM_005"
  name: "Ensure RDS instances are multi-AZ for production"
  category: "BACKUP_AND_RECOVERY"
  severity: "HIGH"

definition:
  or:
    - cond_type: "attribute"
      resource_types:
        - "aws_db_instance"
      attribute: "multi_az"
      operator: "equals"
      value: true

    - and:
        - cond_type: "attribute"
          resource_types:
            - "aws_db_instance"
          attribute: "tags.Environment"
          operator: "not_equals"
          value: "production"
```

### Kubernetes Policy

```yaml
# custom_checks/k8s_service_account.yaml
metadata:
  id: "CKV_K8S_CUSTOM_001"
  name: "Ensure pods use dedicated service accounts"
  category: "IAM"
  severity: "HIGH"

definition:
  cond_type: "attribute"
  resource_types:
    - "Pod"
    - "Deployment"
    - "StatefulSet"
    - "DaemonSet"
  attribute: "spec.serviceAccountName"
  operator: "not_equals"
  value: "default"
```

## Policy Structure

### Python Policy Template

```python
#!/usr/bin/env python3
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class MyCustomCheck(BaseResourceCheck):
    def __init__(self):
        # Metadata
        name = "Check description"
        id = "CKV_[PROVIDER]_CUSTOM_[NUMBER]"  # e.g., CKV_AWS_CUSTOM_001
        supported_resources = ['resource_type']  # e.g., ['aws_s3_bucket']
        categories = [CheckCategories.CATEGORY]  # See categories below
        guideline = "https://docs.example.com/security-policy"

        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            guideline=guideline
        )

    def scan_resource_conf(self, conf, entity_type=None):
        """
        Scan resource configuration for compliance.

        Args:
            conf: Resource configuration dictionary
            entity_type: Resource type (optional)

        Returns:
            CheckResult.PASSED, CheckResult.FAILED, or CheckResult.UNKNOWN
        """
        # Implementation
        if self.check_condition(conf):
            return CheckResult.PASSED

        self.evaluated_keys = ['attribute_that_failed']
        return CheckResult.FAILED

    def get_inspected_key(self):
        """Return the key that was checked."""
        return 'attribute_name'

check = MyCustomCheck()
```

### Check Categories

```python
from checkov.common.models.enums import CheckCategories

# Available categories:
CheckCategories.IAM
CheckCategories.NETWORKING
CheckCategories.ENCRYPTION
CheckCategories.LOGGING
CheckCategories.BACKUP_AND_RECOVERY
CheckCategories.CONVENTION
CheckCategories.SECRETS
CheckCategories.KUBERNETES
CheckCategories.API_SECURITY
CheckCategories.SUPPLY_CHAIN
```

## Loading Custom Policies

### Directory Structure

```
custom_checks/
├── aws/
│   ├── require_tags.py
│   ├── s3_lifecycle.yaml
│   └── rds_backups.py
├── kubernetes/
│   ├── require_resource_limits.py
│   └── security_context.yaml
└── azure/
    └── storage_encryption.py
```

### Load Policies

```bash
# Load from directory
checkov -d ./terraform --external-checks-dir ./custom_checks

# Load specific policy
checkov -d ./terraform --external-checks-git https://github.com/org/policies.git

# List loaded custom checks
checkov -d ./terraform --external-checks-dir ./custom_checks --list
```

## Testing Custom Policies

### Unit Testing

```python
# tests/test_require_tags.py
import unittest
from custom_checks.require_resource_tags import RequireResourceTags
from checkov.common.models.enums import CheckResult

class TestRequireResourceTags(unittest.TestCase):
    def setUp(self):
        self.check = RequireResourceTags()

    def test_pass_with_all_tags(self):
        resource_conf = {
            'tags': [{
                'Environment': 'production',
                'Owner': 'team@example.com',
                'CostCenter': 'engineering'
            }]
        }
        result = self.check.scan_resource_conf(resource_conf)
        self.assertEqual(result, CheckResult.PASSED)

    def test_fail_missing_tag(self):
        resource_conf = {
            'tags': [{
                'Environment': 'production',
                'Owner': 'team@example.com'
                # Missing CostCenter
            }]
        }
        result = self.check.scan_resource_conf(resource_conf)
        self.assertEqual(result, CheckResult.FAILED)

    def test_fail_no_tags(self):
        resource_conf = {}
        result = self.check.scan_resource_conf(resource_conf)
        self.assertEqual(result, CheckResult.FAILED)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```bash
# Test against sample infrastructure
checkov -d ./tests/fixtures/terraform \
  --external-checks-dir ./custom_checks \
  --check CKV_AWS_CUSTOM_001

# Verify output format
checkov -d ./tests/fixtures/terraform \
  --external-checks-dir ./custom_checks \
  -o json | jq '.results.failed_checks[] | select(.check_id == "CKV_AWS_CUSTOM_001")'
```

## Common Patterns

### Pattern 1: Naming Convention Check

```python
import re

class ResourceNamingConvention(BaseResourceCheck):
    def scan_resource_conf(self, conf):
        """Enforce naming convention: env-app-resource"""
        pattern = r'^(dev|staging|prod)-[a-z]+-[a-z0-9-]+$'

        name = conf.get('name')
        if not name or not isinstance(name, list):
            return CheckResult.FAILED

        resource_name = name[0] if isinstance(name[0], str) else str(name[0])

        if not re.match(pattern, resource_name):
            self.evaluated_keys = ['name']
            return CheckResult.FAILED

        return CheckResult.PASSED
```

### Pattern 2: Environment-Specific Requirements

```python
class ProductionEncryption(BaseResourceCheck):
    def scan_resource_conf(self, conf):
        """Require encryption for production resources."""
        tags = conf.get('tags', [{}])[0]
        environment = tags.get('Environment', '')

        # Only enforce for production
        if environment.lower() != 'production':
            return CheckResult.PASSED

        # Check encryption
        encryption_enabled = conf.get('server_side_encryption_configuration')
        if not encryption_enabled:
            return CheckResult.FAILED

        return CheckResult.PASSED
```

### Pattern 3: Cost Optimization

```python
class EC2InstanceSizing(BaseResourceCheck):
    def scan_resource_conf(self, conf):
        """Prevent oversized instances in non-production."""
        tags = conf.get('tags', [{}])[0]
        environment = tags.get('Environment', '')

        # Only restrict non-production
        if environment.lower() == 'production':
            return CheckResult.PASSED

        instance_type = conf.get('instance_type', [''])[0]
        oversized_types = ['c5.9xlarge', 'c5.12xlarge', 'c5.18xlarge']

        if instance_type in oversized_types:
            self.evaluated_keys = ['instance_type']
            return CheckResult.FAILED

        return CheckResult.PASSED
```

## Best Practices

1. **ID Convention**: Use `CKV_[PROVIDER]_CUSTOM_[NUMBER]` format
2. **Documentation**: Include guideline URL in check metadata
3. **Error Handling**: Return `CheckResult.UNKNOWN` for ambiguous cases
4. **Performance**: Minimize complex operations in scan loops
5. **Testing**: Write unit tests for all custom policies
6. **Versioning**: Track policy versions in version control
7. **Review Process**: Require security team review before deployment

## Troubleshooting

### Policy Not Loading

```bash
# Debug loading
checkov -d ./terraform --external-checks-dir ./custom_checks -v

# Verify syntax
python3 custom_checks/my_policy.py

# Check for import errors
python3 -c "import custom_checks.my_policy"
```

### Policy Not Triggering

```bash
# Verify resource type matches
checkov -d ./terraform --external-checks-dir ./custom_checks --list

# Test with specific check
checkov -d ./terraform --check CKV_AWS_CUSTOM_001 -v
```

## Additional Resources

- [Checkov Custom Policies Documentation](https://www.checkov.io/3.Custom%20Policies/Custom%20Policies%20Overview.html)
- [Python Policy Examples](https://github.com/bridgecrewio/checkov/tree/master/checkov/terraform/checks)
- [YAML Policy Examples](https://github.com/bridgecrewio/checkov/tree/master/checkov/terraform/checks/graph_checks)
