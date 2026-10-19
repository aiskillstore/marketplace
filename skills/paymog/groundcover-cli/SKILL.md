---
name: groundcover-cli
description: Invoke the `groundcover` Go CLI to manage Groundcover resources (dashboards, monitors, silences, connected apps, notification routes, API keys, policies, integrations, pipelines, workflows) AND to answer production observability questions by querying logs, traces, metrics, k8s inventory, and k8s events. Use whenever a task needs an authenticated call against the Groundcover API or whenever the user is debugging a prod issue and asks things like "why is X erroring in prod", "show me logs for service Y", "what's the p99 latency on Z", "what pods are crashlooping", "search traces for slow requests", "any k8s events for namespace N", "is service S receiving traffic", "list groundcover monitors", "create a silence", "update notification route", "hit a groundcover endpoint". Covers required env vars, the SDK-backed vs raw command split, and concrete request-body templates for logs/traces/metrics/k8s so the CLI can be driven from anywhere.
---

# Groundcover CLI

Invoke the `groundcover` binary (install via `brew install paymog/tap/groundcover`). Source of truth is [`paymog/groundcover-cli`](https://github.com/paymog/groundcover-cli).

## Auth (required before any command)

```sh
export GROUNDCOVER_API_KEY=gcsa_...   # must be a service-account key
```

**The key must be a service-account key: prefix `gcsa_`, exactly 40 chars.** Anything else is rejected with a clear message — `Invalid token prefix. Expected 'gcsa_'` or `Invalid token length (N, expected 40)`. Don't confuse key types:
- `gcsa_…` — **service-account** key. This is the one query/CRUD commands need.
- `gcik_…` — **ingestion** key (data push). Will NOT authenticate the API; wrong type.

A 401 with a correctly-formatted `gcsa_` key means the key belongs to a **different tenant** than the one you're querying.

If you don't have a `gcsa_` key handy, mint one with `groundcover service-accounts create` using an already-valid key, then `export GROUNDCOVER_API_KEY=gcsa_…` for the session.

Defaults baked in:
- `--base-url https://api.groundcover.com`
- `--backend-id groundcover`

No tenant UUID default — set `--tenant-uuid` / `GROUNDCOVER_TENANT_UUID` to send an `X-Tenant-UUID` header on non-grafana `raw …` passthrough calls (e.g. cross-tenant access). The embedded Grafana `raw grafana …` endpoints ignore it (see the Grafana section below).

The `raw grafana …` commands do NOT use the `gcsa_` key at all — they need a Grafana service account token (`glsa_…`). Set `GROUNDCOVER_GRAFANA_SERVICE_ACCOUNT_TOKEN` / `--grafana-token`.

Override env: `GROUNDCOVER_BACKEND_ID`, `GROUNDCOVER_TENANT_UUID`, `GROUNDCOVER_GRAFANA_SERVICE_ACCOUNT_TOKEN`, `GROUNDCOVER_BASE_URL` (or `GC_*` equivalents). Same names work as `--api-key`, `--backend-id`, `--tenant-uuid`, `--grafana-token`, `--base-url` flags.

### Stored profiles (alternative to env vars)

Instead of exporting `GROUNDCOVER_API_KEY` every session, credentials can be saved in named profiles. The API key goes in the OS keyring; metadata (backend ID, base URL, tenant UUID) lives in `~/.config/groundcover/profiles.yaml`.

```sh
groundcover auth login [name] --backend-id <id>   # prompts for key (or --key); validates before saving
groundcover auth list                              # * marks default
groundcover auth default <name>                    # change default
groundcover --profile <name> <command>             # use a profile for one command
groundcover auth status                            # show resolved source
groundcover auth token                             # print resolved key
groundcover auth logout <name> [-f]
```

Precedence: `--api-key`/`GROUNDCOVER_API_KEY` env → `--profile <name>` → default profile. An explicit key plus `--profile` is rejected as ambiguous. `GROUNDCOVER_PROFILE` sets the profile via env.

Other global flags: `--timeout` (default 30s), `--raw` (don't reformat JSON response).

## Two surfaces

| Surface | When to use |
|---------|-------------|
| **SDK-backed** (`groundcover <resource> <verb>`) | First choice. Stable contracts, typed request bodies. |
| **Raw HAR-derived** (`groundcover raw …`) | Endpoint missing from SDK, or you need a runner feature SDK lacks (see below). |

Always try the SDK form first.

### What raw gives you that SDK does not

- `--set dotted.path=value` — deep-merge overrides on top of the body
- `--query key=value` (repeatable) — arbitrary querystring overrides
- Built-in default body captured from the webapp HAR (SDK requires explicit `--body-file`/`--body-json`)
- Sends `X-Tenant-UUID` on non-grafana raw calls when you set `--tenant-uuid` / `GROUNDCOVER_TENANT_UUID` (for cross-tenant access; the SDK transport otherwise derives tenant from the API key). Grafana `raw grafana …` commands don't use it — they authenticate with the `glsa_` token instead.
- `groundcover raw list` to discover every captured endpoint

Both surfaces support `--body-file` (json/yaml), `--body-json`, and `--raw` output.

### Endpoints that are raw-only (no SDK command yet)

Reach for `groundcover raw …` for any of these; the SDK has the *parent* resource but not the drilldown:

- **logs:** `filters`, `velocity` (SDK only has `search`)
- **traces:** `attributes`, `details`, `errors`, `filters`, `insights`, `latencies`, `requests`, `values-distribution` (SDK only has `search`)
- **metrics:** `cardinality`, `cardinality-graph`, `discovery`, `labels-cardinality`, `query-range`, `resources errors|latencies|list|requests` (SDK has `query`, `names`, `keys`, `values`)
- **prometheus:** `prometheus api query` (raw Prom passthrough — handy for ad-hoc PromQL via `--query query='up'`)
- **Grafana dashboards:** `grafana search`, `grafana dashboards get|save|delete`, `grafana dashboards permissions get|update`, `grafana dashboards versions|get|restore`, `grafana folders list|get|create|update|delete`, `grafana folders permissions get|update`, `grafana annotations list|create|update|delete`, `grafana prometheus rules`, `grafana datasources label-values`, `grafana ds query`
- **monitors drilldowns:** `instances filters|query|timeline`, `labels keys`, `silences`, `summary filters|query`, `timeline` (SDK only has CRUD)
- **k8s drilldowns:** `configmaps|cronjob|daemonsets|deployments|jobs|pods|pvcs|replicasets|statefulsets list`, `container info`, `context events`, `namespaces info|list`, `nodes info-with-resources|list|resources|usage top10`, `pod container usage`, `pods status-over-time`, `workloads availability|events|usage top10`, `network connections|cross-az|cross-az-regions|partners|throughput|top-connections`, `events search-time-series` (SDK only has `clusters`, `workloads`, `events-search`, `events-over-time`)
- **infra:** `infra hosts info-with-resources`
- **resources / RUM:** `resources apis errors|filters|latencies|list|requests`, `rum sessions filters|query`, `sources list`
- **pipelines stats:** `pipelines logs current-stats`, `pipelines traces current-stats` (SDK only does config CRUD)
- **tenant / billing / RBAC reads:** `rbac seatsUsage`, `rbac tenant ai-settings`, `rbac tenant settings`, `backend settings`, `billing method`, `agent token-budgets|token-usage|token-usage history|token-usage tenant`
- **storage management:** `storage-management get|update --data-type <logs|traces|events|measurements|monitor_instance>` for retention, gcQL exception rules, and index-tier settings
- **misc:** `graph`, `graph filters`, `views member`, `views member defaults`, `migrations`, `connectors list org|personal`, `synthetics rules`, `aggregations metrics config|config default`, `integrations data config`

Run `groundcover raw list` / `groundcover raw list <group>` to confirm the exact name before invoking.

## SDK-backed CRUD pattern

```sh
groundcover <resource> list   [--query '<filter>']
groundcover <resource> get    <id>
groundcover <resource> create --body-file <file>   # or --body-json '<json>'
groundcover <resource> update <id> --body-file <file>
groundcover <resource> delete <id>
```

Body files: `.json` or `.yaml`.

### Resources (all follow the pattern above)

- **dashboards** — also `archive <id>`, `restore <id>`
- **monitors** — `--query 'monitor_name = "cpu"'`
- **silences** — `list --active`
- **recurring-silences**
- **connected-apps** — `--query 'type:slack-webhook'`
- **notification-routes** — `--query 'prod'`
- **synthetics**
- **secrets** — also `hash <id>`
- **workflows**

### Auth / RBAC

```sh
groundcover api-keys list
groundcover api-keys create --body-file key.json
groundcover service-accounts list
groundcover service-accounts create --body-file sa.json
groundcover ingestion-keys list
groundcover policies list
groundcover policies apply --body-file policy.json
groundcover policies audit-trail <id>
```

### Pipeline singletons (`get` / `create` / `update` / `delete`, no id)

```sh
groundcover logs-pipeline get
groundcover metrics-pipeline get
groundcover traces-pipeline get
groundcover metrics-aggregator get
```

### Integrations (typed)

```sh
groundcover integrations list
groundcover integrations describe <type>
groundcover integrations create <type>      --body-file config.json
groundcover integrations update <type> <id> --body-file config.json
```

### Observability / read commands (body-file driven)

```sh
groundcover logs search          --body-file body.json
groundcover traces search        --body-file body.json
groundcover metrics query        --body-file body.json   # PromQL range/instant
groundcover metrics names        --body-file body.json   # list metric names
groundcover metrics keys         --body-file body.json   # label keys for a metric
groundcover metrics values       --body-file body.json   # label values for a key
groundcover search discovery     --body-file body.json   # facet / discovery
groundcover search keys          --body-file body.json
groundcover search values        --body-file body.json
groundcover k8s clusters         --body-file body.json
groundcover k8s workloads        --body-file body.json
groundcover k8s events-search    --body-file body.json
groundcover k8s events-over-time --body-file body.json
```

Pipe to `jq` to extract fields, or pass `--raw` to dump the raw response.

#### Body templates for observability

Times are RFC 3339 UTC (`2026-05-28T00:00:00Z`). Wall-clock-now isn't built-in — compute with `date -u`. All searches share the same shape (`logs search`, `traces search`, `k8s events-search`):

```json
{
  "start": "2026-05-28T00:00:00Z",
  "end":   "2026-05-28T01:00:00Z",
  "query": "<GCQL>",
  "filters": "",
  "sources": []
}
```

`metrics query` (note the **capitalized** field names — this is the API):
```json
{
  "Promql":    "rate(http_requests_total[5m])",
  "Start":     "2026-05-28T00:00:00Z",
  "End":       "2026-05-28T01:00:00Z",
  "Step":      "60",
  "QueryType": "range",
  "Conditions": []
}
```
Use `"QueryType": "instant"` and omit `Step` for a point query.

`k8s workloads` / `k8s clusters`:
```json
{
  "conditions":  [],
  "sources":     [],
  "gcqlFilter":  "namespace = 'prod'",
  "limit":       100
}
```

## Raw commands

```sh
groundcover raw list                          # list groups
groundcover raw list <group>                  # list commands in group
groundcover raw k8s clusters list
groundcover raw dashboards get --dashboard-id <id>
groundcover raw metrics query-range --body-file body.json
groundcover raw prometheus api query --query query='up'
groundcover raw grafana dashboards get --dashboard-uid <uid>
groundcover raw grafana dashboards save --body-file dashboard.json
groundcover raw grafana folders list
groundcover raw grafana ds query --body-file query.json
```

### Storage management

Admins can read and update lifecycle settings for `logs`, `traces`, `events`, `measurements` (APM), and `monitor_instance` (monitor issues):

```sh
groundcover raw storage-management get --data-type logs --raw \
  | jq '{retention,version,cold_move_duration,cold_volume,custom_rules:(.custom_rules // [])}' \
  > storage.json
# Edit storage.json, preserving every writable field and the complete rule list.
groundcover raw storage-management update --data-type logs --body-file storage.json
```

Updates use optimistic concurrency and replace the writable settings document. Always start from `get`, carry forward its current `version`, and preserve `retention`, `cold_move_duration`, `cold_volume`, and the complete `custom_rules` list; omitting `custom_rules` removes existing rules. A successful update increments `version`. Each observed custom rule contains `name`, `retention`, and a gcQL `filters` expression.


### Grafana native dashboards

Groundcover also embeds Grafana at `/grafana`. These are **not** the same as Groundcover's first-class `dashboards` SDK resource, so use `raw grafana …` when you need native Grafana JSON dashboards, folders, permissions, annotations, datasource-backed variable values, or panel query execution.

**Auth:** the embedded Grafana lives behind a session-gated proxy that ignores the `gcsa_` API key, backend ID, and tenant UUID. A bearer/`gcsa_` request to `/grafana/api/*` just returns the ~980KB Grafana SPA `index.html` (HTTP 200, `text/html`), never JSON. These commands require a Grafana service account token (`glsa_…`) instead: set `GROUNDCOVER_GRAFANA_SERVICE_ACCOUNT_TOKEN` (or `--grafana-token`). Run any `raw grafana …` command without it and the CLI prints a full setup guide.

**Generating a token** (needs a groundcover tenant admin). The token comes from groundcover's *official* CLI (`github.com/groundcover-com/cli`), which unfortunately also installs a binary named `groundcover`. Its installer drops it at `~/.groundcover/bin/groundcover` and prepends that dir to your PATH, so afterwards `groundcover` resolves to the official CLI and shadows this one. Invoke the official binary by full path to avoid the collision:
```sh
sh -c "$(curl -fsSL https://groundcover.com/install.sh)"      # installs to ~/.groundcover/bin
~/.groundcover/bin/groundcover auth login                     # auth flow
~/.groundcover/bin/groundcover auth generate-service-account-token   # prints glsa_… once
export GROUNDCOVER_GRAFANA_SERVICE_ACCOUNT_TOKEN=glsa_...     # hand it to this CLI
```
To keep this CLI as `groundcover`, remove the `~/.groundcover/bin` PATH line the installer adds to your shell rc.

Common commands:
```sh
groundcover raw grafana search --query query='service slo' --query folderUIDs=general
groundcover raw grafana dashboards get --dashboard-uid streamling-pipeline-slo
groundcover raw grafana dashboards save --body-file dashboard.json
groundcover raw grafana folders list
groundcover raw grafana datasources label-values --datasource-uid <uid> --label project_id --query start=<unix> --query end=<unix>
groundcover raw grafana ds query --query ds_type=prometheus --body-file query.json
```

Grafana raw commands default to `https://app.groundcover.com` (the webapp host), while normal API/SDK commands default to `https://api.groundcover.com`. Pass `--base-url` only for non-standard deployments.

Raw flags: `--body-json`, `--body-file`, `--set dotted.path=value`, `--query key=value` (repeatable), generated path flags (e.g. `--dashboard-id`), `--raw`. Many raw commands ship a default body captured from the webapp HAR, so you can run them with no `--body-*` at all and override specific fields with `--set`.

## Recipes

### Last hour of error logs for a service
```sh
END=$(date -u +%FT%TZ); START=$(date -u -v-1H +%FT%TZ)   # GNU: date -u -d '1 hour ago' +%FT%TZ
jq -n --arg s "$START" --arg e "$END" '{
  start:$s, end:$e,
  query: "service_name = \"api\" AND level = \"error\"",
  filters: "", sources: []
}' | groundcover logs search --body-file /dev/stdin | jq '.[] | {ts:.timestamp, pod:.pod_name, body:(.body|fromjson?)}'
```

> **`logs search` returns a bare JSON array at the root** — `jq '.[]'`, not `.logs[]`. The human-readable message lives in the **`body`** field as a JSON *string* (parse with `fromjson`). Useful top-level fields: `pod_name`, `container_name`, `namespace`, `workload`, `level` (normalized lowercase — `error`/`warning`/`debug`, not the `WARN`/`DEBG` you see inside `body`), `cluster`, `timestamp`, `trace_id`.

### p99 latency for a workload (last 30m, PromQL)
```sh
END=$(date -u +%FT%TZ); START=$(date -u -v-30M +%FT%TZ)
jq -n --arg s "$START" --arg e "$END" '{
  Promql: "histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket{service=\"api\"}[5m])))",
  Start: $s, End: $e, Step: "60", QueryType: "range", Conditions: []
}' | groundcover metrics query --body-file /dev/stdin
```

### Crashlooping or restarting pods
```sh
jq -n '{ conditions: [], sources: [], gcqlFilter: "status != \"Running\"", limit: 200 }' \
  | groundcover k8s workloads --body-file /dev/stdin \
  | jq '.workloads[] | select(.restarts > 0) | {name, namespace, status, restarts}'
```

### Recent k8s events for a namespace
```sh
END=$(date -u +%FT%TZ); START=$(date -u -v-1H +%FT%TZ)
jq -n --arg s "$START" --arg e "$END" '{
  start:$s, end:$e,
  query: "namespace = \"prod\" AND type = \"Warning\"",
  filters: "", sources: []
}' | groundcover k8s events-search --body-file /dev/stdin
```

### Find slow traces, then pivot to their logs
```sh
END=$(date -u +%FT%TZ); START=$(date -u -v-30M +%FT%TZ)
jq -n --arg s "$START" --arg e "$END" '{
  start:$s, end:$e,
  query: "service_name = \"api\" AND duration_ms > 1000",
  filters: "", sources: []
}' | groundcover traces search --body-file /dev/stdin \
  | jq -r '.[] | .trace_id' | head -5 \
  | while read tid; do
      jq -n --arg s "$START" --arg e "$END" --arg t "$tid" '{
        start:$s, end:$e, query: ("trace_id = \"" + $t + "\""), filters: "", sources: []
      }' | groundcover logs search --body-file /dev/stdin
    done
```

### Discover what labels/fields exist on a stream
```sh
# What metric names match a prefix?
jq -n '{ prefix: "http_" }' | groundcover metrics names --body-file /dev/stdin

# What labels does a specific metric have?
jq -n '{ metric: "http_request_duration_seconds" }' | groundcover metrics keys --body-file /dev/stdin

# What values does a label take?
jq -n '{ metric: "http_request_duration_seconds", key: "service" }' \
  | groundcover metrics values --body-file /dev/stdin
```

### GCQL quick reference (logs/traces/events queries)
- Equality: `service_name = "api"` (double quotes inside JSON → `\"`)
- Comparison: `duration_ms > 1000`, `status_code >= 500`
- Boolean: `AND`, `OR`, `NOT`
- Substring: `message ~ "timeout"`, regex: `message ~* "^panic:"`
- Membership: `level IN ("error", "fatal")` — works on a **named field** only
- **Freetext phrase:** a bare quoted string, e.g. `container = "my-service" AND "database unavailable"`. `IN(...)` is **not** valid as freetext (errors `freetext 'in(...)' is not supported`) — expand to `level = "error" OR level = "fatal"`.
- **Never send an empty `query`** — `query: ""` → 500 `pipeline cannot be nil`. Always supply at least one term.
- Null check: `trace_id IS NOT NULL`

Enumerating fields: `search discovery`/`search keys` are finicky (discovery requires `Limit` + `Type` and may still 400). The reliable move is to fetch one sample log and inspect `keys` and the parsed `body`.

### Find then silence a monitor
```sh
groundcover monitors list --query 'monitor_name ~ "ingest"'
groundcover silences create --body-json '{"monitor_id":"<id>","duration_seconds":3600,"reason":"deploy"}'
```

### Dump every dashboard
The list field is **`uuid`**, not `id` (`.id` is null). Each entry also has `archivedTimestamp` — skip archived ones (active = `0001-01-01T00:00:00.000Z`).
```sh
groundcover dashboards list \
  | jq -r '.[] | select(.archivedTimestamp == "0001-01-01T00:00:00.000Z") | .uuid' \
  | while read id; do groundcover dashboards get "$id" > "dashboards/$id.json"; done
```

### Build a dashboard deep-link with pre-filled template variables
`groundcover dashboards get <uuid>` returns the variable definitions under `.preset` (a **JSON string** — parse with `fromjson`). Find a dashboard and inspect its vars:
```sh
groundcover dashboards list | jq -r '.[] | select(.name|test("prod";"i")) | "\(.uuid)\t\(.name)"'
groundcover dashboards get <uuid> | jq -r '.preset | fromjson | .variables'
# each var: { kind:"list", spec:{ values:{default:["*"]}, datasource:{key,kind,metric}, variableName } }
```
The webapp encodes selected variable values in a `variables` **URL query param** — a URL-encoded JSON object keyed by `$<variableName>`. Each entry needs `name`, `key`, `values` (array; supports globs like `myapp*`), `datasource` (usually `"metrics"`), and `refiner.metric` (the source metric from the var's `datasource.metric`).

**Pin EVERY variable you care about — including ones you want wide open.** Any var you omit falls back to the dashboard's *saved default*, which is often NOT `*` (e.g. a hardcoded `deployment` hash, or `shard: primary`). To get a truly broad view, explicitly set those to `["*"]`. Always confirm a label value exists before using it — e.g. `app_kubernetes_io_instance` may have no bare `myapp`, only `myapp-web-0` etc., so use the `myapp*` glob.

Build it with jq so the encoding is correct:
```sh
VARS=$(jq -cn '{
  "$cluster":{name:"cluster",key:"cluster",values:["example-cluster"],datasource:"metrics",refiner:{metric:"my_metric_total"}},
  "$deployment":{name:"deployment",key:"deployment",values:["*"],datasource:"metrics",refiner:{metric:"my_metric_total"}},
  "$app_kubernetes_io_instance":{name:"app_kubernetes_io_instance",key:"app_kubernetes_io_instance",values:["myapp*"],datasource:"metrics",refiner:{metric:"my_metric_total"}}
}')
ENC=$(jq -rn --arg v "$VARS" '$v|@uri')
echo "https://app.groundcover.com/dashboards?backendId=groundcover&tenantUUID=<your-tenant-uuid>&duration=Last+1+hour&viewId=<uuid>&qb-disable-auto-focus=true&variables=${ENC}"
```
Notes: the dashboard opens via `viewId=<uuid>` (not the `/dashboards/<uuid>` path); `duration` takes UI strings like `Last+1+hour` / `Last+5+minutes`.

### Ad-hoc Prom query via raw
```sh
groundcover raw prometheus api query --query query='up{namespace="prod"}'
```

## Building & editing dashboards

The interesting part of a dashboard isn't the CRUD verbs (`dashboards get/list/create/update/archive/restore`) — it's the **preset**, where the whole panel layout lives in one field.

### Preset structure

`dashboards get <uuid>` returns the dashboard with `.preset` as a **JSON string** (parse with `fromjson` / `json.loads`; re-serialize to a string before writing back). Shape:

```jsonc
{
  "spec": { "layoutType": "ordered", "crosshairSyncEnabled": true },
  "layout": [ /* one entry per TOP-LEVEL item, placed on a 24-col grid */ ],
  "widgets": [ /* the actual panels, referenced by id from layout */ ],
  "duration": "Last 6 hours",   // UI duration string
  "variables": [ /* template vars, same shape as the deep-link recipe */ ],
  "schemaVersion": 7
}
```

- **`layout`** — top-level grid placement. Each entry `{ "id":"A", "h":12, "w":24, "x":0, "y":0, "minH":8 }`. Grid is **24 columns wide** (`w:8` = a third, `w:12` = half); `id` must match a widget `id`. You hand-compute `y` to stack rows — there is no auto-flow.
- **`widgets`** — `{ id, name, type, queries:[{id, expr, dataType:"metrics", editorMode:"editor"}], visualizationConfig:{ type, selectedUnit, ... } }`. `expr` is PromQL with `$var` substitutions.
- Widget types: `time-series`, `stat`, `text` (markdown in `content`, no queries — use for headers/dividers), `section`.

### Sections (collapsible groups)

A section is a widget `{ id, name, type:"section", color, isCollapsed:false }`. Its **layout** entry carries a `children` array of *relative*-positioned panel entries: `{ id, h, w:24, x:0, y:0, children:[ {h,w,x,y,id,minH}, ... ] }`. The header occupies the top ~2 rows, so children start at `y:2`.

### The update contract

`dashboards update <uuid>` body MUST include **`currentRevision`** (the current `.revisionNumber`) — it's optimistic concurrency. Omit it → `Field validation for 'CurrentRevision' failed on the 'required_if' tag`. Re-`get` after every successful update to read the bumped revision before the next write.

```sh
groundcover dashboards get <uuid> > d.json
# NEW_PRESET must be the preset object re-serialized to a STRING
jq -n --slurpfile d d.json --arg preset "$NEW_PRESET" '{
  name: $d[0].name, viewType: ($d[0].viewType // "explore"),
  status: "active", currentRevision: $d[0].revisionNumber, preset: $preset
}' | groundcover dashboards update <uuid> --body-file /dev/stdin
```

### Validation rules (the API only says `Dashboard validation failed`)

The update endpoint returns an **opaque** `400 {"message":"Dashboard validation failed"}` — no field, no offending widget. When you hit it, **bisect**: deploy a minimal preset (one section / one panel) and add pieces back until it breaks. Two non-obvious rules that each cost real bisecting time:

1. **Stat widgets (`visualizationConfig.type:"stat"`) validate ONLY as flat top-level `layout` entries — NEVER inside a section's `children[]`.** Time-series widgets work in both. To build an overview stat row, place the stat panels as flat top-level items (with a `text` header widget above them) and keep time-series panels in sections.
2. **Section `color` accepts only a fixed palette.** Verified valid: `gray`, `purple`, `teal`. Verified rejected: `green`, `blue`, `red`, `yellow`, `orange`.

### Stat panels read "No Results" on lagging metrics → wrap in `last_over_time`

Stat panels evaluate as an **instant query at "now"**. A metric that lags real-time leaves that instant window empty → the panel shows **"No Results"** even though it graphs fine in a time-series panel (which range-queries the whole window). Metrics pulled from polled integrations (e.g. cloud-provider integrations like CloudWatch) commonly lag minutes behind real-time, so stat panels built directly on them come up blank.

Fix: wrap the selector in `last_over_time(<selector>[30m])` **inside** the aggregation so the instant evaluation reaches back past the staleness:

```promql
max(last_over_time(my_metric{...}[30m]))   # NOT  max(my_metric{...})
```

The `*_over_time` wrappers render fine in stat panels (e.g. a working `100 * avg_over_time((...)[7d:5m])` uptime stat). In-cluster metrics scraped in real-time (~1s fresh) don't need it.

### Verifying a dashboard without the UI

If the headless browser hits Groundcover's SSO wall (no session), you can't screenshot-verify. Verify via the API instead:
- **Every query returns data:** pull the deployed preset, substitute concrete values into each `expr` (a `$var` → a real label value; a wildcard var → a `=~".+"` regex), and run it through `metrics query` as a **range** query. Use a window ≥ the metric's emit cadence (sparse integration metrics may only emit every few minutes).
- **Geometry:** assert no two layout rects overlap and every `x+w ≤ 24` (top-level entries and each section's `children`).
- **Caveat:** the CLI can't reliably run instant queries (see Common issues), so you can't reproduce the stat-panel instant path from the CLI — reason from staleness + range data.

### Polled-integration metrics (e.g. CloudWatch): label-scheme gotchas

Metrics ingested from a polled cloud integration differ from in-cluster exporter metrics in ways that bite when building dashboards:
- **They lag real-time** (see the stat-panel note above) — minutes, not seconds.
- **They're often multiplied by a `stat` dimension** (`stat=average/maximum/minimum`) — every series appears 3×. Always filter to the one you want (e.g. `stat="average"`) or aggregations double/triple-count.
- **The env/scope label is integration-named**, not a clean `env`. If the same resource is *also* covered by an in-cluster exporter, the two families carry **different label keys** for the same concept (e.g. `instance_id` vs `instanceid`). Use a **separate template variable per label scheme** rather than forcing one variable to span both.

## Production observability triage flow

When asked "why is X broken in prod" / "what's going on with service Y":

1. **Scope the time window.** Default to last 1h. Compute `START`/`END` with `date -u` (see recipes).
2. **Logs first.** `groundcover logs search` with a GCQL filter on `service_name` and `level = "error"`. Cheap and usually answers it.
3. **Traces if latency / slow.** `groundcover traces search` filtering on `duration_ms`, `status_code`, or `service_name`. Grab a few `trace_id`s and pivot back to logs via `trace_id = "..."`.
4. **Metrics for shape over time.** `groundcover metrics query` with PromQL — error rate, p99, saturation. Use `range` for graphs, `instant` for a point check.
5. **K8s if "is it even running".** `groundcover k8s workloads` for status/restarts; `groundcover k8s events-search` for `Warning` events (OOMKilled, FailedScheduling, BackOff).
6. **Don't know the field name?** `groundcover search discovery`, `metrics names`, `metrics keys`, `metrics values` to enumerate.
7. **Need to silence noisy alerts during the incident?** `groundcover monitors list --query …` → `groundcover silences create`.

## When unsure which command exists

1. Check the resource list above.
2. `groundcover --help` and `groundcover <resource> --help`.
3. For raw: `groundcover raw list`, then `groundcover raw list <group>`.

## Common issues

### `401 Unauthorized`, token-prefix/length errors, or empty results
- `Invalid token prefix` / `Invalid token length` → the key isn't a `gcsa_` service-account key (see **Auth**). A `gcik_` ingestion key is the common mistake.
- `401` with a valid-looking `gcsa_` key → the key is for a **different tenant**. For other tenants also set `GROUNDCOVER_TENANT_UUID` and (if applicable) `GROUNDCOVER_BASE_URL`.
- Otherwise verify the env var is actually exported in the current shell.

### SDK command rejects the body
Body shape drifted from the SDK contract. Fetch an existing resource with `get <id>` and use its shape as a template.

### Empty results from `logs search` / `traces search` / `events-search`
Almost always one of:
- Time window is wrong / too narrow. `start` must be **before** `end`, both RFC 3339 UTC.
- GCQL field name doesn't exist in this tenant. Use `search discovery` / `search keys` to enumerate.
- Query string isn't escaped — inside JSON, `service_name = "api"` becomes `"service_name = \"api\""`.

### `metrics query` returns no data but the metric exists
- Field names are **capitalized** (`Promql`, `Start`, `End`, `Step`, `QueryType`) — lowercase is silently accepted by JSON but ignored.
- `Step` is a string (`"60"`), not a number.
- For instant queries set `"QueryType": "instant"` and omit `Step`. **Observed caveat:** in testing the CLI `metrics query` has returned `400 metricsQueryBadRequest` for instant bodies (every shape tried — `Start`==`End`, `Time`, with/without `QueryType`), even on fresh metrics. When you need a single current value, fall back to a **range** query (`QueryType:"range"` + `Step`) over a short window and take the last point. (Genuine instant PromQL is also reachable via `raw prometheus api query`, but that passthrough may target a different store than `metrics query`.)
- Parsing the response: results live at `.data.result // .result`; each `values` entry is `[unix_ts, "stringvalue"]`. Sum a range with `[.values[][1]] | map(tonumber) | add`; format the timestamp with `strftime`.

### `logs search` times out (`context deadline exceeded`)
Chatty, high-volume workloads flood logs, so broad or single-pod queries over even a ~60–90s window can exceed the deadline. Fixes:
- Always include a **discriminating term** (a phrase + `container`/`pod`), not just a pod by itself.
- **Narrow the window** and raise `--timeout` (e.g. `--timeout 120s`).
- Avoid large `OR` chains in one query — run them separately.
- For "how often / over time" questions prefer **`metrics query`** over scraping logs.

### `monitors` editing & search
- `monitors get` / `update` speak **YAML** (even with `--raw`). Workflow: `monitors get <uuid> > mon.yaml`, edit, `monitors update <uuid> --body-file mon.yaml`. A successful update returns `{"status":202}` (applied asynchronously — re-`get` to confirm).
- Slack-app destinations need **both** `connectedApps: [<app-id>]` and `connectedAppParams.<app-id>.channels: [{id, name}]`. The webapp PUT is YAML `text/plain` with that shape. SDK ≥ v1.376 encodes `connectedAppParams`; older SDKs dropped it and the API returned `400 connectedApps[0]: channels is required for slack-app route params`.
- Monitor model lives under `model.queries[].sqlPipeline.filters.conditions[]` — each condition is `{key, origin: root, type, filters:[{op, value}]}`; freetext uses `type: freetext` + `op: phrase_search`. Other knobs: `instantRollup` (e.g. `1 minute`), `thresholds[]`, `evaluationInterval.{interval, pendingFor}`.
- `monitors list --query 'monitor_name ~ "..."'` → 400 `regexp requires a string column type`. Use `monitor_name = "exact"`, or list all and filter with `jq`.

### Raw command "not found" inside a group
The endpoint isn't in the captured HAR. Use the SDK form if one exists, or regenerate — regeneration lives in the `groundcover-cli` repo (`go run ./scripts/generate-commands.go <har>`).
