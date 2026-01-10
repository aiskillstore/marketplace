---
name: deployment-management
description: Track and manage UniFi deployments across your infrastructure. Monitor deployment status, configuration, and progress for coordinated infrastructure updates.
---

# Deployment Management Skill

Track and manage UniFi deployments across your infrastructure.

## What this skill does

This skill enables you to:
- View all active deployments
- Get detailed deployment information
- Monitor deployment status and progress
- Track deployment configuration
- Analyze deployment metrics
- Plan coordinated deployments
- Monitor deployment health
- Generate deployment reports

## When to use this skill

Use this skill when you need to:
- Check deployment status
- Get deployment configuration details
- Monitor deployment progress
- Plan infrastructure updates
- Track configuration changes
- Analyze deployment impact
- Generate deployment reports
- Troubleshoot deployment issues

## Available Tools

- `list_deployments` - List all deployments across all sites
- `get_deployment_details` - Get detailed information about a specific deployment

## Typical Workflows

### Deployment Monitoring
1. Use `list_deployments` to view all active deployments
2. Use `get_deployment_details` for detailed status of each
3. Monitor deployment progress and status
4. Generate status report

### Deployment Planning
1. Use `list_deployments` to see current deployment load
2. Use `get_deployment_details` to understand current deployments
3. Plan new deployment windows
4. Coordinate with existing deployments

### Deployment Troubleshooting
1. Use `list_deployments` to find problematic deployment
2. Use `get_deployment_details` for detailed diagnostics
3. Analyze deployment configuration
4. Identify and resolve issues

### Change Tracking
1. Use `list_deployments` to view all changes
2. Use `get_deployment_details` to track specific changes
3. Document configuration changes
4. Generate change history report

## Example Questions

- "Show me all active deployments"
- "What's the status of the current deployment?"
- "Get details on a specific deployment"
- "Are there any failed or stalled deployments?"
- "What deployments are currently running?"
- "Show me the deployment history"
- "What changes are being deployed?"

## Response Format

When using this skill, I provide:
- Complete list of all deployments
- Detailed deployment status and progress
- Configuration information for each deployment
- Deployment health assessment
- Summary metrics and statistics

## Best Practices

- Monitor deployment progress regularly
- Document deployment changes
- Plan deployments during maintenance windows
- Coordinate multi-site deployments
- Test deployments in non-production first
- Have rollback plans ready
- Track deployment history
- Review deployment logs for issues

