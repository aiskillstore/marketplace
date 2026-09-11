import { createHash } from "node:crypto";
import { eq, sql } from "drizzle-orm";
import { getDb } from "./db";
import { redact } from "./redact";
import { enrichmentRuns } from "./schema";
import type { PaidCallMeta } from "./provider";

export type SpendCall = { meta: PaidCallMeta; operation: string; provider: string; endpoint: string; estimateUsd: number; maxSpendUsd: number; maxCalls?: number };

export async function reserveSpend(call: SpendCall): Promise<string> {
  "use step";
  if (process.env.GTM_SANDBOX === "1") throw new Error("The authoring sandbox cannot run a workflow.");
  if (![call.estimateUsd, call.maxSpendUsd].every((value) => Number.isFinite(value) && value >= 0)) throw new Error("Invalid spending limit.");
  const id = createHash("sha256").update(JSON.stringify([call.meta.runKey, call.meta.rowKey ?? null, call.meta.step, call.operation])).digest("hex");
  const db = await getDb();
  const rows = await db.all(sql`
    INSERT INTO enrichment_runs (id,run_key,workflow,row_key,step,provider,endpoint,inputs_hash,status,cost_usd,cost_source,created_at)
    SELECT ${id},${call.meta.runKey},${call.meta.slug},${call.meta.rowKey ?? null},${call.meta.step ?? null},${call.provider},${call.endpoint},${id},'pending',${call.estimateUsd},'projected',${Date.now()}
    WHERE NOT EXISTS (SELECT 1 FROM workflow_runs WHERE run_key=${call.meta.runKey} AND (cancel_requested_at IS NOT NULL OR finished_at IS NOT NULL))
      AND (SELECT coalesce(sum(cost_usd),0) FROM enrichment_runs WHERE run_key=${call.meta.runKey}) + ${call.estimateUsd} <= ${call.maxSpendUsd}
      AND (SELECT count(*) FROM enrichment_runs WHERE run_key=${call.meta.runKey} AND row_key IS ${call.meta.rowKey ?? null} AND step IS ${call.meta.step ?? null} AND endpoint=${call.endpoint}) < ${call.maxCalls ?? 1}
    ON CONFLICT(id) DO NOTHING RETURNING id`);
  if (rows.length !== 1) throw new Error("[spend_cap] This call exceeds the accepted budget or has already started.");
  return id;
}

export async function settleSpend(id: string, costUsd?: number, error?: unknown): Promise<void> {
  "use step";
  if (costUsd !== undefined && (!Number.isFinite(costUsd) || costUsd < 0)) throw new Error("Invalid reported cost; reservation retained.");
  await (await getDb()).update(enrichmentRuns).set({ status: error ? "error" : "success", ...(costUsd === undefined ? {} : { costUsd, costSource: "reported" as const }), ...(error ? { errorKind: "call" as const, error: redact(error) } : {}) }).where(eq(enrichmentRuns.id, id));
}

export async function withSpend<T extends { costUsd?: number }>(meta: PaidCallMeta, options: { step: string; estimateUsd: number }, fn: () => Promise<T>): Promise<T> {
  const scoped = { ...meta, step: options.step };
  const id = await reserveSpend({ meta: scoped, operation: options.step, provider: "agent-stage", endpoint: options.step, estimateUsd: options.estimateUsd, maxSpendUsd: meta.maxSpendUsd ?? options.estimateUsd });
  try { const value = await fn(); await settleSpend(id, value.costUsd); return value; }
  catch (error) { await settleSpend(id, undefined, error); throw error; }
}

reserveSpend.maxRetries = 0;
settleSpend.maxRetries = 0;
