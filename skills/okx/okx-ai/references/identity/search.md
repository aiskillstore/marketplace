# Agent and service discovery

## Module Description

A Service **MUST** be matched and explicitly selected by the User before `task-create-prepare`.
Never create a task directly from an Agent ID, Service ID, service name, or search request.

## Flow

### Extract arguments

#### Query context

Extract explicit service/ASP selectors, price bounds, and capability-focused search keywords from
the current query. Use the previous query only to resolve follow-ups:

1. For a standalone or unrelated request, use only the current query.
2. For a follow-up, use the previous query only to fill omitted context; the current query
   overrides conflicting, replaced, or rejected conditions.
3. Use only explicit or contextually resolved content; never invent conditions.

#### Output contract

Build every field in this internal argument object; use `null` for absent scalars and `[]` for no
keywords:

```typescript
type SearchArguments = {
  "asp-agent-id": string | null;
  "asp-name": string | null;
  "service-name": string | null;
  "sid": string | null;
  "min-payment-token-amount": number | null;
  "max-payment-token-amount": number | null;
  "keywords": string[];
};
```

#### Extraction rules

Apply these extraction rules:

1. **Names and IDs:** Classify an ID before removing syntax markers, using this precedence:
   1. An explicit Service ID or SID label maps to `sid`.
   2. An explicit Agent ID or ASP ID label maps to `asp-agent-id`.
   3. In an Agent/service discovery or service-use request, an otherwise unlabeled `#<digits>` maps
      to `asp-agent-id`; `#` is an Agent ID sigil, not disposable punctuation. Accept intervening
      whitespace and the full-width `＃` form.
   4. Forms such as `agent9967`, `agent 9967`, or a numeric ID used as the owner/provider of services
      map to `asp-agent-id`.
   5. A bare numeric value, including digits merely adjacent to the generic word `service`,
      is ambiguous. Ask whether it is a Service ID or Agent ID and wait without searching. Only an
      explicit Service ID or SID label maps such a value to `sid`.

   Explicit textual labels override the `#` convention. After classification, preserve the value
   verbatim except for removing its label, quotes, brackets, delimiters, whitespace, and an adjacent
   `#` or `＃`. Never retry or reinterpret an ID as the other type because a search returned no
   results.
2. **Price bounds:** Map lower-bound wording (`above`, `greater than`, `no less than`, `at least`,
   `>`, `>=`) to `min-payment-token-amount`; map upper-bound wording (`below`, `less than`, `no more
   than`, `at most`, `<`, `<=`) to `max-payment-token-amount`; map an explicit range to both. Map an
   explicit request for a free or zero-price Service (`free`, `no charge`, `zero-cost`) to `max-payment-token-amount: 0`; because Service prices are non-negative,
   this means an exact zero price. Treat it as a price constraint, never as a keyword. Do not apply
   this mapping to a free trial, gas-free wording, a negated request such as `not free`, or text about
   something other than the Service price.
3. **Keywords:** MUST keep only requested capabilities and outputs with required subjects, modifiers,
   and scopes. MUST use only keywords explicitly present in the current query or carried-over context;
   MUST NOT invent, infer, paraphrase, translate, or expand them. Exclude names, IDs, price
   constraints, request wrappers, filler, rejected intent, generic service words, and provider/listing
   metadata. When a follow-up adds a scope, attach it to the previous capability as one phrase. Return
   1–5 concise, deduplicated phrases; if no capability or output is requested, MUST return
   `"keywords": []`.

#### Examples

Examples show only non-null/non-empty fields; apply the Output contract defaults to omitted fields.

| Previous query | Current query | Extracted arguments |
|---|---|---|
| — | `Find a market analysis service priced between 8 and 20` | `{"min-payment-token-amount":8,"max-payment-token-amount":20,"keywords":["market analysis"]}` |
| `Find a BTC market-analysis service` | `Switch to ETH, below 10` | `{"max-payment-token-amount":10,"keywords":["ETH market analysis"]}` |
| — | `Find the free services from #2189` | `{"asp-agent-id":"2189","max-payment-token-amount":0,"keywords":[]}` |
| — | `用 Service ID #2189 找服务` | `{"sid":"2189","keywords":[]}` |
| — | `帮我找一下13373服务` | Ask whether `13373` is an Agent ID or Service ID; do not search. |

`sid` and `asp-agent-id` are both numeric strings; never use their numeric shape alone to distinguish
them.

### Run the search

Run `service-match` only after extraction has produced unambiguous search arguments.

If an ID requires clarification, ask the User and stop; do not search. Otherwise, for every new
service-use request, including one with an exact Service ID, Agent ID, or service name, run
`service-match`, display the results, and wait for the User to select a Service in a subsequent
message.

Pass the non-null/non-empty arguments to:

```bash
onchainos agent service-match \
  [--keywords <kw>...] [--asp-agent-id <id>] [--asp-name <name>] \
  [--service-name <name>] [--sid <sid>] \
  [--min-payment-token-amount <n>] [--max-payment-token-amount <n>] \
  [--limit <n>]
```

A Service ID **MUST** use `--sid`; **NEVER** use `--service-id`.

If the user does not request a result count, **MUST** pass `--limit 3` by default.
When requested, `--limit` **MUST** be `1–10`; values outside this range are invalid.

### Read the result

Read `services[]`, `searchAfter`, `hasMore`, and `tip`.
**MUST** render the result with the already-loaded `output-templates.md` applicable template.
If `output-templates.md` was not loaded with this search reference, do not produce a user-facing
result until it has been loaded.
Do not load any A2A creation or action reference before the user explicitly
selects a Service and `task-create-prepare` returns its next action.

### Display results

**MUST** group `services[]` by `asp.aspAgentId` in returned order and render
each group with the `Agent Service group` template in `output-templates.md`.

**MUST** render all Agent groups, then the localized CLI `tip` once.

```text
<CLI-returned tip>
```

### Pagination

When `hasMore == true`, `searchAfter` is non-empty, and the user asks for more, run:

```bash
onchainos agent service-match --search-after <searchAfter> --limit <n>
```

Use the `searchAfter` value returned by the immediately preceding query exactly as returned.
Do not modify, decode, encode, truncate, or regenerate it. Apply the same rules to every page.

### Select a service

Use the selected Service's numeric `sid` and its owning `asp.aspAgentId`
internally. **NEVER** show `sid`.

**MUST** stop. Only after explicit confirmation or selection in a subsequent
User message, route by the selected Service's `serviceType`:

- `A2A`: pass its numeric `sid` to
  [`../a2a/user/create-prepare.md`](../a2a/user/create-prepare.md).
- `A2MCP`: pass its `id` field as the numeric `sid`, and its `asp.aspAgentId`, to
  [`../a2mcp/handoff.md`](../a2mcp/handoff.md) for explicit MCP preparation.
- Missing or unsupported type: stop; do not guess a preparation path.
