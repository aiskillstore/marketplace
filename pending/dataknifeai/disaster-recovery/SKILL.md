---
name: disaster-recovery
description: Implement disaster recovery and backup strategies for Proxmox. Create and manage backups, test recovery procedures, and ensure business continuity for your infrastructure.
---

# Disaster Recovery Skill

Implement and manage disaster recovery and backup strategies for Proxmox.

## What this skill does

This skill enables you to:
- Create and manage VM backups
- Create and manage container backups
- Monitor backup status and history
- Track backup storage usage
- Restore VMs from backups
- Restore containers from backups
- Create VM snapshots for recovery
- Create container snapshots for recovery
- Plan backup strategies
- Test disaster recovery procedures
- Generate backup reports
- Manage backup retention policies

## When to use this skill

Use this skill when you need to:
- Create backups of VMs and containers
- Restore from backups
- Plan backup strategies
- Monitor backup status
- Test recovery procedures
- Verify backup integrity
- Plan backup retention
- Troubleshoot backup failures
- Generate compliance reports
- Plan for disaster scenarios

## Available Tools

- `create_vm_backup` - Create a backup of a VM
- `create_container_backup` - Create a backup of a container
- `restore_vm_backup` - Restore a VM from backup
- `restore_container_backup` - Restore a container from backup
- `create_vm_snapshot` - Create VM snapshot for recovery
- `restore_vm_snapshot` - Restore from VM snapshot
- `create_container_snapshot` - Create container snapshot
- `restore_container_snapshot` - Restore from container snapshot
- `delete_backup` - Delete a backup file

## Typical Workflows

### Backup Creation & Management
1. Create backups of critical VMs and containers
2. Monitor backup completion and status
3. Verify backup storage allocation
4. Manage backup retention policies
5. Clean up old backups

### Disaster Recovery Testing
1. Create test backups of critical systems
2. Use snapshots for point-in-time recovery
3. Restore to test environment
4. Verify functionality and data integrity
5. Document recovery procedures

### Recovery Operations
1. Identify failed VM/container
2. Locate appropriate backup
3. Use `restore_vm_backup` or `restore_container_backup`
4. Verify restored system functionality
5. Complete recovery procedures

### Backup Monitoring
1. Monitor backup schedule compliance
2. Track backup storage usage
3. Monitor backup success/failure rates
4. Identify backup issues early
5. Generate audit reports

## Example Questions

- "Create a backup of VM 100 to storage"
- "What's the status of recent backups?"
- "Restore VM 200 from the backup created yesterday"
- "Show me all available backups and their sizes"
- "Create a snapshot of container 101 before updates"
- "How much storage is used for backups?"
- "Generate a disaster recovery test report"

## Response Format

When using this skill, I provide:
- Backup creation confirmations
- Backup listings with dates and sizes
- Restore operation status
- Backup storage usage analysis
- Recovery procedure documentation
- Compliance and audit reports

## Best Practices

- Implement 3-2-1 backup rule (3 copies, 2 media types, 1 offsite)
- Backup critical systems regularly
- Test restore procedures regularly
- Monitor backup success rates
- Implement backup retention policies
- Encrypt backups for security
- Store backups off-site
- Document recovery procedures
- Verify backup integrity
- Monitor backup storage capacity
- Automate backup schedules
- Test recovery before disaster strikes
- Keep backup inventories current
- Monitor backup performance
- Plan for recovery time objectives (RTO)
- Plan for recovery point objectives (RPO)

