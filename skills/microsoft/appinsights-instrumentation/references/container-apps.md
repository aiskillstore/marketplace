## Container Apps Observability

Observability guide for apps running in Azure Container Apps.

## Environment-Level Log Analytics

By default, Container Apps environments use a Log Analytics workspace. Configure it at environment creation (`--logs-workspace-id` expects the workspace **Customer ID** (GUID), not the ARM resource ID):

```bash
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group <rg> --workspace-name <workspace-name> \
  --query customerId -o tsv)

WORKSPACE_KEY=$(az monitor log-analytics workspace get-shared-keys \
  --resource-group <rg> --workspace-name <workspace-name> \
  --query primarySharedKey -o tsv)

az containerapp env create \
  --name <env-name> \
  --resource-group <rg> \
  --logs-workspace-id $WORKSPACE_ID \
  --logs-workspace-key $WORKSPACE_KEY \
  --logs-destination log-analytics
```

> 💡 **Tip:** All apps in the same environment share the workspace. Use `--logs-destination none` only for BYOB (bring-your-own-backend) scenarios.

## System Logs vs Application Logs

| Log Table | Content | Retention |
|-----------|---------|-----------|
| `ContainerAppConsoleLogs_CL` | stdout/stderr from containers | Workspace default |
| `ContainerAppSystemLogs_CL` | Platform events (scaling, restarts, image pulls) | Workspace default |

> ⚠️ **Note:** The `_CL` suffix and `_s` column suffixes apply to the **Log Analytics** destination. Environments using the newer **Azure Monitor** destination use `ContainerAppConsoleLogs` / `ContainerAppSystemLogs` (no `_CL`, no `_s` suffixes). Check your environment's log destination to use the correct table name.

System logs capture events outside your code—replica scheduling, health probe results, and revision activation. Console logs capture everything your app writes to stdout/stderr.

## Built-in Metrics

Container Apps exposes these metrics without any SDK:

| Metric | Description | Dimensions |
|--------|-------------|-----------|
| `Replicas` | Current replica count | `revision` |
| `Requests` | HTTP request count | `statusCode`, `statusCodeCategory`, `revision`, `replica` |
| `UsageNanoCores` | CPU usage per replica | `revision`, `replica` |
| `WorkingSetBytes` | Memory usage per replica | `revision`, `replica` |
| `RestartCount` | Container restart count | `revision`, `replica` |
| `RxBytes` / `TxBytes` | Network I/O | `revision`, `replica` |

> ⚠️ **Warning:** Built-in metrics cover infrastructure only. For request-level tracing, response times, and dependency tracking, add Application Insights SDK.

## Application Insights SDK Setup

Set `APPLICATIONINSIGHTS_CONNECTION_STRING` as an environment variable on the container app, then add the SDK per language:

| Language | Package | Init Pattern |
|----------|---------|-------------|
| Node.js | `@azure/monitor-opentelemetry` | Call `useAzureMonitor()` before app startup |
| Python | `azure-monitor-opentelemetry` | Call `configure_azure_monitor()` at entry |
| .NET | `Azure.Monitor.OpenTelemetry.AspNetCore` | `builder.Services.AddOpenTelemetry().UseAzureMonitor()` |
| Java | Agent JAR (manual) | Set `JAVA_TOOL_OPTIONS=-javaagent:/agent/applicationinsights-agent.jar` |

```bash
# Store as a secret (recommended — keeps value out of az show output and portal config)
az containerapp secret set -n <app-name> -g <rg> \
  --secrets "appinsights-conn=<conn-string>"

az containerapp update \
  --name <app-name> \
  --resource-group <rg> \
  --set-env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=secretref:appinsights-conn"
```

## Distributed Tracing Across Microservices

Container Apps with multiple services need correlation. The OpenTelemetry SDK propagates `traceparent` headers automatically through HTTP calls. Ensure:

1. Every microservice has the SDK initialized with the **same** Application Insights resource
2. HTTP clients use instrumented libraries (e.g., `requests` in Python, `fetch`/`axios` in Node.js)
3. Verify end-to-end traces in the **Application Map** blade

> 💡 **Tip:** Use `operation_Id` in KQL queries to trace a single request across all services.

## Dapr Observability

For apps using Dapr sidecars, Dapr generates tracing spans for service invocation, pub/sub, and state operations when tracing is configured. Note that `samplingRate: "1"` means 100% sampling — consider lowering for production workloads.

Configure Dapr tracing in the Container Apps environment. The YAML below represents the config spec — in ACA, apply it via `az containerapp env dapr-component set` or ARM/Bicep (not as a raw YAML file):

```yaml
# Dapr tracing config spec (apply via CLI or Bicep, not raw kubectl)
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: appconfig
spec:
  tracing:
    samplingRate: "1"
    otel:
      endpointAddress: "<otlp-collector-endpoint>"
      isSecure: true
      protocol: grpc
```

> ⚠️ **Note:** `endpointAddress` should point to an OpenTelemetry Collector (not Application Insights directly). Configure the collector with the Azure Monitor exporter to forward traces to App Insights.

Dapr generates spans for:
- **Service invocation** — caller → Dapr sidecar → target sidecar → target app
- **Pub/sub** — publisher → broker → subscriber
- **Bindings** — input/output binding operations

## ARG Queries — Monitoring Status

Discover Container Apps and their monitoring configuration:

```kql
// Container Apps without App Insights configured (checks all containers)
resources
| where type == "microsoft.app/containerapps"
| mv-expand container = properties.template.containers
| mv-expand envVar = container.env
| where isnotempty(envVar)
| summarize hasAppInsights = countif(envVar.name == "APPLICATIONINSIGHTS_CONNECTION_STRING") by name, resourceGroup
| where hasAppInsights == 0
```

> **Note:** This query only covers apps with existing environment variables. Apps with no env vars are excluded by the `mv-expand` and should be identified separately (e.g., filter for containers where `env` is null or empty).

## KQL Query Library

### Console log errors

```kql
ContainerAppConsoleLogs_CL
| where Log_s contains "error" or Log_s contains "exception"
| project TimeGenerated, ContainerAppName_s, RevisionName_s, Log_s
| order by TimeGenerated desc
| take 50
```

### Replica restart events

```kql
ContainerAppSystemLogs_CL
| where EventSource_s == "ContainerAppController" and Reason_s == "Restarting"
| summarize restarts = count() by ContainerAppName_s, RevisionName_s, bin(TimeGenerated, 1h)
| order by TimeGenerated desc
```

### Scaling events

```kql
ContainerAppSystemLogs_CL
| where Reason_s in ("ScalingUp", "ScalingDown")
| project TimeGenerated, ContainerAppName_s, Reason_s, Log_s
| order by TimeGenerated desc
```

### Console log volume by revision

```kql
ContainerAppConsoleLogs_CL
| where isnotempty(Log_s)
| summarize logCount = count() by RevisionName_s, bin(TimeGenerated, 5m)
| render timechart
```

### Request latency by instance (requires Application Insights SDK)

```kql
requests
| where cloud_RoleName has "<app-name>"
| summarize avgDuration = avg(duration), p95 = percentile(duration, 95) by cloud_RoleInstance, bin(timestamp, 5m)
| render timechart
```

> 💡 **Tip:** Console logs don't contain latency data. For request-level latency and dependency analysis, query the `requests` and `dependencies` tables from Application Insights.
