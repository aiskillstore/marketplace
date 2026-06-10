# Context receipts Agent Skill recipe

This is a small, copyable Agent Skill recipe for context-engineering users who are adopting Tool Search, lazy MCP loading, dynamic tool discovery, skills, memory, compaction, GraphRAG/code search, transcript review, or subagents and need to verify what actually crossed the context boundary.

It is intentionally markdown-only so it can be copied into a local skills directory such as:

- `.claude/skills/context-receipts/SKILL.md`
- `.opencode/skills/context-receipts/SKILL.md`
- `.agents/skills/context-receipts/SKILL.md`

The two newest smoke paths are:

- **Runtime tool-surface diff:** prove which MCP tools were discovered, activated, withheld, or blocked without copying raw schemas/prompts/results.
- **Context attention:** prove that retrieved/baseline context was delivered, acknowledged before planning, and cited before edits/tool calls.

## Quick smoke

Ask an agent or harness using the skill to emit a receipt for one workflow and verify these constraints:

```bash
grep -E 'mcp\.tool_index\.loaded|context\.skill\.registry\.index\.loaded|subagent\.mcp_policy\.applied|subagent\.toolsearch\.propagation\.evaluated|context\.prune\.completed|context\.compaction\.rollback\.completed|subagent\.delegation\.requested' receipt.jsonl
grep -E 'raw_(schema|query|args|result|output|transcript|text)_copied":false|raw.*CopiedToReceipt":false' receipt.jsonl
```

Then manually check that the receipt contains counts, hashes, ids, buckets, and `audit_gap`, but does **not** contain private prompts, raw schemas, tool args/results, skill bodies, memory bodies, customer names, secrets, or transcript text.

For executable fixture examples, see:

- [`../../examples/tool-surface-diff-receipts/`](../../examples/tool-surface-diff-receipts/) for runtime MCP tool-surface diff receipts.
- [`../../examples/context-attention-receipts/`](../../examples/context-attention-receipts/) for retrieved-context attention receipts.
- [`../../examples/context-input-evidence/`](../../examples/context-input-evidence/) for ToolSearch propagation, pruning, and compaction transaction smokes.

```bash
node ../../examples/context-attention-receipts/check-attention-receipt.mjs \
  ../../examples/context-attention-receipts/attention-receipt-pass.json
node ../../examples/context-input-evidence/convert-subagent-toolsearch-propagation-log.mjs
node ../../examples/context-input-evidence/convert-pruning-log.mjs
node ../../examples/context-input-evidence/convert-compaction-transaction-log.mjs
```
