---
name: infrastructure-management
description: Manage network hosts and devices across all UniFi sites. Monitor host status, device configuration, and infrastructure health for comprehensive inventory management.
---

# Infrastructure Management Skill

Manage and monitor network hosts and devices across your UniFi infrastructure.

## What this skill does

This skill enables you to:
- View all hosts across all sites
- Get detailed host information and status
- View all network devices in your infrastructure
- Get detailed device configuration and status
- Filter infrastructure by site
- Monitor host and device health
- Track infrastructure inventory
- Analyze resource distribution across sites

## When to use this skill

Use this skill when you need to:
- Check host and device inventory
- Monitor infrastructure status
- Get device configuration details
- Analyze site-specific infrastructure
- Troubleshoot connectivity issues
- Plan capacity expansion
- Generate infrastructure reports
- Verify device assignments

## Available Tools

- `list_hosts` - List all hosts across all sites
- `get_host_details` - Get detailed information about a specific host
- `get_hosts_by_site` - Get all hosts in a specific site
- `list_devices` - List all network devices across all sites
- `get_device_details` - Get detailed information about a specific device
- `get_devices_by_site` - Get all devices in a specific site

## Typical Workflows

### Infrastructure Inventory
1. Use `list_hosts` to get all hosts
2. Use `list_devices` to get all devices
3. Use `get_hosts_by_site` and `get_devices_by_site` to organize by location
4. Generate comprehensive inventory report

### Site-Specific Analysis
1. Use `get_hosts_by_site` to view hosts in a location
2. Use `get_devices_by_site` to view devices in a location
3. Analyze resource distribution
4. Check device and host status

### Device Configuration Review
1. Use `get_device_details` to retrieve device configuration
2. Verify device settings and parameters
3. Identify configuration inconsistencies
4. Recommend standardization

### Troubleshooting Infrastructure
1. Use `list_devices` to find target device
2. Use `get_device_details` to check configuration
3. Use `list_hosts` to verify host connectivity
4. Use `get_host_details` for detailed diagnostics

## Example Questions

- "List all hosts in the New York site"
- "Show me all network devices and their status"
- "What devices are assigned to the San Francisco site?"
- "Get detailed information about a specific device"
- "How many hosts and devices do I have per site?"
- "Show me the complete infrastructure inventory"
- "Are all devices properly configured and online?"

## Response Format

When using this skill, I provide:
- Complete host and device listings
- Filtered results by site or device type
- Configuration details and status
- Site-specific resource distribution
- Infrastructure organization and hierarchy

## Best Practices

- Maintain consistent device naming
- Document device purposes and locations
- Track device assignments per site
- Monitor host connectivity
- Review device configurations regularly
- Keep inventory updated
- Plan for infrastructure growth
- Use site organization for better management

