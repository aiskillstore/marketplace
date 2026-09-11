import { sql } from "drizzle-orm";
import {
  index,
  integer,
  primaryKey,
  real,
  sqliteTable,
  text,
  uniqueIndex,
} from "drizzle-orm/sqlite-core";

export type EnrichmentStatus =
  | "pending"
  | "cache_hit"
  | "success"
  | "empty"
  | "error"
  | "lost";
export type CostSource = "reported" | "fixed" | "projected";
export type EnrichmentErrorKind =
  | "pre_call"
  | "call"
  | "cache_parse"
  | "provider_auth"
  | "provider_quota"
  | "lost";
export type WorkflowStatus =
  | "running"
  | "waiting"
  | "cancelling"
  | "completed"
  | "stopped"
  | "timed_out"
  | "failed"
  | "cancelled";

export const enrichmentCache = sqliteTable(
  "enrichment_cache",
  {
    provider: text("provider").notNull(),
    endpoint: text("endpoint").notNull(),
    inputsHash: text("inputs_hash").notNull(),
    inputs: text("inputs").notNull(),
    raw: text("raw"),
    value: text("value").notNull(),
    expiresAt: integer("expires_at").notNull(),
    createdAt: integer("created_at").notNull(),
  },
  (table) => [
    primaryKey({ columns: [table.provider, table.endpoint, table.inputsHash] }),
  ],
);

export const enrichmentRuns = sqliteTable(
  "enrichment_runs",
  {
    id: text("id").primaryKey(),
    runKey: text("run_key").notNull(),
    workflow: text("workflow").notNull(),
    rowKey: text("row_key"),
    step: text("step"),
    provider: text("provider").notNull(),
    endpoint: text("endpoint").notNull(),
    inputsHash: text("inputs_hash").notNull(),
    status: text("status").$type<EnrichmentStatus>().notNull(),
    costUsd: real("cost_usd"),
    costSource: text("cost_source").$type<CostSource>().notNull().default("fixed"),
    error: text("error"),
    errorKind: text("error_kind").$type<EnrichmentErrorKind>(),
    createdAt: integer("created_at").notNull(),
  },
  (table) => [index("enrichment_runs_run_key_idx").on(table.runKey)],
);

export const workflowRuns = sqliteTable(
  "workflow_runs",
  {
    runKey: text("run_key").primaryKey(),
    runId: text("run_id").unique(),
    parentRunKey: text("parent_run_key"),
    workspaceHead: text("workspace_head"),
    workflow: text("workflow").notNull(),
    path: text("path").notNull(),
    method: text("method").$type<"GET" | "POST">().notNull(),
    input: text("input").notNull(),
    inputHash: text("input_hash").notNull(),
    status: text("status").$type<WorkflowStatus>().notNull(),
    error: text("error"),
    stopReason: text("stop_reason"),
    remainingKeys: text("remaining_keys"),
    failedStep: text("failed_step"),
    runUrl: text("run_url"),
    completed: integer("completed"),
    failed: integer("failed"),
    costUsd: real("cost_usd"),
    checkpoint: integer("checkpoint"),
    webhookUrl: text("webhook_url"),
    triggerToken: text("trigger_token"),
    approval: text("approval"),
    scheduledFor: text("scheduled_for"),
    cancelRequestedAt: integer("cancel_requested_at"),
    startedAt: integer("started_at").notNull(),
    finishedAt: integer("finished_at"),
  },
  (table) => [
    index("workflow_runs_parent_idx").on(table.parentRunKey),
    uniqueIndex("workflow_runs_live_idx")
      .on(table.path, table.inputHash)
      .where(sql`finished_at IS NULL`),
    uniqueIndex("workflow_runs_scheduled_idx")
      .on(table.path, table.scheduledFor)
      .where(sql`scheduled_for IS NOT NULL`),
  ],
);

export type WorkflowRunRow = typeof workflowRuns.$inferSelect;
export type WorkflowRunInsert = typeof workflowRuns.$inferInsert;
