# SMT requests

Sail runs complete SMT-LIB transcripts through its bundled pinned Z3. The
following request works independently of a Rust project. Save it as
`query.json`:

```json
{
  "version": 1,
  "input": {
    "kind": "smt",
    "queries": [
      {
        "obligation_id": "count-bound",
        "requirement_ids": ["REQ-001"],
        "backend": "z3",
        "script": "(set-option :produce-models true)\n(declare-const count Int)\n(assert (> count 2))\n(check-sat)\n(get-model)\n"
      }
    ]
  }
}
```

```sh
sail runtime capabilities
sail runtime execute --file query.json
```

Use `sail runtime --help` to inspect the runtime commands; they are not listed
by top-level `sail --help`. Check capabilities once during setup, or when a
request reports that its backend is unavailable.

Read the execution outcome and ordered satisfiability checks in the JSON
response. This formula is satisfiable; its model gives a value of `count`
greater than two. Models require `sat`; unsat cores require `unsat` and the
appropriate produce-unsat-cores option and named assertions in the script.

Repeat the same request to reuse decided output from the on-disk cache. The key
binds script bytes, limits, pinned solver identity and execution settings.
Each entry in `output.results` reports reuse in its `cache_hit` field.
Unknown answers, timeouts and incomplete executions are not cached as successful
evidence. Each request is a complete transcript; there is no solver session
handle carried between calls. Push/pop and multiple checks can occur inside
one transcript.

For rejected requests, check the admission error and the maintained schema
below. Requirement IDs must be sorted and unique; unknown JSON fields are
rejected. For a resource-limited or incomplete result, inspect its outcome and
configured limits before changing the request or reporting an answer.

## MCP

With Sail's MCP server configured:

1. Call `runtime_capabilities` with `{}` to inspect the installed backend.
2. Call `runtime_execute` with `{"request": QUERY_DOCUMENT}`, using the JSON
   document above as `QUERY_DOCUMENT`.
3. Read per-query outcomes, checks and any requested products. Responses retain
   the caller's obligation and requirement IDs, including on a cache hit.

Unknown or incomplete MCP executions set `isError`; read the structured result
to distinguish them from a decided answer.

The server starts the shared daemon when needed. If an older daemon lacks a
compatible runtime endpoint, report the incompatibility and inspect `sail status`.
Do not substitute another backend or treat installation readiness as a solved query.

The installed MCP tool schema and runtime help describe the interface for that
build. The maintained request schema, admission rules and shared-service setup:
https://github.com/Chelis-Lang/sail/blob/main/docs/runtime.md
