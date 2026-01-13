---
name: network-monitoring
description: Monitor UniFi network infrastructure including sites, devices, and system health. Diagnose connectivity issues, track device performance, and generate network diagnostics.
---

# Network Monitoring Skill

Monitor and diagnose your UniFi network infrastructure with comprehensive site, device, and health monitoring.

## What this skill does

This skill enables you to:
- Monitor all configured UniFi sites and their health status
- Track device status and performance metrics
- Diagnose network connectivity issues
- Generate network diagnostic reports
- Compare infrastructure across multiple sites

## When to use this skill

Use this skill when you need to:
- Check overall network health and status
- Identify offline or underperforming devices
- Diagnose connectivity problems
- Get device-specific statistics (CPU, memory, uptime)
- Compare site health across your infrastructure
- Generate diagnostic reports for troubleshooting

## Available Tools

- `get_network_sites` - List all configured sites
- `get_site_health` - Get comprehensive health status for a site
- `get_network_devices` - List all devices in a site
- `get_network_device_stats` - Get detailed device statistics
- `get_network_info` - Get system information and metrics

## Typical Workflows

### Site Health Check
1. Use `get_network_sites` to list all sites
2. Use `get_site_health` for each site to check status
3. Identify any sites with degraded health
4. Drill down with `get_network_devices` to find the issue

### Device Performance Analysis
1. Use `get_network_devices` to list devices
2. Use `get_network_device_stats` to get detailed metrics
3. Identify devices with high CPU/memory usage
4. Look for patterns of underperformance

### Network Troubleshooting
1. Start with `get_site_health` to identify problems
2. Use `get_network_devices` to list all devices
3. Use `get_network_device_stats` to analyze performance
4. Check `get_network_info` for system-level issues

## Example Questions

- "What's the health status of all my sites?"
- "Which devices in my network are offline?"
- "Get device statistics for high CPU usage"
- "Compare health across all my sites"
- "Diagnose why connectivity is slow"
- "Generate a network diagnostic report"

## Response Format

When using this skill, I provide:
- Health status indicators (excellent, good, minor issues, major issues)
- Device counts and status breakdowns
- Performance metrics (CPU, memory, uptime)
- Specific problem identification with recommendations
- Actionable diagnostics for troubleshooting

## Best Practices

- Check site health first before diving into individual devices
- Correlate device statistics with reported issues
- Use multiple data points to identify root causes
- Document patterns for trend analysis over time
- Escalate hardware issues when performance metrics indicate failure
