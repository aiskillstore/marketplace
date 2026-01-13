---
name: device-management
description: Manage device adoption and onboarding, maintain device inventory, and monitor device configurations across your UniFi network infrastructure.
---

# Device Management Skill

Manage device adoption, maintain inventory, and monitor device configurations.

## What this skill does

This skill enables you to:
- Manage device adoption and onboarding process
- Maintain comprehensive device inventory
- Monitor device configurations and status
- Track pending devices awaiting adoption
- Plan device upgrades and replacements
- Monitor UniFi controller status and versions

## When to use this skill

Use this skill when you need to:
- Adopt new devices into the UniFi network
- Create and maintain device inventory
- Check device adoption status
- Monitor controller versions and updates
- Plan hardware refreshes
- Track device models and specifications
- Verify device configuration compliance

## Available Tools

- `get_pending_devices` - List devices pending adoption
- `get_network_devices` - List all adopted devices
- `get_network_device_stats` - Get device specifications and status
- `get_network_info` - Get controller info and system status

## Understanding Site IDs

**Important Note:** Your UniFi site ID may appear as an empty string (`""`) in API responses. This is normal and should be handled as follows:

- When querying via tools, pass an empty string or use "default" for the default site
- The MCP server automatically resolves empty site IDs to your first available site
- In curl commands, you'll see endpoints like `/sites//devices` (double slashes) when the site ID is empty

**Example curl with empty site ID:**
```bash
curl -k -H "X-API-KEY: $UNIFI_API_KEY" \
  "$UNIFI_BASE_URL/proxy/network/integration/v1/sites//devices"
```

## Typical Workflows

### New Device Adoption
1. Use `get_pending_devices` to find devices awaiting adoption
2. Review device details (MAC address, IP, model)
3. Plan adoption by site and function
4. Document adoption process completion

### Device Inventory Management
1. Use `get_network_devices` to get current inventory
2. Use `get_network_device_stats` for specifications
3. Organize devices by type and location
4. Create inventory reports
5. Plan upgrade cycles based on age and performance

### System Monitoring
1. Use `get_network_info` to check controller status
2. Monitor controller version and uptime
3. Track system health metrics
4. Plan maintenance windows
5. Verify backup status

## Example Questions

- "Show all devices pending adoption"
- "List the device inventory"
- "What's the controller version and status?"
- "Get specifications for all network devices"
- "Create a device inventory report by type"
- "Plan a device upgrade strategy"

## Response Format

When using this skill, I provide:
- Device listings with MAC addresses and IP information
- Device specifications (model, firmware version)
- Adoption status and pending device details
- System health and version information
- Inventory organization by type/location
- Upgrade recommendations based on age/performance
- Hardware planning suggestions

## Best Practices

- Adopt devices in logical groups (by site/function)
- Maintain up-to-date device inventory
- Document device purpose and location
