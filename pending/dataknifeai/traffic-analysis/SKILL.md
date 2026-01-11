---
name: traffic-analysis
description: Analyze network traffic patterns, identify top applications and bandwidth usage, and optimize traffic management. Perform DPI-based traffic classification.
---

# Traffic Analysis Skill

Analyze network traffic patterns and identify top applications and bandwidth consumers.

## What this skill does

This skill enables you to:
- Identify applications in use with DPI classification
- Analyze bandwidth usage by client and application
- Identify heavy users and bandwidth-intensive applications
- Track traffic patterns and trends
- Recommend traffic optimization strategies
- Perform DPI-based network analytics

## When to use this skill

Use this skill when you need to:
- Identify what applications are using bandwidth
- Find bandwidth-heavy users or applications
- Optimize traffic policies
- Analyze traffic distribution
- Plan bandwidth upgrades
- Troubleshoot congestion issues
- Generate traffic analysis reports

## Available Tools

- `get_dpi_categories` - Get DPI application categories in use
- `get_client_stats` - Get client bandwidth and traffic statistics
- `get_network_devices` - Get device-level traffic information
- `get_network_device_stats` - Get detailed device throughput metrics

## Typical Workflows

### Traffic Classification
1. Use `get_dpi_categories` to see application categories in use
2. Understand traffic classification (streaming, gaming, etc.)
3. Identify major application types
4. Plan QoS policies based on categories

### Bandwidth Analysis
1. Use `get_client_stats` to get client bandwidth usage
2. Identify top bandwidth consumers
3. Analyze bandwidth distribution
4. Correlate with application categories
5. Recommend bandwidth allocation changes

### Performance Troubleshooting
1. Use `get_network_device_stats` to check throughput
2. Use `get_client_stats` to analyze client bandwidth
3. Use `get_dpi_categories` to identify congestion causes
4. Correlate metrics to identify bottlenecks

## Example Questions

- "What applications are using the most bandwidth?"
- "Show top 10 bandwidth-consuming clients"
- "Analyze traffic by DPI category"
- "Identify bandwidth bottlenecks"
- "Generate traffic analysis report"
- "Which applications should we prioritize?"
- "Recommend QoS policies based on traffic"

## Response Format

When using this skill, I provide:
- DPI application categories and traffic volumes
- Top bandwidth consumers (clients)
- Traffic distribution analysis
- Bandwidth utilization patterns
- QoS recommendations
- Congestion identification
- Optimization suggestions

## Best Practices

- Monitor traffic patterns regularly
- Correlate DPI categories with application policy
- Use traffic data to justify bandwidth upgrades
- Implement QoS based on application categories
- Track traffic trends over time
- Monitor for unusual traffic patterns
- Balance bandwidth allocation fairly
- Document traffic policies and rationale
- Review and adjust policies quarterly
