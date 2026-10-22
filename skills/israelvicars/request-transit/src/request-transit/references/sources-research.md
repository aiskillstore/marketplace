# Trace sources research: PostHog and Datadog (Oct 2026)

Research only; nothing here is implemented yet. Researched 2026-10-14 from official docs and repos.
Both vendors say their MCP tools change often; re-check before building.

## 1. PostHog: what trace/span data exists

PostHog now has **three different things that can be called "traces"**. Only one is a distributed request trace.

| Product | What it is | Parent/child spans? | Fit for Transit |
| --- | --- | --- | --- |
| **Distributed Tracing (APM)** | Generic OTLP receiver. Apps export OTel spans to `https://us.i.posthog.com/i/v1/traces` with the project token (`phc_...`) [P1][P2] | Yes: standard OTel `trace_id`, `span_id`, `parent_span_id`, service name, timing, attributes [P1] | **Good.** Same model as our OTLP adapter |
| **AI Observability** (formerly LLM analytics) | Events `$ai_trace`, `$ai_span`, `$ai_generation`, `$ai_embedding` grouped by `$ai_trace_id`, nested via `$ai_parent_id` [P3][P4] | Yes, a tree, but of LLM steps (tool calls, retrieval, model calls), usually inside one service. Latency in seconds (`$ai_latency`); no service name; start time is the event timestamp [P4][P5] | **Partial.** Could draw an agent's steps as a map, but it's not a cross-service request |
| **Product analytics / session events** | `events` table, `$session_id`, session replay | No span tree | **Not a trace.** Could at most be a user-journey timeline; out of scope |

The OTel-to-AI path is a separate endpoint (`/i/v0/ai/otel`) that only accepts generative-AI spans [P1].

### Retrieving a distributed trace

- **REST, one trace:** `POST /api/projects/:project_id/tracing/spans/trace/:trace_id/` with a **personal API key** (`phx_...`, Bearer). Returns every span plus `self_time_nano`, paginated (`hasMore`, `nextOffset`) [P6].
- **REST, search:** `POST /api/projects/:project_id/tracing/spans/query/`, body `{"query": {"traceId": "<32-hex>", "rootSpans": false, "flatSpans": true, "limit": 100}}`. `limit` 1-1000, keyset cursor `after`, `excludeAttributes` to shrink payloads, duration filters in **nanoseconds**, `statusCodes: [2]` for errors [P6][P7].
- **SQL (HogQL):** table `posthog.trace_spans`. `trace_id` is stored **base64-encoded**; convert with `lower(hex(tryBase64Decode(trace_id)))`, or filter with `trace_id IN (base64Encode(unhex('<hex>')))`. It sits on a different ClickHouse cluster from `events`, so spans and AI events can't be joined in one query [P8].

**Span fields** (REST and MCP) [P6][P9]: `uuid`, `trace_id` (32 hex), `span_id` (16 hex), `parent_span_id` (hex, **all zeros for roots**), `name`, `kind` (int 0-5, OTel enum), `service_name`, `status_code` (0 unset, 1 ok, 2 error; 2 is the only error signal), `timestamp` (ISO start), `end_time` (ISO), `duration_nano`, `is_root_span`, `trace_start`, `trace_duration`, `attributes{}`, `resource_attributes{}`, `self_time_nano` (trace-get only).

## 2. PostHog MCP server

- **Official**, hosted by PostHog: `https://mcp.posthog.com/mcp`. Free to connect; routes to US/EU from your login [P10][P11].
- **Auth:** OAuth in the browser on first use (personal API key is the alternative; see FAQ) [P10][P12]. `?readonly=true` removes write tools; `?features=...` / `?tools=...` filter the tool list [P11][P12].
- **Install:**
  - Any client: `npx @posthog/wizard mcp add` [P10]
  - Claude Code: `claude mcp add --transport http posthog https://mcp.posthog.com/mcp -s user`, then `/mcp` to log in; or `claude plugin install posthog` [P12]
  - Cursor: Marketplace plugin, or `mcp.json` `{"mcpServers":{"posthog":{"url":"https://mcp.posthog.com/mcp"}}}` [P10]
  - Codex: listed as supported [P11]; use Codex's remote MCP config with the same URL (not checked against Codex docs)
- **Tool mode:** most clients get one `exec` tool and call others by name: `exec({"command":"call --json apm-trace-get {...}"})` [P9].

**Tools useful for a request timeline** [P9]:

