---
name: monitoring-analytics
description: Monitor Proxmox infrastructure health and performance. Track node statistics, analyze resource utilization, and identify optimization opportunities across your cluster.
---

# Monitoring & Analytics Skill

Monitor and analyze your Proxmox infrastructure health and performance.

## What this skill does

This skill enables you to:
- Get node statistics and performance metrics
- Monitor CPU, memory, and disk utilization
- Track network performance
- Analyze VM/container performance
- Monitor resource allocation efficiency
- Identify performance bottlenecks
- Generate performance reports
- Track usage trends over time
- Plan capacity based on metrics
- Establish baselines and thresholds

## When to use this skill

Use this skill when you need to:
- Check cluster health and performance
- Monitor node resource usage
- Analyze VM/container performance
- Identify performance bottlenecks
- Troubleshoot performance issues
- Plan capacity expansion
- Generate performance reports
- Establish monitoring baselines
- Forecast resource needs
- Optimize resource allocation

## Available Tools

- `get_node_status` - Get node statistics and performance
- `get_vm_status` - Get VM performance metrics
- `get_container_status` - Get container performance metrics
- `get_cluster_resources` - Get overall cluster metrics

## Typical Workflows

### Infrastructure Health Check
1. Use `get_cluster_resources` for overall health
2. Use `get_node_status` for each node
3. Use `get_vm_status` and `get_container_status` for workload analysis
4. Generate comprehensive health report

### Performance Analysis
1. Use `get_node_status` to analyze node performance
2. Use `get_vm_status` to check VM performance
3. Identify high-utilization resources
4. Analyze performance trends
5. Recommend optimizations

### Capacity Planning
1. Use `get_cluster_resources` for current utilization
2. Use `get_node_status` for detailed metrics
3. Analyze growth trends
4. Project future capacity needs
5. Plan scaling or upgrades

### Bottleneck Identification
1. Use `get_node_status` to find high CPU/memory nodes
2. Use `get_vm_status` for resource-hungry VMs
3. Use `get_storage` for disk bottlenecks
4. Analyze performance impact
5. Recommend solutions

## Example Questions

- "What's the current cluster health and performance?"
- "Which nodes are running at high utilization?"
- "Show me the performance metrics for all VMs"
- "Are there any performance bottlenecks?"
- "Get a complete performance analysis report"
- "Which containers are consuming the most resources?"
- "What are the resource trends over time?"

## Response Format

When using this skill, I provide:
- Node statistics with CPU, memory, disk metrics
- VM/container performance data
- Utilization trends and analysis
- Bottleneck identification
- Capacity planning recommendations
- Optimization suggestions

## Best Practices

- Monitor metrics continuously
- Establish performance baselines
- Set appropriate alert thresholds
- Track metrics over time for trends
- Identify and optimize peak usage periods
- Balance load across nodes
- Monitor both physical and virtual resources
- Analyze before and after optimization
- Keep historical data for trend analysis
- Use metrics to justify capacity investments
- Monitor network performance
- Consider both current and future growth

