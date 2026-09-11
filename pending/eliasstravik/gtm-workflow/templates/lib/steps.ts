import { and, eq, or, sql } from "drizzle-orm";
import { getWorkflowMetadata } from "workflow";
import { getDb, getRunRow, getRunLedgerSummary, runLedgerCondition, updateRunPlain } from "./db";
import { redact, redactValue } from "./redact";
import { enrichmentRuns, type WorkflowStatus } from "./schema";

export type ApprovalState = {
  stage: string;
  token: string;
  summary: string;
  approved?: boolean;
  comment?: string | null;
  resolved_at?: number;
};

export type RunPatch = {
  status?: WorkflowStatus;
  run_id?: string | null;
  completed?: number | null;
  failed?: number | null;
  cost_usd?: number | null;
  checkpoint?: number | null;
  webhook_url?: string | null;
  trigger_token?: string | null;
  approval?: ApprovalState | null;
  error?: string | null;
  stop_reason?: string | null;
  remaining_keys?: string[] | null;
  failed_step?: string | null;
  run_url?: string | null;
  finished?: boolean;
  resolved?: boolean;
};

export async function registerWorkflowRun(runKey: string): Promise<void> {
  "use step";
  const metadata = getWorkflowMetadata();
  await updateRunPlain(runKey, {
    runId: metadata.workflowRunId,
    runUrl: metadata.url,
  });
}

export async function recordWorkflowProgressAndStatus(
  runKey: string,
  patch: RunPatch,
): Promise<void> {
  "use step";
  const now = Date.now();
  const metadata = getWorkflowMetadata();
  const current = await getRunRow(runKey);
  if (current?.cancelRequestedAt !== null && current?.cancelRequestedAt !== undefined && patch.finished) {
    patch = { ...patch, status: "cancelling", stop_reason: current.stopReason, finished: false };
  }
  const safeApproval = patch.approval
    ? (redactValue(patch.approval) as ApprovalState)
    : patch.approval;
  const approval =
    safeApproval && patch.resolved
      ? { ...safeApproval, resolved_at: now }
      : safeApproval;
  const actualCostUsd =
    patch.cost_usd !== undefined || patch.finished
      ? await getActualRunCostUsd(runKey)
      : undefined;
  await updateRunPlain(runKey, {
    runId: patch.run_id === undefined ? metadata.workflowRunId : patch.run_id,
    runUrl: patch.run_url === undefined ? metadata.url : patch.run_url,
    ...(patch.status !== undefined ? { status: patch.status } : {}),
    ...(patch.completed !== undefined ? { completed: patch.completed } : {}),
    ...(patch.failed !== undefined ? { failed: patch.failed } : {}),
    ...(actualCostUsd !== undefined ? { costUsd: actualCostUsd } : {}),
    ...(patch.checkpoint !== undefined ? { checkpoint: patch.checkpoint } : {}),
    ...(patch.webhook_url !== undefined ? { webhookUrl: patch.webhook_url } : {}),
    ...(patch.trigger_token !== undefined ? { triggerToken: patch.trigger_token } : {}),
    ...(approval !== undefined
      ? { approval: approval === null ? null : JSON.stringify(approval) }
      : {}),
    ...(patch.error !== undefined
      ? { error: patch.error === null ? null : redact(patch.error) }
      : {}),
    ...(patch.stop_reason !== undefined ? { stopReason: patch.stop_reason } : {}),
    ...(patch.remaining_keys !== undefined
      ? {
          remainingKeys:
            patch.remaining_keys === null ? null : JSON.stringify(patch.remaining_keys),
        }
      : {}),
    ...(patch.failed_step !== undefined ? { failedStep: patch.failed_step } : {}),
    ...(patch.finished ? { finishedAt: now } : {}),
  });
}

export const updateRun = recordWorkflowProgressAndStatus;

/** Record a completed row before cancellation can discard workflow memory. */
export async function recordCompletedRow(runKey: string, key: string): Promise<void> {
  "use step";
  const db = await getDb();
  await db.run(sql`UPDATE workflow_runs SET completed = coalesce(completed, 0) + 1,
    remaining_keys = (SELECT json_group_array(value) FROM json_each(workflow_runs.remaining_keys) WHERE value <> ${key})
    WHERE run_key = ${runKey} AND EXISTS (SELECT 1 FROM json_each(workflow_runs.remaining_keys) WHERE value = ${key})`);
}

export async function getActualRunCostUsd(runKey: string): Promise<number> {
  "use step";
  const db = await getDb();
  const row = (
    await db
      .select({
        costUsd: sql<number>`coalesce(sum(${enrichmentRuns.costUsd}), 0)`,
      })
      .from(enrichmentRuns)
      .where(runLedgerCondition(runKey))
  )[0];
  return Number(row?.costUsd ?? 0);
}

export async function getRunReceipt(runKey: string) {
  "use step";
  return getRunLedgerSummary(runKey);
}

export async function getHeldRunReason(
  runKey: string,
): Promise<"provider_auth" | "provider_quota" | undefined> {
  "use step";
  const db = await getDb();
  const row = (
    await db
      .select({ errorKind: enrichmentRuns.errorKind })
      .from(enrichmentRuns)
      .where(
        and(
          eq(enrichmentRuns.runKey, runKey),
          or(
            eq(enrichmentRuns.errorKind, "provider_auth"),
            eq(enrichmentRuns.errorKind, "provider_quota"),
          ),
        ),
      )
      .limit(1)
  )[0];
  return row?.errorKind === "provider_auth" || row?.errorKind === "provider_quota"
    ? row.errorKind
    : undefined;
}
