---
name: infrastructure-reporting
description: Generate comprehensive network infrastructure reports including health status, performance analysis, security audits, and capacity planning recommendations.
---

# Infrastructure Reporting Skill

Generate comprehensive reports for network health, performance, security, and capacity planning.

## What this skill does

This skill enables you to:
- Generate network health and status reports
- Create performance analysis reports
- Generate security audit and compliance reports
- Create device inventory reports
- Produce capacity planning recommendations
- Generate multi-site comparison reports
- Create executive summary dashboards

## When to use this skill

Use this skill when you need to:
- Create periodic health check reports
- Document network performance
- Generate audit documentation for compliance
- Plan infrastructure upgrades
- Compare performance across sites
- Create dashboards for monitoring
- Generate executive reports for stakeholders
- Document security posture

## Available Tools

- All network tools combined for comprehensive reporting
- `get_network_sites` - Site overview
- `get_site_health` - Health metrics
- `get_network_devices` - Device inventory
- `get_network_device_stats` - Performance data
- `get_network_clients` - Client information
- `get_client_stats` - Client metrics
- `get_wifi_networks` - WiFi configuration
- `get_firewall_zones` - Security zones
- `get_acl_rules` - Access controls
- `get_network_info` - System information

## Typical Workflows

### Weekly Health Report
1. Gather data from all sites using `get_site_health`
2. Use `get_network_devices` to list devices
3. Use `get_network_device_stats` for performance
4. Summarize findings with recommendations
5. Create executive summary

### Monthly Performance Report
1. Use `get_network_device_stats` for device metrics
2. Use `get_client_stats` for client performance
3. Analyze trends and patterns
4. Create performance dashboards
5. Identify improvement opportunities

### Security & Compliance Audit
1. Use `get_firewall_zones` for network segmentation
2. Use `get_acl_rules` for access controls
3. Use `get_network_info` for system info
4. Document security posture
5. Create audit trail and recommendations

### Capacity Planning Report
1. Gather inventory with `get_network_devices`
2. Analyze usage with `get_network_device_stats`
3. Project future needs
4. Recommend upgrades
5. Estimate timelines and costs

## Example Questions

- "Generate a weekly health report"
- "Create a monthly performance report"
- "Generate a security audit report"
- "Perform capacity planning analysis"
- "Compare health across all sites"
- "Create an executive dashboard"
- "Generate a device inventory report"
- "Create a compliance audit report"

## Response Format

When using this skill, I provide:
- Executive summary with key findings
- Detailed data analysis with metrics
- Visual representations (tables, charts)
- Trend analysis and forecasting
- Specific recommendations with priority
- Risk assessments
- Action items with timelines
- Comparison across sites (if applicable)
