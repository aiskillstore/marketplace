# Flow Nexus Platform Management - Quick Start

Comprehensive platform management for Flow Nexus covering authentication, services, deployment, operations, and billing.

## Quick Start

```bash
# 1. Register and login
mcp__flow-nexus__user_register
mcp__flow-nexus__user_login

# 2. Create sandbox
mcp__flow-nexus__sandbox_create { "template": "node" }

# 3. Deploy application
mcp__flow-nexus__template_deploy { "template_name": "nextjs-starter" }

# 4. Monitor
mcp__flow-nexus__system_health
mcp__flow-nexus__sandbox_logs

# 5. Manage billing
./platform/scripts/billing-util.sh balance
```

## What This Skill Does

- **Authentication**: User registration, login, session management
- **Services**: Setup sandboxes, storage, databases, real-time
- **Deployment**: Deploy from templates or custom apps
- **Operations**: Monitor health, logs, metrics, scaling
- **Billing**: Manage credits, payments, auto-refill

## When to Use

- Setting up Flow Nexus platform
- Deploying applications to cloud
- Managing platform resources
- Monitoring production systems
- Handling billing and payments

## Agents Involved

- **cicd-engineer**: Infrastructure and deployments
- **backend-dev**: Service integration and APIs
- **system-architect**: Architecture and design

## Success Criteria

- User authenticated
- Services configured
- Application deployed
- Monitoring active
- Billing managed

## Duration

30-60 minutes

## See Also

- Full SOP: [SKILL.md](SKILL.md)
- Detailed Process: [PROCESS.md](PROCESS.md)
- Visual Workflow: [process-diagram.gv](process-diagram.gv)