| Tool | Returns |
| --- | --- |
| `apm-trace-get` | every span of one trace, with `self_time_nano`: **the one Transit needs** |
| `query-apm-spans` | span search (service, status, duration, attributes) to find a trace id |
| `apm-services-list`, `apm-spans-tree`, `apm-spans-aggregate`, `apm-spans-duration-histogram` | discovery and stats (later story 2b) |
| `query-llm-trace`, `query-llm-traces-list` | AI Observability trace trees |
| `execute-sql` | HogQL fallback against `posthog.trace_spans` |
| `query-logs` | logs that share the OTel pipeline (not needed for v1) |

PostHog also ships an agent skill for these tools with a field reference [P13].

## 3. Datadog MCP server

- **Official**, remote, hosted by Datadog, one endpoint per site (for example `mcp.datadoghq.com`, `mcp.datadoghq.eu`, `mcp.us3.datadoghq.com`). Not supported on the gov sites. Docs say the tools are "under significant development and are subject to change" [D1][D2].
- **Auth:** OAuth (default), or API key + application key via `DD_MCP_DOMAIN`, `DD_API_KEY`, `DD_APPLICATION_KEY` [D3]. Access follows the user's own role permissions; trace tools need **APM Read** [D1].
- **Install:**
  - Claude Code: `/plugin install datadog@claude-plugins-official`, then `/ddsetup`; or `claude mcp add --transport http datadog-mcp <ENDPOINT>` [D2][D3]
  - Cursor: Datadog extension for Cursor, or the endpoint in `mcp.json` [D4]
  - Codex and others: own tabs in the setup docs [D2][D4]
  - Toolsets: `?toolsets=apm` (or `all`); drop tools with `?omit_tools=...` [D1][D2]
- **Tools:**

| Tool | Toolset | Notes |
| --- | --- | --- |
| `get_datadog_trace` | core | full trace by id. "Large traces with thousands of spans may be truncated (and indicated as such) without a way to retrieve all spans" [D1] |
| `search_datadog_spans` | core | span search by service, time, resource, etc.; finds a trace id |
| `aggregate_spans` | core | p50-p99, counts, group by (story 2b) |
| `apm_query_trace` | apm (**Preview, sign-up**) | read-only SQL over one trace's spans |
| `apm_latency_bottleneck_summary` | apm (Preview) | self-time hotspots across traces |
| `execute_code` | code-exec | JS sandbox with `dd.*` helpers; could return spans as structured data |

- **Output shape:** the docs don't publish a schema for what `get_datadog_trace` returns (it's built for the model to read). Treat it as unknown: save it as-is and detect the shape. If it isn't span-like JSON, fall back to the Spans API.
- **API fallback (headless):** `POST https://api.<site>/api/v2/spans/events/search` with `DD_API_KEY` + `DD_APP_KEY` (apm_read). Returns the Spans API v2 shape our adapter already parses; up to 1000 spans per page, 300 requests per hour (from the prototype notes; recheck) [D5].

## 4. Can Transit fetch through the MCP and write a file? Adapter mapping

Pattern for both: **the agent calls the MCP tool, writes the raw JSON response to `trace.json`, then runs `node scripts/fetch.mjs file trace.json` (or build/render directly).** The model sees the whole response, which costs tokens on big traces and may not repeat exactly. Rendering only repeats exactly once the file is saved. For CI, use the REST/API backends instead.

### PostHog `apm-trace-get` / REST trace → normalized (new `posthog-tracing` format)

| Transit | PostHog |
| --- | --- |
| `traceId` | `trace_id` (hex; if from HogQL, base64-decode then hex) |
| `spanId` | `span_id` |
| `parentId` | `parent_span_id`, with **all-zeros or empty → `null`** |
| `service` | `service_name` (else `resource_attributes['service.name']`) |
| `name` | `name` |
| `resource` | `attributes['http.route']` or `url.path` or `rpc.method`; else `name` |
| `start` | `Date.parse(timestamp)` in ms, minus the trace minimum. Watch precision: ISO strings may only carry µs/ms |
| `duration` | `duration_nano / 1e6` (prefer over `end_time - timestamp`) |
| `status` | `status_code` 2 → `error`, 1 → `ok`, 0 → `unset`; message from `attributes['otel.status_description']` or the exception event if present |
| `kind` | int enum: 0 unspecified → `internal`, 1 internal, 2 server, 3 client, 4 producer, 5 consumer |
| `peer` | `peer.service`, `db.system`, `messaging.system` from `attributes`, as in the OTLP adapter |

Detect by `service_name` + `duration_nano` + `parent_span_id`. Response wrappers seen in docs: a `results`/`spans` array, with `hasMore` + `nextOffset` for pagination. The agent must follow pages until `hasMore` is false.

