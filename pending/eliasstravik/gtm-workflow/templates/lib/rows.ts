import {
  cancellationHook,
  cancellationToken,
  checkpoint,
  type WorkflowMeta,
} from "./approve";
import { setAttributes } from "workflow";
import { redact } from "./redact";
import {
  getActualRunCostUsd,
  getHeldRunReason,
  registerWorkflowRun,
  recordCompletedRow,
  updateRun,
} from "./steps";

function stageLabel(name: string): string {
  const words = name.replace(/([a-z0-9])([A-Z])/g, "$1 $2").replace(/[_-]+/g, " ").toLowerCase();
  return words.charAt(0).toUpperCase() + words.slice(1);
}

export const MAX_ROW_CONCURRENCY = 16;

export type RowStepResult =
  | { key: string; status?: "success"; value: Record<string, unknown> }
  | { key: string; status: "empty"; value?: undefined };

export type RunRowsTable = {
  name: string;
  save: (row: Record<string, unknown>) => Promise<void>;
};

export type RunRowsCaps = {
  maxRows: number;
  maxSpendUsd: number;
  costPerRowUsd: number;
};

export async function runRows<TRow extends { key: string }>(input: {
  rows: TRow[];
  meta: WorkflowMeta;
  table: RunRowsTable;
  rowStep: (
    row: TRow,
    meta: WorkflowMeta,
    signal: AbortSignal,
  ) => Promise<RowStepResult>;
  /** Runs in workflow context after persistence, before checkpoint and terminal state. */
  afterSave?: (row: TRow, meta: WorkflowMeta, signal: AbortSignal) => Promise<void>;
  caps: RunRowsCaps;
  /** Bounded width; checkpoints round up to the end of a batch. */
  concurrency?: number;
}) {
  const concurrency = input.concurrency ?? 1;
  if (!Number.isSafeInteger(concurrency) || concurrency < 1 || concurrency > MAX_ROW_CONCURRENCY) {
    throw new Error(`Row concurrency must be an integer from 1 to ${MAX_ROW_CONCURRENCY}`);
  }
  input = { ...input, caps: { ...input.caps,
    maxSpendUsd: Math.min(input.caps.maxSpendUsd, input.meta.maxSpendUsd ?? input.caps.maxSpendUsd),
  } };
  if (!Number.isSafeInteger(input.caps.maxRows) || input.caps.maxRows < 0 ||
      !Number.isFinite(input.caps.maxSpendUsd) || input.caps.maxSpendUsd < 0 ||
      !Number.isFinite(input.caps.costPerRowUsd) || input.caps.costPerRowUsd < 0) throw new Error("Invalid row spending limits");
  await registerWorkflowRun(input.meta.runKey);
  const projected = input.rows.length * input.caps.costPerRowUsd;
  if (
    input.rows.length > input.caps.maxRows ||
    projected > input.caps.maxSpendUsd
  ) {
    await updateRun(input.meta.runKey, {
      status: "failed",
      error: "accepted workflow limits exceeded",
      stop_reason: "caps_exceeded",
      completed: 0,
      failed: 0,
      finished: true,
    });
    throw new Error("Accepted workflow limits exceeded");
  }

  const completed: string[] = [];
  if (new Set(input.rows.map((row) => row.key)).size !== input.rows.length) throw new Error("Rows require unique keys");
  await updateRun(input.meta.runKey, { completed: 0, failed: 0, remaining_keys: input.rows.map((row) => row.key) });
  const failed: { key: string; error: string }[] = [];
  let success = 0;
  let empty = 0;
  let status: "completed" | "stopped" | "timed_out" | "cancelling" = "completed";
  let stopReason: string | null = null;
  let remainingKeys: string[] = [];
  let failedStep: string | null = null;
  let checkpointTaken = false;

  const controller = new AbortController();
  const cancel = cancellationHook.create({ token: cancellationToken(input.meta) });
  const cancelled = cancel.then(({ reason }) => {
    controller.abort(reason ?? "run cancelled");
    return { cancelled: true as const };
  });

  try {
    for (let index = 0; index < input.rows.length; index += concurrency) {
      const batch = input.rows.slice(index, index + concurrency);
      if (concurrency > 1) await setAttributes({ stage: `${stageLabel(input.rowStep.name || "rowStep")} (${concurrency} rows at a time)` });
      const outcomes = await Promise.allSettled(batch.map(async (row) => {
        const rowMeta = {
          ...input.meta,
          maxSpendUsd: input.caps.maxSpendUsd,
          rowKey: row.key,
          step: input.rowStep.name || "rowStep",
          concurrency,
        };
        if (concurrency === 1) await setAttributes({ stage: stageLabel(input.rowStep.name || "rowStep"), row: row.key });
        if (controller.signal.aborted) return { cancelled: true as const };
        const outcome = await Promise.race([
          input.rowStep(row, rowMeta, controller.signal).then((value) => ({
            cancelled: false as const,
            value,
          })),
          cancelled,
        ]);
        if (!("value" in outcome) || controller.signal.aborted) return { cancelled: true as const };
        if (outcome.value.status === "empty") {
          await recordCompletedRow(input.meta.runKey, row.key);
          return { key: outcome.value.key, empty: true };
        } else {
          if (concurrency === 1) await setAttributes({ stage: stageLabel(input.table.save.name || "save"), row: row.key });
          await input.table.save({ key: outcome.value.key, ...outcome.value.value });
          if (controller.signal.aborted) return { cancelled: true as const };
          if (input.afterSave) {
            if (concurrency === 1) await setAttributes({ stage: stageLabel(input.afterSave.name || "afterSave"), row: row.key });
            await input.afterSave(row, rowMeta, controller.signal);
          }
          await recordCompletedRow(input.meta.runKey, row.key);
          return { key: outcome.value.key, empty: false };
        }
      }));
      // Fold in input order after every sibling settles; completion order changes no counts.
      let held: "provider_auth" | "provider_quota" | "spend_cap" | undefined;
      const unfinished: string[] = [];
      for (let offset = 0; offset < outcomes.length; offset++) {
        const outcome = outcomes[offset];
        const row = batch[offset];
        if (outcome.status === "fulfilled" && "key" in outcome.value && typeof outcome.value.key === "string") {
          completed.push(outcome.value.key);
          if (outcome.value.empty) empty++;
          else success++;
        } else if (controller.signal.aborted || outcome.status === "fulfilled") {
          unfinished.push(row.key);
        } else {
          held ??= heldReason(outcome.reason);
          if (heldReason(outcome.reason) === "spend_cap") { unfinished.push(row.key); continue; }
          failed.push({ key: row.key, error: plainReason(redact(outcome.reason)) });
          failedStep = input.rowStep.name || "rowStep";
        }
      }
      const nextKeys = input.rows.slice(index + batch.length).map(({ key }) => key);
      await updateRun(input.meta.runKey, { completed: completed.length, failed: failed.length,
        remaining_keys: [...unfinished, ...nextKeys] });
      if (controller.signal.aborted) {
        status = "cancelling";
        stopReason = "cancelled";
        remainingKeys = [...unfinished, ...nextKeys];
        break;
      }
      if (outcomes.some((outcome) => outcome.status === "rejected")) held ??= await getHeldRunReason(input.meta.runKey);
      if (held) {
        status = "stopped";
        stopReason = held;
        remainingKeys = [...unfinished, ...nextKeys];
        break;
      }
      const spentUsd = await getActualRunCostUsd(input.meta.runKey);
      if (spentUsd > input.caps.maxSpendUsd || (concurrency > 1 && nextKeys.length > 0 && input.caps.costPerRowUsd > 0 && spentUsd >= input.caps.maxSpendUsd)) {
        status = "stopped";
        stopReason = "spend_cap";
        remainingKeys = nextKeys;
        break;
      }

      const processed = completed.length + failed.length;
      if (!checkpointTaken && input.meta.checkpoint !== null && processed >= input.meta.checkpoint) {
        checkpointTaken = true;
        const decision = await checkpoint(input.meta, {
          completed: completed.length,
          failed: failed.length,
          spentUsd,
          projectedSpentUsd: processed * input.caps.costPerRowUsd,
          projectedRemainingUsd:
            (input.rows.length - processed) * input.caps.costPerRowUsd,
          table: input.table.name,
          concurrency,
        });
        if (!decision.approved) {
          status = decision.outcome === "timed_out" ? "timed_out" : "stopped";
          stopReason =
            decision.outcome === "timed_out"
              ? "approval_timeout"
              : "operator_denied";
          remainingKeys = nextKeys;
          break;
        }
      }
    }
  } finally {
    await cancel.dispose();
  }

  await updateRun(input.meta.runKey, {
    status: status === "completed" && failed.length > 0 ? "failed" : status,
    completed: completed.length,
    failed: failed.length,
    cost_usd: await getActualRunCostUsd(input.meta.runKey),
    stop_reason: stopReason,
    remaining_keys: remainingKeys,
    failed_step: failedStep,
    ...(failed.length ? { error: failed.length === 1 ? failed[0].error : `${failed.length} rows failed. First: ${failed[0].error}` } : {}),
    finished: status !== "cancelling",
  });
  return {
    status: status === "completed" && failed.length > 0 ? "failed" : status,
    concurrency,
    completed,
    failed,
    counts: { success, empty, failed: failed.length },
    stopReason,
    remainingKeys,
  };
}

/** Drop the runtime's retry wrapper so the run keeps only the sentence a person can act on. */
function plainReason(message: string): string {
  return message.replace(/^Step "[^"]*" failed after \d+ retr(?:y|ies): /, "").trim();
}

function heldReason(error: unknown): "provider_auth" | "provider_quota" | "spend_cap" | undefined {
  if (!error || typeof error !== "object") return undefined;
  const value = error as { providerErrorKind?: unknown; name?: unknown; message?: unknown };
  // The SDK wraps a step's message with its name and retry count.
  if (typeof value.message === "string" && /(?:^|:\s)\[spend_cap\]/.test(value.message)) return "spend_cap";
  if (
    value.providerErrorKind === "provider_auth" ||
    value.name === "ProviderAuthError" ||
    (typeof value.message === "string" && value.message.startsWith("[provider_auth]"))
  ) {
    return "provider_auth";
  }
  if (
    value.providerErrorKind === "provider_quota" ||
    value.name === "ProviderQuotaError" ||
    (typeof value.message === "string" && value.message.startsWith("[provider_quota]"))
  ) {
    return "provider_quota";
  }
  return undefined;
}
