# A2MCP over MCP transport (Streamable HTTP / SSE)

## When this applies
`payment quote` returned `data.mcpTools[]`, OR the endpoint URL ends in `/mcp`/`/sse`, OR the bare
probe returned `Content-Type: text/event-stream` or a JSON-RPC body. The paywall is at the
`tools/call` layer — a bare probe / `tools/list` returns no 402; only a real `tools/call` does.

The CLI does the whole `initialize → tools/list → tools/call` JSON-RPC handshake and SSE parsing
internally. Do NOT hand-write JSON-RPC or parse SSE yourself.

## Three-step flow
1. **Discover** — `onchainos payment quote <url>`
   → returns `data.mcpTools[]` (each `{name, description?, inputSchema?}`); no `paymentId`; free.
2. **Trigger 402** — pick a tool per the user's intent (`AskUserQuestion` if ambiguous), assemble
   `--param key=value` from the tool's `inputSchema`, then
   `onchainos payment quote <url> --tool <name> --param k=v …`
   → the CLI issues `tools/call`. A paid tool returns 402 → `data.{paymentId,accepts,candidates}`
     (identical to a REST quote). A free / first-N-free tool returns `data.result` instead.
3. **Pay** — confirm the amount/scheme (Step A3), then
   `onchainos payment pay --payment-id <id> [--selected-index <n>] --yes`
   → the CLI TEE-signs and replays the SAME `tools/call` with a `PAYMENT-SIGNATURE` header, then
     parses the SSE response + `PAYMENT-RESPONSE` receipt.
   (`--selected-index <n>` picks an `accepts[]` entry when the 402 offered multiple schemes.)

## `--param` coercion (must match the tool's `inputSchema`)
The CLI coerces each `--param` value per `inputSchema.properties[key].type`:
- `integer` / `number` → JSON number   • `boolean` → JSON bool   • `object` / `array` → parsed JSON
- other type / no schema / parse failure → kept as a string

Example: `zip` is declared `string` → `--param zip=01234` stays `"01234"`; `n` is declared
`integer` → `--param n=5` becomes JSON `5`. The coerced values are persisted in the paymentId state
and replayed verbatim by `payment pay`.

## SSE / tiered billing
The response is a Streamable-HTTP SSE stream (`event: message` / `data:` lines). In-stream
notifications (e.g. `progress`) that arrive before the response are skipped; the first `data:` line
carrying a JSON-RPC `result`/`error` is taken. Tiered billing is supported: `tools/list` is free,
a paid `tools/call` returns 402, and a "first N calls free" tool returns no 402 — that non-402
`tools/call` is a **free result** surfaced as `data.result`.

## Do NOT hallucinate a payment
A bare probe / `tools/list` returning no 402 does **NOT** mean the service is free — on an MCP
endpoint the paywall lives at the `tools/call` layer, so a tool's price only surfaces when you
actually invoke it. Never invent or assume a payment. If a real `tools/call` genuinely returns no
402 (a non-402 `data.result`), report the endpoint as **free / not x402-enabled** and stop — do not
fabricate a `paymentId`, an `accepts[]` challenge, or a signing step that the server never asked for.

## Error tokens (grep-able first word of `.error`)
- `endpoint_unreachable` — `initialize` / `tools/list` / `tools/call` transport failure; or a bare
  405 on a non-`mcp|sse` URL with no `--tool` (retry with `--tool <name>` or `--method POST`).
- `invalid_input` — `--tool` names a tool not in the discovered catalog (the message lists the
  available tool names).
- `unsupported` — the 402 challenge's `accepts[]` has no known payment scheme.

The destructive `payment pay` confirming gate (exit 2, `{confirming,…}`) and all REST error tokens
are reused unchanged.

## Not in scope
stdio / local MCP transport; paying for MCP `resources` / `prompts`; non-x402 MCP payment schemes;
cross-process MCP session caching (`quote` and `pay` each re-handshake).
