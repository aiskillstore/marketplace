---
name: cluster-management
description: Monitor and manage Proxmox cluster nodes, resources, and infrastructure health. Track node status, cluster quorum, and resource allocation across your virtualization platform.
---

# Cluster Management Skill

Monitor and manage your Proxmox VE cluster infrastructure and node health.

## What this skill does

This skill enables you to:
- View all nodes in the Proxmox cluster
- Monitor node status and health
- Track cluster resources and utilization
- Analyze node performance metrics
- Monitor cluster quorum status
- Plan cluster scaling and expansion
- Identify resource bottlenecks
- Generate cluster health reports

## When to use this skill

Use this skill when you need to:
- Check overall cluster status
- Monitor node health and performance
- Verify cluster quorum
- Plan resource allocation
- Troubleshoot node issues
- Analyze cluster capacity
- Generate infrastructure reports
- Plan cluster upgrades or maintenance

## Available Tools

- `get_nodes` - List all nodes in the cluster
- `get_node_status` - Get detailed status of a specific node
- `get_cluster_resources` - Get all cluster resources (nodes, VMs, containers)

## Typical Workflows

### Cluster Health Check
1. Use `get_cluster_resources` for overall cluster status
2. Use `get_nodes` to list all nodes
3. Use `get_node_status` for each node to check health
4. Generate cluster health report

### Node Monitoring
1. Use `get_nodes` to list all cluster nodes
2. Use `get_node_status` to check individual node performance
3. Monitor CPU, memory, and storage metrics
4. Identify performance issues

### Capacity Planning
1. Use `get_cluster_resources` to analyze current usage
2. Use `get_node_status` for detailed node metrics
3. Project growth and identify bottlenecks
4. Plan scaling or upgrades

## Example Questions

- "Show me the status of all cluster nodes"
- "Is the cluster healthy and properly configured?"
- "What's the resource utilization across the cluster?"
- "Which nodes have capacity issues?"
- "Get a complete cluster infrastructure report"
- "Are there any offline or degraded nodes?"
- "What's the cluster quorum status?"

## Response Format

When using this skill, I provide:
- Complete list of cluster nodes with status
- Node health and performance metrics
- Cluster resource overview and utilization
- Quorum and cluster configuration status
- Recommendations for optimization

## Best Practices

- Monitor cluster health regularly
- Maintain proper node quorum (3+ nodes recommended)
- Balance resource allocation across nodes
- Plan maintenance during off-hours
- Test cluster failover scenarios
- Keep all nodes updated
- Monitor network connectivity between nodes
- Document cluster configuration changes

