# Workflow library

The template adds these chosen conventions to Vercel Workflow:

- `runRows({ rows, meta, table: { name, save }, rowStep, caps: { maxRows, maxSpendUsd, costPerRowUsd } })` handles caps, row progress, cancellation, and optional checkpoints. `rowStep` returns `{ key, value }` to save or `{ key, status: "empty" }` to skip; a thrown error fails that row and its plain message is kept on the run.
- `provider()` wraps a fixed paid call with caching and a ledger entry. Every `"use step"` function that makes a paid call sets `fn.maxRetries = 0` so a failure is not billed again.
- `agent()` produces one structured model response. A Gateway credential wins; otherwise `GTM_HOST` selects Claude Code or Codex exactly.
- `agentStage()` lets the model choose among a declared list of HTTP MCP servers for several turns. Through the Gateway it is a `WorkflowAgent` and each MCP call is a durable step. Locally without a key, Claude Code runs it as one headless call with a budget cap and only those MCP tools; Codex cannot cap spend and refuses.
- `withSpend(meta, { step, estimateUsd }, fn)` atomically reserves and settles a paid operation against the run cap. Every paid helper receives an explicit enclosing function name as `step`; only those Diagram nodes light up.
- Every result table declares `key` and `updatedAt` (`updated_at`). `npm run db:generate` writes committed SQL and regenerates the bundled migration module. Nitro applies every pending migration at startup.
- The workflow file starts with an author-written `Diagram:` block. Numbered nodes run in order unless a line uses `-> N`. Paid nodes need `[cost: $X/row]`; `agentStage()` needs `[cost: up to $X/row]`; schedules need `[schedule: cron]` and a matching `vercel.json` entry.
- `gtm` provides `run`, `runs get`, `query`, `check`, `verify`, `diagram`, `approve`, `cancel`, `upgrade`, and `help`. `run --background` returns at once and starts the run detached after `--wait-live`; `GET /api/runs/latest?workflow=<slug>&head=<sha>` finds it. A local `gtm run` starts the server on a free loopback port and writes a `GTM_RUN_SECRET` into `.env` the first time. The web diagram response includes Diagram, image, Runs, and Data links.
- Workflow files live at `workflows/workflows/<slug>.ts`, tables at `workflows/db/tables/<name>.ts`, and the test input at `workflows/data/test-1-row.json` (ignored by git).

```ts
/**
 * Diagram:
 *   1. Read the company list       [step: parseInput]
 *   2. Research each company       [step: researchCompany] [cost: up to $0.10/row]
 *   3. Save to account_scores      [step: saveRow]
 */
import { z } from "zod";
import { agentStage } from "../lib/agent-stage";
import type { WorkflowMeta } from "../lib/approve";
import { upsertRows } from "../lib/db";
import { runRows } from "../lib/rows";
import { accountScores } from "../db/tables/account-scores";

export const input = z.object({ rows: z.array(z.object({ key: z.string() })) });
type Input = z.infer<typeof input>;
export const MAX_ROWS = 100;
export const MAX_SPEND_USD = 10;
export const COST_PER_ROW_USD = 0.1;

const result = z.object({ score: z.number(), reason: z.string() });

/** Read the company list */
async function parseInput(value: unknown) {
  "use step";
  return input.parse(value);
}
parseInput.maxRetries = 0;

/** Research each company */
async function researchCompany(row: Input["rows"][number], meta: WorkflowMeta, signal: AbortSignal) {
  const value = await agentStage({
    step: "researchCompany",
    instructions: "Research the company and return a score with a one-line reason.",
    input: row,
    schema: result,
    tools: [{ name: "company-data", url: "https://example.com/mcp", headers: { Authorization: "COMPANY_DATA_TOKEN" } }],
    maxUsd: COST_PER_ROW_USD,
    maxTurns: 4,
    deadlineMs: 120_000,
    meta,
    signal,
  });
  return { key: row.key, value };
}

/** Save to account_scores */
async function saveRow(row: Record<string, unknown>) {
  "use step";
  await upsertRows(accountScores, [{ ...row, updatedAt: Date.now() }]);
}

export async function accountScoring(raw: unknown, meta: WorkflowMeta) {
  "use workflow";
  const value = await parseInput(raw);
  return runRows({
    rows: value.rows,
    meta,
    table: { name: "account_scores", save: saveRow },
    rowStep: researchCompany,
    caps: { maxRows: MAX_ROWS, maxSpendUsd: MAX_SPEND_USD, costPerRowUsd: COST_PER_ROW_USD },
  });
}
```
