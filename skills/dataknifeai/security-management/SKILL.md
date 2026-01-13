---
name: security-management
description: Manage security policies, firewall zones, access control rules (ACLs), and guest network access. Perform comprehensive security audits and compliance reviews.
---

# Security Management Skill

Manage your UniFi network security including firewall zones, access controls, and guest policies.

## What this skill does

This skill enables you to:
- View and manage firewall zones and network segmentation
- Review and manage access control rules (ACLs)
- Monitor and manage guest network access via hotspot vouchers
- Perform comprehensive security audits
- Verify security policies and configurations
- Generate security compliance reports

## When to use this skill

Use this skill when you need to:
- Review firewall configuration and zone setup
- Audit access control policies
- Manage guest network access and vouchers
- Ensure security compliance
- Plan network segmentation
- Troubleshoot security-related issues
- Generate security audit reports

## Available Tools

- `get_firewall_zones` - List and view firewall zones
- `get_acl_rules` - List and review access control rules
- `get_hotspot_vouchers` - List and manage guest access vouchers
- `get_network_info` - Get system information for compliance verification

## Typical Workflows

### Security Audit
1. Use `get_firewall_zones` to verify zone configuration
2. Use `get_acl_rules` to review access control policies
3. Use `get_hotspot_vouchers` to check guest access setup
4. Use `get_network_info` for system-level security info
5. Generate audit report with findings and recommendations

### Guest Access Management
1. Use `get_hotspot_vouchers` to list active vouchers
2. Check expiration dates and status
3. Verify guest network policies
4. Plan voucher lifecycle management

### Network Segmentation Review
1. Use `get_firewall_zones` to understand zone setup
2. Verify zone isolation policies
3. Review intra-zone communication rules
4. Assess network segmentation adequacy

## Example Questions

- "Show all firewall zones and their configuration"
- "Review all access control rules"
- "List active guest network vouchers and their status"
- "Are there any expired or expiring vouchers?"
- "Perform a complete security audit"
- "Verify network segmentation setup"
- "Check security compliance status"

## Response Format

When using this skill, I provide:
- Firewall zone listings with descriptions
- Access control rule details with purposes
- Guest access voucher status and expiration dates
- Security assessment findings
- Compliance status
- Specific recommendations for improvements
- Risk assessments where applicable

## Best Practices

- Review firewall zones quarterly
- Audit access control rules regularly
- Monitor guest voucher expiration dates
- Document security policy changes
- Test zone isolation periodically
- Review guest access patterns
- Keep audit logs for compliance
- Implement principle of least privilege
- Segment networks by trust level and function
