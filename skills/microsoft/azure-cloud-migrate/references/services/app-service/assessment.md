# Assessment Phase

Generate a migration assessment report before any code changes.

## Prerequisites

- Workspace contains source platform project files (Procfile, app.yaml, .ebextensions, etc.)
- Prompt user to upload relevant files if not present

## Assessment Steps

1. **Identify Application** — Determine app type (web, API, worker), runtime, and framework
2. **Map Platform Services** — Map source services to Azure equivalents (see scenario-specific references)
3. **Map Properties** — Map compute config (instance size, scaling) to App Service Plan properties
4. **Check Dependencies** — List 3rd-party libraries and verify Azure compatibility
5. **Analyze Code** — Check for platform-specific APIs, SDKs, or patterns that need migration
6. **Map Data Services** — Identify database and storage migration paths
7. **Map Deployment** — Identify equivalent Azure deployment strategies (azd, GitHub Actions, Bicep)
8. **Review CI/CD** — Check pipeline compatibility with Azure DevOps or GitHub Actions
9. **Map Monitoring** — Map observability stack → Application Insights / Azure Monitor

## Code Preview

During assessment, show a **sneak peek** of key configuration changes:
- Startup command / Dockerfile adjustments
- App Settings mapping
- Database connection string migration (to managed identity)

This helps the user understand the migration scope before committing.

## Architecture Diagrams

Generate two diagrams:
1. **Current State** — Source platform architecture with services and integrations
2. **Target State** — Azure architecture showing equivalent App Service structure

## Assessment Report Format

> ⚠️ **MANDATORY**: Use these exact section headings in every assessment report. Do NOT rename, reorder, or omit sections.

The report MUST be saved as `migration-assessment-report.md` inside the output directory (`<source-folder>-azure/`).

```markdown
# Migration Assessment Report

## 1. Executive Summary

| Property | Value |
|----------|-------|
| **Application Name** | <name> |
| **Application Type** | Web App / API / Worker |
| **Source Platform** | <Heroku / Elastic Beanstalk / App Engine> |
| **Source Runtime** | <runtime and version> |
| **Target Platform** | Azure App Service |
| **Target Runtime** | <runtime and version> |
| **Migration Readiness** | <High / Medium / Low> |
| **Estimated Effort** | <Low / Medium / High> |
| **Assessment Date** | <date> |

## 2. Application Inventory

| # | Component | Runtime | Type | Instances | Description |
|---|-----------|---------|------|-----------|-------------|
| 1 | | | Web / Worker / Cron | | |

## 3. Service Mapping

| Source Service | Azure Equivalent | Migration Complexity | Notes |
|----------------|------------------|----------------------|-------|
| | | | |

## 4. Compute & Scaling Mapping

| # | Source Config | Value | Azure Equivalent | Azure Value | Notes |
|---|-------------|-------|------------------|-------------|-------|
| 1 | Instance type | | App Service Plan SKU | | |
| 2 | Auto-scaling | | App Service Autoscale | | |
| 3 | Health check | | Health Check feature | | |

## 5. Dependencies Analysis

| # | Package/Library | Version | Platform-Specific? | Azure Equivalent | Compatible? | Notes |
|---|----------------|---------|---------------------|------------------|-------------|-------|
| 1 | | | | | | |

## 6. Environment Variables & Configuration

| # | Source Variable | Purpose | Azure Equivalent | Auth Method | Notes |
|---|---------------|---------|------------------|-------------|-------|
| 1 | | | App Setting / Key Vault | Managed Identity / App Setting | |

## 7. Architecture Diagrams

### 7a. Current State (Source Platform)

<!-- Mermaid or ASCII diagram -->

### 7b. Target State (Azure)

<!-- Mermaid or ASCII diagram -->

## 8. Data Services Mapping

| Source Database/Storage | Azure Equivalent | Migration Path | Notes |
|------------------------|------------------|----------------|-------|
| | | | |

## 9. Networking & Security Mapping

| Source Feature | Azure Equivalent | Notes |
|---------------|------------------|-------|
| Custom domain | App Service Custom Domain | |
| SSL/TLS | App Service Managed Certificate / BYO cert | |
| VPN/VPC | VNet Integration | |

## 10. Monitoring & Observability Mapping

| Source Service | Azure Equivalent | Migration Notes |
|---------------|------------------|-----------------|
| | Application Insights | |
| | Azure Monitor Metrics | |
| | Azure Monitor Alerts | |

## 11. CI/CD & Deployment Mapping

| Source Tool | Azure Equivalent | Notes |
|------------|------------------|-------|
| | GitHub Actions / Azure DevOps | |
| | Bicep / ARM Templates | |
| | Deployment Slots | |

## 12. Recommendations

1. **Runtime**: <recommended App Service runtime stack and version>
2. **App Service Plan**: <Free / Basic / Standard / Premium v3>
3. **IaC Strategy**: <Bicep with azd / Terraform>
4. **Auth Strategy**: <Managed Identity for all service-to-service>
5. **Monitoring**: <Application Insights + Azure Monitor>

## 13. Next Steps

- [ ] Review and approve this assessment report
- [ ] Proceed to code migration (azure-cloud-migrate Phase 2)
- [ ] Hand off to azure-prepare for IaC generation
```

> 💡 **Tip:** Use `mcp_azure_mcp_get_azure_bestpractices` tool to learn App Service best practices for the comparison.
