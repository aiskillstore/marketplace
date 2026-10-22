# Adapters and fetch backends

Every input becomes one normalized shape (`adapters/normalize.mjs`):

```
{ traceId, meta: { format, source, synthetic, startUnixNs, warnings[] },
  spans: [{ spanId, parentId, service, name, resource?, start, duration, status, kind,
            statusMessage?, peer?, operation?, attrs? }] }
```

`start`/`duration` are ms (start relative to the earliest span); `status` is `ok|error|unset`;
`kind` is `server|client|producer|consumer|internal`; `peer` names an uninstrumented dependency
(db, cache, broker) that becomes a dotted *infrastructure* line.

| Format | Detected from | Notes |
| --- | --- | --- |
| OTLP JSON | `resourceSpans` | `service.name` resource attr; status code 2 = error |
| Datadog tracer/agent span JSON | `[[span]]`, `[span]`, `{traces}`, `{spans}` with `trace_id` | 64-bit ids and ns timestamps kept exact (numbers quoted before parse); `_dd.p.tid` gives the 128-bit id |
| Datadog Spans API v2 | `{data:[{type:"spans"}]}` | `resource_name`, ISO start/end, `custom.duration` |
| PostHog Distributed Tracing | `results`/`spans`/array of objects with `span_id` + `service_name`/`duration_nano` | REST trace endpoint or MCP `apm-trace-get`; hex or base64 (HogQL) ids; all-zero parent = root; `kind` 0-5 and `status_code` 0-2 are OTel enums; ISO timestamps parsed to ns; `hasMore: true` adds a warning |
| AWS X-Ray | `{Traces:[{Segments:[{Document}]}]}`, `{Segments}`, or segment documents (`trace_id` + `start_time`) | segment = service hop (server; consumer under a queue send); nested subsegments: no namespace = in-process (internal), `remote`/`aws` = downstream client call (producer for SendMessage/Publish/PutRecord/PutEvents), `peer` = subsegment name; `parent_id` links a segment to the calling subsegment; `fault`/`error`/`throttle` = error with `cause.exceptions` message; inferred segments dropped; `1-xxxxxxxx-…` id becomes the 32-hex OTel id. GetTraceSummaries input is rejected with a hint |
| Grafana Tempo | v1 `{batches:[…]}`; v2 `{trace:{resourceSpans or batches}, status}` | OTLP inside, read by the OTLP mapper: base64 (protobuf-JSON) or hex ids, `SPAN_KIND_*` / `STATUS_CODE_*` strings or numbers, `scopeSpans` or legacy `instrumentationLibrarySpans`. v2 `status: PARTIAL` (size limit or `q` filter) adds a warning. Protobuf responses (`Accept: application/protobuf`) and the `application/vnd.grafana.llm` format are not read: fetch JSON |
| internal | already normalized | validated only |

Full Datadog field mapping is in the comments of `<skill>/adapters/normalize.mjs`; tests in `<skill>/scripts/test-normalize.mjs`.

## Backends

| Backend | When | How | Status |
| --- | --- | --- | --- |
| plain file | default, README demo, zero auth | `node <skill>/scripts/fetch.mjs file trace.json` (or pass the file straight to build) | working |
| Datadog MCP | interactive agent use; access follows the user's own permissions | agent calls the MCP server's trace/span tools, saves the JSON to a file, then uses the file backend. Results pass through model context: costs tokens on big traces | documented, milestone 4 |
| Datadog API keys | headless / CI | `DD_API_KEY`, `DD_APP_KEY` (apm_read), `DD_SITE` in env; `node scripts/fetch.mjs datadog-api <id>` | code from prototype, untested |
| PostHog MCP | interactive; OAuth via `https://mcp.posthog.com/mcp` | agent calls `apm-trace-get` (find ids with `query-apm-spans`), follows pages until `hasMore` is false, saves JSON, then the file backend | documented; shape from docs, synthetic sample only |
| PostHog API | headless | `POSTHOG_API_KEY` (personal `phx_` key), `POSTHOG_HOST`, `POSTHOG_PROJECT_ID`; `node scripts/fetch.mjs posthog-api <trace_id>` | written, **untested live** |
| AWS X-Ray CLI | headless; your normal AWS CLI credentials (`AWS_PROFILE`/`AWS_REGION`/SSO) | `node scripts/fetch.mjs xray <trace id>` runs `aws xray batch-get-traces`; `xray --find [--minutes 60] [--filter 'fault = true']` lists ids via `get-trace-summaries`. Default sampling is ~5% | written, **untested live** |
| AWS MCP | interactive | AWS Labs CloudWatch Application Signals MCP server (`uvx awslabs.cloudwatch-appsignals-mcp-server@latest`): `get_xray_trace` (up to 5 ids), `search_transaction_spans`, `query_sampled_traces`. Save the trace JSON (BatchGetTraces shape or segment documents), then the file backend. Output shape not yet checked live | documented only |
| Tempo API | headless; local or Grafana Cloud | `TEMPO_URL`, optional `TEMPO_TOKEN` (bearer) or `TEMPO_USER`+`TEMPO_PASSWORD` (basic; Grafana Cloud instance id + token), `TEMPO_TENANT` (`X-Scope-OrgID`); `node scripts/fetch.mjs tempo <trace_id> [--start s --end s]` uses `/api/v2/traces/<id>` and falls back to `/api/traces/<id>` on older Tempo; `tempo --find '{ status = error }'` lists ids via `/api/search` | tested against a local mock server (v2, v1 fallback, auth headers, not-found). **Not tested against a real Tempo** (Docker image pull hung on the test machine) |
| Grafana / Tempo MCP | interactive | Grafana's `mcp-grafana` (`get_tempo_trace`, `search_tempo_traces`) or the MCP server built into Tempo at `/api/mcp` (`get-trace`, `traceql-search`). Save the trace JSON (ask for OTLP JSON, not the LLM format), then the file backend. Output shape not yet checked live | documented only |
| Jaeger | later | see `references/more-sources.md` | not started |

## Privacy

Traces are processed locally; `transit.html` has no network calls (fonts and data are inlined).
`<skill>/../../core/build.mjs` drops attribute keys matching a default PII pattern before rendering
(`DEFAULT_REDACT`), plus any keys passed with `--redact`. Disable the default with `--no-default-redact`.
