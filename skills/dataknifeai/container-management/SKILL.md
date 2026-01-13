---
name: container-management
description: Create, manage, and optimize LXC containers in Proxmox. Control container lifecycle, manage resources, and coordinate container deployments across nodes.
---

# Container Management Skill

Create, manage, and optimize LXC containers in your Proxmox environment.

## What this skill does

This skill enables you to:
- List containers on specific nodes
- Get detailed container configuration and status
- Start, stop, reboot, and delete containers
- Create new LXC containers with basic or advanced configuration
- Clone existing containers
- Modify container resource allocation
- Monitor container performance metrics
- Manage container templates
- Plan container deployment strategies
- Optimize resource allocation for containers

## When to use this skill

Use this skill when you need to:
- Check container status and configuration
- Manage container lifecycle (start/stop/reboot)
- Monitor container performance and resource usage
- Adjust container resources (CPU, memory, storage)
- Create new containers
- Troubleshoot container issues
- Plan container migrations
- Optimize container placement
- Manage container templates

## Available Tools

- `get_containers` - List all containers on a specific node
- `get_container_status` - Get detailed container status and configuration
- `get_container_config` - Get full container configuration details
- `start_container` - Start a container
- `stop_container` - Stop a container immediately
- `shutdown_container` - Gracefully shutdown a container
- `reboot_container` - Reboot a container
- `create_container` - Create a new LXC container with basic configuration
- `create_container_advanced` - Create a container with advanced configuration options
- `clone_container` - Clone an existing container
- `delete_container` - Delete a container

## Typical Workflows

### Container Lifecycle Management
1. Use `get_containers` to list available containers
2. Use `get_container_status` or `get_container_config` to check state
3. Use start/stop/reboot to manage container operations
4. Monitor container health during changes

### Container Creation & Deployment
1. Use `create_container` or `create_container_advanced` to provision new container
2. Use `get_container_status` to verify configuration
3. Use `clone_container` to create copies for testing or deployment
4. Use `get_container_config` to review detailed settings
5. Document container details for reference

### Container Lifecycle Operations
1. Use `shutdown_container` for graceful shutdown
2. Use `reboot_container` to restart container
3. Use `stop_container` for immediate termination if needed
4. Monitor container status during transitions

### Container Troubleshooting
1. Use `get_container_status` to diagnose issues
2. Use reboot/restart to recover from problems
3. Use snapshots to rollback problematic changes
4. Analyze logs and metrics for root cause

## Example Questions

- "List all containers on the worker node"
- "What's the status and resource usage of container 101?"
- "Get the full configuration of container 105"
- "Start the database container"
- "Create a new container with 2 cores and 4GB RAM"
- "Clone container 102 to create a test environment"
- "Gracefully shutdown container 103"
- "Delete container 199 and remove all data"
- "Show me all containers and their resource allocation"

## Response Format

When using this skill, I provide:
- Container listings with status and resources
- Detailed container configuration and metrics
- Status confirmations for container operations
- Resource utilization analysis
- Optimization recommendations

## Best Practices

- Monitor container performance regularly
- Use cloning for quick container deployment
- Create containers with appropriate resource allocation
- Use graceful shutdown to minimize disruption
- Plan resource allocation carefully
- Balance containers across nodes
- Implement monitoring for critical containers
- Use container templates for consistency
- Document container configuration and purpose
- Test changes in development first
- Monitor disk usage and resource limits
- Clean up unused containers regularly
- Use meaningful hostnames for easy identification

