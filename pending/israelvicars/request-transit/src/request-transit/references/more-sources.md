# More trace sources: candidates for Transit adapters (Oct 2026)

Research only. "Mapping" means getting to Transit's normalized span shape
`{traceId, spanId, parentId, service, name, resource, start, duration, status, kind}`.
"MCP output" matters because the MCP path saves the tool's response to a file. A tool that returns
formatted text (a waterfall drawn for the model) is much harder to parse than one that returns JSON.

## Summary table

| Source | Trace-by-id API | MCP for traces | MCP output | Mapping | Splash / audience |
| --- | --- | --- | --- | --- | --- |
| **Jaeger** (v2) | `GET /api/v3/traces/{id}` returns **OTLP JSON** [J1] | community `jaeger-mcp-server` (npm), get-trace returns OTLP resource spans [J2][J3]; a Jaeger ADR proposes a built-in one [J4] | JSON (OTLP) | **trivial**: existing OTLP adapter, plus unwrapping the `result` envelope | high in OSS; free local demo (Jaeger all-in-one + OTel demo) |
| **Grafana Tempo** | `GET /api/traces/{id}`, `/api/v2/traces/{id}`, OTLP-shaped; `Accept: application/vnd.grafana.llm` gives a slimmer LLM format [T1][T3] | **official, two:** built into Tempo at `/api/mcp` (`get-trace`, `traceql-search`, `traces-diff`) [T2]; Grafana's `mcp-grafana` (`get_tempo_trace`, `search_tempo_traces`) [T4] | JSON via API; MCP likely OTLP/LLM JSON (verify) | **easy** (OTLP); the LLM format needs a small adapter | high: Grafana Cloud free tier, big LGTM community |
| **AWS X-Ray / CloudWatch Application Signals** | `BatchGetTraces` returns segment documents (JSON strings), nested subsegments, float-second times [A3]; Transaction Search exposes OTel spans in CloudWatch Logs [A1] | **official** AWS Labs `cloudwatch-applicationsignals-mcp-server`: `get_xray_trace` (up to 5 ids), `search_transaction_spans`, `query_sampled_traces` [A1][A2] | JSON-ish summaries (verify) | **medium-hard**: segments vs subsegments, `namespace: aws/remote` become infra hops, fault/error/throttle flags; X-Ray is 5% sampled by default [A1] | very high (AWS shops, serverless) |
| **Honeycomb** | no simple public get-trace-by-id endpoint; Query API with `trace.trace_id` filter returns raw event rows [H4] | **official hosted** MCP, OAuth: `get_trace` (view modes auto/compact/full/focused), `list_spans`, `get_span_details` [H1][H2][H3] | **rendered waterfall** text, collapsed by default; `view_mode: full` needed | **medium**: Honeycomb fields (`trace.span_id`, `trace.parent_id`, `service.name`, `duration_ms`); MCP text needs parsing | high among observability practitioners; good share on X |
| **Sentry** | trace endpoint used by the Sentry UI (`/organizations/{org}/trace/{id}/`, not stable public API) [S3]; span search through Discover/`search_events` | **official** `sentry-mcp`: `get_trace_details` returns a **condensed overview and selected spans**, and says to use `search_events` (dataset spans) for full enumeration [S1][S2] | markdown summary; full spans via search_events | **medium**: transactions + spans, `op`/`description`, `project` as service; MCP output deliberately incomplete | very high (frontend + backend devs; many have traces and don't know it) |
| **New Relic** | NerdGraph `actor.distributedTracing.trace(traceId)` with spans [N3] | **official** MCP `mcp.newrelic.com/mcp`: `search_traces`, `get_trace`, `get_distributed_trace_details` [N1][N2] | JSON-ish (verify) | **medium**: span attributes `entity.name`, `parent.id`, `duration.ms`, `span.kind` | medium-high enterprise |
| **Azure App Insights** | KQL over `requests`, `dependencies`, `exceptions` joined on `operation_Id`; `id` = span, `operation_ParentId` = parent [Z2] | **official** Azure MCP Server, Monitor tools run KQL against Log Analytics / App Insights [Z1] | tabular JSON from KQL | **medium**: two tables to merge, `success`, `duration` in ms, `cloud_RoleName` as service | high in .NET/Azure orgs, low on X |
| **Google Cloud Trace** | v1 `projects.traces.get` spans (`spanId`, `parentSpanId`, `startTime`, `endTime`, `labels`) [G2]; v2 is write-side | **official** remote MCP `https://cloudtrace.googleapis.com/mcp`: `get_trace`, `list_traces` [G1] | JSON, documented schema (Trace with spans[]) | **easy**: service from `/component` or `g.co/agent`-style labels; kind field present | medium (GCP/GKE) |
| **Zipkin** | `GET /api/v2/trace/{traceId}`, a flat span list: `timestamp`/`duration` in µs, `localEndpoint.serviceName`, `kind`, `parentId` [Z3] | community only | n/a | **trivial** | low splash now, but many systems still export Zipkin v2 JSON (Spring, Envoy, Istio) |

## Ranked recommendation

1. **Jaeger + Tempo ("any OTLP backend")**: one small adapter on top of OTLP plus two fetch scripts, both run locally free with Docker. Best "it just works" demo story: "point it at your Jaeger/Tempo." Tempo also has an official MCP built into the server, so the agent path is strong. Lowest risk, widest OSS reach.
2. **AWS X-Ray / Application Signals**: biggest audience and an official AWS MCP. Real mapping work (segments and subsegments), and sampling caveats belong in the render ("5% sampled"). High splash: "your Lambda request as a subway map."
3. **Sentry**: huge developer base, official MCP, and many teams already have tracing turned on through the SDK. The MCP trace tool is a summary, so the adapter has to go through span search. Medium effort, high reach.
4. **Honeycomb**: the observability crowd is the audience most likely to share Transit renders. Needs a Query API path or parsing of `get_trace` full mode.
5. **Google Cloud Trace**: an easy, cleanly documented JSON shape and an official MCP. Cheap to add once 1-4 exist.

Also worth adding because it's nearly free: a **Zipkin v2** adapter (about 30 lines), which covers Spring/Envoy/Istio exports. New Relic and Azure App Insights are worth doing on demand. Each is medium effort and their audiences are less likely to share on social.

Before building any of these: check the real MCP output shape on a live or sandbox account. Several MCP tools return text formatted for the model, not stable JSON. Prefer the REST/API fetch for anything you need to repeat exactly.

## Sources

- [J1] Jaeger APIs (v2, api/v3 OTLP): https://www.jaegertracing.io/docs/2.dev/architecture/apis/
- [J2] jaeger-mcp-server (npm): https://www.npmjs.com/package/jaeger-mcp-server
- [J3] digma-ai/jaeger-mcp: https://github.com/digma-ai/jaeger-mcp
- [J4] Jaeger ADR 002, MCP server: https://github.com/jaegertracing/jaeger/blob/main/docs/adr/002-mcp-server.md
- [T1] Tempo HTTP API: https://grafana.com/docs/tempo/latest/api_docs/
- [T2] Tempo MCP server: https://grafana.com/docs/tempo/latest/api_docs/mcp-server/
- [T3] Tempo and AI (LLM response format): https://grafana.com/docs/tempo/latest/introduction/tempo-and-ai/
- [T4] grafana/mcp-grafana README: https://github.com/grafana/mcp-grafana/blob/main/README.md
- [A1] CloudWatch Application Signals MCP server: https://awslabs.github.io/mcp/servers/cloudwatch-applicationsignals-mcp-server
- [A2] awslabs/mcp source: https://github.com/awslabs/mcp/blob/main/src/cloudwatch-applicationsignals-mcp-server/README.md
- [A3] X-Ray BatchGetTraces: https://docs.aws.amazon.com/xray/latest/api/API_BatchGetTraces.html
- [H1] Honeycomb MCP tools: https://docs.honeycomb.io/integrations/mcp/tools
- [H2] Honeycomb MCP overview: https://docs.honeycomb.io/integrations/mcp
- [H3] Honeycomb agent skill, trace exploration: https://github.com/honeycombio/agent-skill/blob/main/honeycomb/skills/production-investigation/references/trace-exploration.md
- [H4] Honeycomb Query API: https://docs.honeycomb.io/api/
- [S1] sentry-mcp get_trace_details: https://github.com/getsentry/sentry-mcp/blob/main/packages/mcp-core/src/tools/catalog/get-trace-details.ts
- [S2] sentry-mcp trace tool PR: https://github.com/getsentry/sentry-mcp/pull/456
- [S3] Sentry API docs: https://docs.sentry.io/api/
- [N1] New Relic MCP tool reference: https://docs.newrelic.com/docs/agentic-ai/mcp/tool-reference/
- [N2] New Relic MCP setup: https://docs.newrelic.com/docs/agentic-ai/mcp/setup/
- [N3] New Relic NerdGraph: https://docs.newrelic.com/docs/apis/nerdgraph/get-started/introduction-new-relic-nerdgraph/
- [Z1] Azure MCP Server, Azure Monitor tools: https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/tools/azure-monitor
- [Z2] Application Insights data model: https://learn.microsoft.com/en-us/azure/azure-monitor/app/data-model-complete
- [G1] Cloud Trace MCP get_trace: https://docs.cloud.google.com/trace/docs/reference/mcp/mcp/tools_list/get_trace
- [G2] Cloud Trace API v1: https://cloud.google.com/trace/docs/reference/v1/rest/v1/projects.traces/get
- [Z3] Zipkin API v2: https://zipkin.io/zipkin-api/
