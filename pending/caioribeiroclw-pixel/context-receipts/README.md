# Pluribus context-receipts Agent Skill

Privacy-safe receipts for agent context boundaries: MCP Tool Search / dynamic discovery, runtime tool-surface diffs, GraphRAG or memory retrieval that may be ignored, skill/rule injection, subagent delegation, and related handoffs.

This skill is intentionally evidence-focused, not a memory layer, RAG system, MCP gateway, or tracing backend. It asks an agent to emit low-cardinality receipt fields so reviewers can answer:

> what crossed the context boundary, what stayed out, and what audit gap remains?

## Source

Canonical upstream directory:

https://github.com/caioribeiroclw-pixel/pluribus/tree/main/skills/context-receipts

Runnable public examples:

- Browser playground: https://caioribeiroclw-pixel.github.io/pluribus/receipt-playground.html
- Tool-surface diff demo: `npx --yes pluribus-context@latest demo tool-surface-diff --json`
- Context attention receipts: https://github.com/caioribeiroclw-pixel/pluribus/tree/main/examples/context-attention-receipts

## Security / privacy notes

- Pure Markdown skill: no scripts, no hooks, no network calls, no credential reads, no auto-update.
- Receipts should not include raw prompts, raw tool schemas, raw tool arguments, raw tool results, raw skill bodies, customer text, secrets, or full transcripts.
- Prefer ids, hashes, counts, token/line buckets, categorical reasons, and explicit privacy booleans.

## License

MIT, same as Pluribus.
