---
name: sail-verification
description: Verify Rust with Verus, check proof repairs, and run cached Z3 queries with Sail. Use when cargo verus verify is slow, when developing Verus proofs, or when giving coding agents SMT-LIB solver access through the CLI or MCP.
license: MIT
metadata:
  version: "1.0.0"
---

# Sail verification

Sail reuses solver answers and proofs across edits so developers and agents
spend less time waiting for Verus. It also runs SMT-LIB queries through bundled
Z3 with a persistent result cache.

Sail runs on Linux x86-64 and Apple-silicon macOS. Use its CLI or an already
configured Sail MCP server.

## Verify Rust

In a Cargo project using Verus, run:

```sh
sail verify --output json
```

`sail verify` takes the arguments you would pass to `cargo verus verify`.

Use the failure locations and diagnostics to revise the code or proof, then
verify again. Preserve the intended contract; weakening a specification is not
a fix for an implementation that violates it. A selected function passing is
not evidence that the entire target passes.

For a new Verus library, run `sail new --lib demo`, then `cd demo`. Write the intended Verus
contracts and proofs along with the Rust implementation.

Read [Verus workflows](references/verus.md) for standalone files, MCP,
background preparation, explicit jobs, proof-repair checks and cache management. Inspect the installed help before
choosing the standalone workflow; the reference explains release availability.

## Run SMT queries

For repeated Z3 work outside Rust, check the installed solver once with
`sail runtime capabilities`, then submit complete SMT-LIB transcripts using
`sail runtime execute --file query.json`. Read [SMT requests](references/smt.md)
for a complete request and the equivalent MCP tools.

Sail returns stored output when the transcript and execution settings match a
cached decided run. Changed formulas are solved again. Read the satisfiability
answer and requested model or unsat core; solver installation readiness alone
is not a result about the formula.

## Read the evidence

For Verus results, check scope and currentness before reporting success. Current
evidence matches the present inputs; Historical evidence no longer matches
them; Unknown does not establish a current proof. Current describes freshness,
not success: read the verdict too. Verify again after
further edits. An SMT answer concerns its submitted formula; Verus checks
whether the Rust implementation meets its contracts.

Keep transcripts, logs and redirected output outside the project's watched
inputs during verification. Writing them inside those inputs can invalidate
freshness.

If Sail is missing, use the [installation guide](https://github.com/Chelis-Lang/sail/blob/main/docs/install.md).
Sail ships its own Verus and Z3; an existing Verus installation is left alone.
For a missing runtime, check `sail engine status` and the installation guide.
Use [compatibility](https://github.com/Chelis-Lang/sail/blob/main/docs/compatibility.md)
to check the pinned release. Use `cargo verus verify` if a project must keep
a different Verus release.
