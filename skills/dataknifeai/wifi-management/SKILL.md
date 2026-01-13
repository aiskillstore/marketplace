---
name: wifi-management
description: Monitor, analyze, and optimize WiFi networks and client connections. Track signal strength, analyze channel usage, and optimize band distribution.
---

# WiFi Management Skill

Monitor and optimize WiFi networks, client connections, and band distribution for peak performance.

## What this skill does

This skill enables you to:
- Monitor all WiFi networks in your UniFi deployment
- Track connected client devices and their signal strength
- Analyze channel usage and interference patterns
- Optimize band distribution (2.4GHz vs 5GHz)
- Identify problematic WiFi connections
- Recommend WiFi performance improvements

## When to use this skill

Use this skill when you need to:
- Check WiFi network status and configuration
- Monitor connected client devices
- Analyze WiFi performance issues
- Optimize channel selection
- Review network security settings
- Plan WiFi infrastructure improvements
- Troubleshoot poor WiFi coverage or speed

## Available Tools

- `get_wifi_networks` - List and get details of all WiFi networks
- `get_wifi_broadcasts` - Get WiFi broadcast information and SSID details
- `get_network_clients` - List all connected WiFi clients
- `get_client_stats` - Get detailed statistics for WiFi clients
- `get_network_device_stats` - Get access point performance metrics

## Typical Workflows

### WiFi Network Overview
1. Use `get_wifi_networks` to list all networks
2. Use `get_wifi_broadcasts` to check SSID broadcasts
3. Use `get_network_clients` to see connected devices
4. Use `get_client_stats` to analyze client distribution

### WiFi Performance Optimization
1. Use `get_network_clients` to analyze client distribution
2. Use `get_client_stats` to check band distribution (2.4GHz vs 5GHz)
3. Use `get_network_device_stats` to check AP performance
4. Recommend channel and band adjustments

### Troubleshooting WiFi Issues
1. Use `get_wifi_networks` to verify network configuration
2. Use `get_network_clients` to check connection status
3. Use `get_client_stats` to analyze signal strength
4. Use `get_network_device_stats` to check AP load

## Example Questions

- "Show all WiFi networks and their status"
- "Which clients have poor signal strength?"
- "What's the client distribution across bands?"
- "Are there any offline WiFi access points?"
- "Analyze channel usage and suggest optimizations"
- "Compare WiFi performance across all APs"
- "Why are some clients dropping connections?"

## Response Format

When using this skill, I provide:
- WiFi network listings with security details
- Client connection status with signal strengths
- Band distribution analysis (2.4GHz vs 5GHz)
- Channel utilization information
- Performance recommendations
- Specific optimization suggestions

## Best Practices

- Monitor band distribution for balanced load
- Check signal strength to identify dead zones
- Analyze channel congestion for interference
- Review client connection quality metrics
- Track AP performance for capacity planning
- Use band steering recommendations for optimization
- Monitor for unusual client behavior patterns
