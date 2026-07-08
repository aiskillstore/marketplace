# Azure Messaging Troubleshooting

Diagnose and resolve issues with Azure Event Hubs and Service Bus SDKs.

## Routing

| Symptom | Guide |
|---------|-------|
| Connection failures, firewall, IP/VNet, WebSocket | [service-troubleshooting.md](service-troubleshooting.md) |
| SDK-specific errors (see language below) | Language guide |

## SDK Troubleshooting by Language

- **Event Hubs**: [Python](azure-eventhubs-py.md) | [Java](azure-eventhubs-java.md) | [JS](azure-eventhubs-js.md) | [.NET](azure-eventhubs-dotnet.md)
- **Service Bus**: [Python](azure-servicebus-py.md) | [Java](azure-servicebus-java.md) | [JS](azure-servicebus-js.md) | [.NET](azure-servicebus-dotnet.md)

## Common Issues

| Issue | Category |
|-------|----------|
| AMQP link detach, idle timeout, connection inactive | [service-troubleshooting.md](service-troubleshooting.md) |
| Message lock lost/expired, lock renewal failures | Language-specific SDK guide |
| Session lock errors, session receiver detach | Language-specific SDK guide |
| Duplicate events, checkpoint/offset reset | Language-specific SDK guide |
| Batch >1 MB rejected, partition key conflicts | [service-troubleshooting.md](service-troubleshooting.md) |

## MCP Tools

| Tool | Use |
|------|-----|
| `mcp_azure_mcp_eventhubs` | List namespaces, hubs, consumer groups |
| `mcp_azure_mcp_servicebus` | List namespaces, queues, topics, subscriptions |
| `mcp_azure_mcp_monitor` | Query diagnostic logs with KQL |
| `mcp_azure_mcp_resourcehealth` | Check service health status |
| `mcp_azure_mcp_documentation` | Search Microsoft Learn for troubleshooting docs |