### PostHog AI Observability (`query-llm-trace`) → normalized (optional `posthog-ai` format)

`traceId` ← `$ai_trace_id`; `spanId` ← `$ai_span_id` (generate one from the event uuid if missing); `parentId` ← `$ai_parent_id`, mapped to `null` when it equals the trace id; `service` ← `$ai_provider`/`$ai_model` for generations, `$ai_span_name` or the app name for spans; `name` ← `$ai_span_name`; `start` ← event `timestamp`, which may be the **end** time; `duration` ← `$ai_latency * 1000`; `status` ← `$ai_is_error`; `kind` ← `client` for generations, `internal` for spans. Start/end are approximate, so label renders "AI trace, approximate timing".

### Datadog MCP `get_datadog_trace` → normalized

The output isn't documented. Plan: save it raw, then try the existing detectors (tracer/agent span JSON, Spans API v2). If neither matches, ask the agent to call `search_datadog_spans` filtered by `trace_id:<id>` or use the API backend. Field mapping, once the JSON is span-shaped, is the existing Datadog table in `references/adapters.md`. Flag truncated traces in `meta.warnings` and on the render.

## 5. Recommendation: realistic v1 support matrix

| Source | v1 status | Notes |
| --- | --- | --- |
| OTLP JSON file | **Supported** (done) | default, zero auth, README demo |
| Datadog span JSON / Spans API v2 file | **Supported** (done) | |
| Datadog API keys backend | **Beta** | code exists, never run against a live account; needs one real test |
| Datadog MCP | **Beta, documented workflow** | the agent saves the MCP output to a file; the output shape isn't published, so detect it and fall back. Note truncation of very large traces |
| PostHog Distributed Tracing (MCP `apm-trace-get` or REST) | **v1.x: add a `posthog-tracing` adapter** | cheap: same OTel model, about 40 lines of mapping plus pagination. Needs a synthetic fixture in the documented shape and one live check |
| PostHog AI Observability | **Experimental / later** | different data (LLM steps, approximate timing); render as "agent trace", not a request trace |
| PostHog product/session events | **Not supported** | no span tree; don't claim it |

**What "PostHog support" should honestly mean:** "Transit animates **distributed traces stored in PostHog Distributed Tracing** (OTel spans sent to `/i/v1/traces`), fetched with the PostHog MCP `apm-trace-get` tool or the REST trace endpoint." It does **not** mean PostHog analytics events, session replay, or (in v1) LLM-analytics traces. A user with OTel already pointing at PostHog can also export plain OTLP JSON and use the file path today.

## Sources

PostHog
- [P1] Distributed tracing, start here: https://posthog.com/docs/distributed-tracing/start-here
- [P2] Distributed tracing overview: https://posthog.com/docs/distributed-tracing
- [P3] AI Observability basics: https://posthog.com/docs/ai-observability/basics
- [P4] AI Observability traces: https://posthog.com/docs/ai-observability/traces
- [P5] AI Observability spans: https://posthog.com/docs/ai-observability/spans
- [P6] Tracing API reference (trace endpoint): https://posthog.com/docs/api/tracing-2 and https://posthog.com/docs/api/tracing
- [P7] Tracing query body schema (generated): https://github.com/PostHog/posthog/blob/0622fb80/products/tracing/frontend/generated/api.schemas.ts
- [P8] Link traces to AI Observability (HogQL `posthog.trace_spans`): https://posthog.com/docs/distributed-tracing/link-ai-observability
- [P9] PostHog MCP tools reference: https://posthog.com/docs/model-context-protocol/tools
- [P10] PostHog MCP for Cursor: https://posthog.com/docs/model-context-protocol/cursor
- [P11] PostHog MCP overview: https://posthog.com/mcp
- [P12] PostHog MCP for Claude Code: https://posthog.com/docs/model-context-protocol/claude-code.md
- [P13] PostHog skill, span fields reference: https://github.com/posthog/posthog/blob/HEAD/products/tracing/skills/exploring-apm-traces/references/spans-and-fields.md

Datadog
- [D1] Datadog MCP Server tools: https://docs.datadoghq.com/mcp_server/tools.md
- [D2] Set up the Datadog MCP Server: https://docs.datadoghq.com/mcp_server/setup.md
- [D3] Datadog Claude Code plugin: https://github.com/datadog-labs/claude-code-plugin
- [D4] Datadog MCP Server overview: https://docs.datadoghq.com/mcp_server.md
- [D5] Datadog Spans API: https://docs.datadoghq.com/api/latest/spans/
