import { defineHook, sleep } from "workflow";
import { z } from "zod";
import { getActualRunCostUsd, getRunReceipt, recordWorkflowProgressAndStatus } from "./steps";

export const approvalDecision = z.object({ approved: z.boolean(), comment: z.string().nullable().default(null) });
export const approvalHook = defineHook({ schema: approvalDecision });
export const cancellationHook = defineHook({ schema: z.object({ reason: z.string().nullable().default(null) }) });
export type WorkflowMeta = { runKey: string; slug: string; checkpoint: number | null; scheduledFor?: string | null; rowKey?: string; step?: string; maxSpendUsd?: number; concurrency?: number };
export type ApprovalResult = { approved: boolean; comment: string | null; outcome: "approved" | "denied" | "timed_out" };

export async function approve(input: { stage: string; summary: string; meta: WorkflowMeta; timeoutMs?: number }): Promise<ApprovalResult> {
  if (input.stage.includes(".")) throw new Error("Approval stage names cannot contain dots.");
  const token = approvalToken(input.meta, input.stage), pending = approvalHook.create({ token });
  const approval = { stage: input.stage, token, summary: input.summary };
  await recordWorkflowProgressAndStatus(input.meta.runKey, { status: "waiting", approval });
  const winner = await Promise.race([pending.then((payload) => ({ kind: "hook" as const, payload })), sleep(input.timeoutMs ?? 604_800_000).then(() => ({ kind: "timeout" as const }))]);
  await pending.dispose();
  const payload = winner.kind === "hook" ? winner.payload : { approved: false, comment: "timeout" };
  const outcome = winner.kind === "timeout" ? "timed_out" : payload.approved ? "approved" : "denied";
  await recordWorkflowProgressAndStatus(input.meta.runKey, { status: outcome === "approved" ? "running" : outcome === "timed_out" ? "timed_out" : "stopped", stop_reason: outcome === "approved" ? null : outcome === "timed_out" ? "approval_timeout" : "operator_denied", approval: { ...approval, ...payload }, resolved: true });
  return { ...payload, outcome };
}

export async function checkpoint(meta: WorkflowMeta, state: { completed: number; failed: number; spentUsd: number; projectedSpentUsd: number; projectedRemainingUsd: number; table: string; concurrency?: number }): Promise<ApprovalResult> {
  if (meta.checkpoint === null) return { approved: true, comment: null, outcome: "approved" };
  const spentUsd = await getActualRunCostUsd(meta.runKey), receipt = await getRunReceipt(meta.runKey), done = state.completed + state.failed;
  await recordWorkflowProgressAndStatus(meta.runKey, { completed: state.completed, failed: state.failed, cost_usd: spentUsd, checkpoint: meta.checkpoint });
  return approve({ stage: "checkpoint", meta, summary: `${done} rows done, ${state.failed} failed; actual $${spentUsd.toFixed(2)}; up to $${state.projectedRemainingUsd.toFixed(2)} remains; ${receipt.cacheHits} cache hits; open ${state.table} in Data.` });
}

export function approvalToken(meta: WorkflowMeta, stage: string) { return `${meta.slug}.${meta.runKey}.${stage}`; }
export function cancellationToken(meta: WorkflowMeta) { return `${meta.slug}.${meta.runKey}.cancel`; }
