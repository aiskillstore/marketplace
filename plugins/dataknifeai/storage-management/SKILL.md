---
name: storage-management
description: Manage storage devices and resources in Proxmox. Monitor storage usage, allocate resources, and plan storage expansion for your virtualization infrastructure.
---

# Storage Management Skill

Manage and optimize storage in your Proxmox environment.

## What this skill does

This skill enables you to:
- List all storage devices in the cluster
- Get storage device details and capacity
- Monitor storage usage and utilization
- Track storage allocation per VM/container
- Analyze storage performance
- Plan storage expansion
- Manage storage pools
- Monitor storage health
- Identify storage bottlenecks
- Generate storage reports

## When to use this skill

Use this skill when you need to:
- Check available storage capacity
- Monitor storage utilization
- Plan storage expansion
- Analyze storage performance
- Troubleshoot storage issues
- Allocate storage to VMs/containers
- Monitor storage device health
- Generate capacity planning reports
- Optimize storage allocation

## Available Tools

- `get_storage` - Get all storage devices in the cluster
- `get_node_storage` - Get storage devices for a specific node

## Typical Workflows

### Storage Capacity Planning
1. Use `get_storage` to view all storage devices
2. Use `get_node_storage` for node-specific analysis
3. Analyze current usage and growth trends
4. Plan storage expansion or upgrades
5. Generate capacity report

### Storage Monitoring
1. Use `get_storage` to view overall utilization
2. Use `get_node_storage` for detailed per-node analysis
3. Monitor critical thresholds
4. Track usage trends over time
5. Alert on capacity issues

### Storage Optimization
1. Use `get_storage` to identify underutilized storage
2. Use `get_node_storage` to analyze node-level usage
3. Rebalance storage allocation
4. Archive or consolidate data
5. Optimize storage pool configuration

### Storage Troubleshooting
1. Use `get_storage` to verify device availability
2. Use `get_node_storage` to diagnose node-specific issues
3. Check for I/O errors or performance degradation
4. Verify RAID status and redundancy
5. Analyze performance metrics

## Example Questions

- "Show me all storage devices and their capacity"
- "What's the storage usage per node?"
- "Which storage devices are near capacity?"
- "How much free space do we have across all storage?"
- "Get storage capacity and planning report"
- "Are there any storage performance issues?"
- "Show storage allocation across the cluster"

## Response Format

When using this skill, I provide:
- Storage device listings with capacity/usage
- Per-node storage analysis
- Utilization percentages and trends
- Available capacity summary
- Bottleneck identification
- Expansion recommendations

## Best Practices

- Monitor storage capacity regularly
- Maintain 20-30% free space for performance
- Plan storage expansion proactively
- Implement redundancy for critical storage
- Monitor RAID health and status
- Use appropriate storage tiers for workload types
- Implement data archival policies
- Monitor I/O performance and latency
- Document storage configuration
- Test disaster recovery procedures
- Plan for future growth
- Use snapshots for backup and recovery

