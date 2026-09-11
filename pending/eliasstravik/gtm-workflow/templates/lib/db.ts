import { createClient as createWebClient, type Client } from "@libsql/client/web";
import { and, desc, eq, getTableColumns, or, sql } from "drizzle-orm";
import type { LibSQLDatabase } from "drizzle-orm/libsql/driver-core";
import { drizzle as drizzleWeb } from "drizzle-orm/libsql/web";
import { getRun } from "workflow/api";
import { HookNotFoundError, WorkflowRunFailedError } from "workflow/errors";
import { getDatabaseConfig } from "./db-url";
import { redact } from "./redact";
import { enrichmentRuns, workflowRuns, type WorkflowRunInsert, type WorkflowRunRow, type WorkflowStatus } from "./schema";
import * as schema from "./schema";

type Database = LibSQLDatabase<typeof schema>;
type Runtime = { client: Client; database: Database };
const importLocal = new Function("specifier", "return import(specifier)") as <T>(specifier: string) => Promise<T>;
let runtimePromise: Promise<Runtime> | undefined;
let migrationPromise: Promise<void> | undefined;
let migrationStatus = "pending";

async function getRuntime(): Promise<Runtime> {
  runtimePromise ??= (async () => {
    const config = getDatabaseConfig();
    if (config.dialect === "sqlite") {
      const [{ createClient }, { drizzle }] = await Promise.all([importLocal<typeof import("@libsql/client")>("@libsql/client"), importLocal<typeof import("drizzle-orm/libsql")>("drizzle-orm/libsql")]);
      const client = createClient({ url: config.url });
      // busy_timeout first: a second process opening the same fresh file must wait, not fail, while the first sets WAL.
      await client.execute("PRAGMA busy_timeout=5000");
      for (let attempt = 0; ; attempt += 1) {
        try { await client.execute("PRAGMA journal_mode=WAL"); break; }
        catch (error) { if (attempt >= 20 || !/SQLITE_BUSY|database is locked/i.test(String(error))) throw error; await new Promise((resolve) => setTimeout(resolve, 100 + Math.floor(Math.random() * 200))); }
      }
      return { client, database: drizzle(client, { schema }) as Database };
    }
    const client = createWebClient({ url: config.url, authToken: config.authToken });
    return { client, database: drizzleWeb(client, { schema }) };
  })();
  runtimePromise.catch(() => { runtimePromise = undefined; });
  return runtimePromise;
}

export function getMigrationStatus() { return migrationStatus; }

async function readApplied(client: Client): Promise<Set<string>> {
  return new Set((await client.execute("SELECT hash FROM __drizzle_migrations")).rows.map((row) => String(row.hash)));
}

const RETRYABLE = /SQLITE_BUSY|database is locked|already exists|duplicate column/i;

/**
 * Apply every committed migration that the ledger does not list yet. Several
 * server instances may boot at once, so a locked database or a migration that
 * another instance just applied is retried with a short pause, not treated as
 * a failure. Only a migration that is still pending after the retries fails.
 */
export async function ensureMigrated(): Promise<void> {
  migrationPromise ??= (async () => {
    try {
      const { client } = await getRuntime();
      const { migrations } = await import("./migrations.generated");
      for (let attempt = 0; ; attempt += 1) {
        try { await client.execute("CREATE TABLE IF NOT EXISTS __drizzle_migrations (id INTEGER PRIMARY KEY AUTOINCREMENT, hash TEXT NOT NULL, created_at INTEGER)"); break; }
        catch (error) { if (attempt >= 20 || !RETRYABLE.test(String(error))) throw error; await pause(); }
      }
      let applied = await readApplied(client);
      for (const migration of migrations) {
        if (applied.has(migration.hash)) continue;
        let last: unknown;
        for (let attempt = 0; attempt < 30; attempt += 1) {
          try {
            const tx = await client.transaction("write");
            try {
              for (const statement of migration.sql.split("--> statement-breakpoint").map((item) => item.trim()).filter(Boolean)) await tx.execute(statement);
              await tx.execute({ sql: "INSERT INTO __drizzle_migrations(hash, created_at) VALUES (?, ?)", args: [migration.hash, migration.createdAt] });
              await tx.commit();
            } catch (error) { await tx.rollback().catch(() => undefined); throw error; }
            last = undefined;
            console.log(`Applied migration ${migration.tag}.`);
            break;
          } catch (error) {
            last = error;
            if (!RETRYABLE.test(String(error))) break;
            await pause();
            applied = await readApplied(client).catch(() => applied);
            if (applied.has(migration.hash)) { last = undefined; break; }
          }
        }
        if (last) throw last;
      }
      migrationStatus = "ok";
    } catch (error) {
      // A connection failure at boot must not poison this instance: the next request tries again.
      migrationStatus = `failed: ${redact(error).split("\n")[0]}`;
      migrationPromise = undefined;
      runtimePromise = undefined;
      throw error;
    }
  })();
  return migrationPromise;
}

function pause() { return new Promise((resolve) => setTimeout(resolve, 100 + Math.floor(Math.random() * 200))); }

/** Hashes already recorded in the ledger, or an empty set when the ledger does not exist yet. */
export async function readAppliedMigrationHashes(): Promise<Set<string>> {
  try { const { client } = await getRuntime(); return await readApplied(client); } catch { return new Set(); }
}

export async function getDb(): Promise<Database> { await ensureMigrated(); return (await getRuntime()).database; }
export async function upsertRows(table: any, rows: Record<string, unknown>[]): Promise<number> {
  if (!rows.length) return 0;
  const columns = getTableColumns(table) as Record<string, any>;
  if (!columns.key || !columns.updatedAt) throw new Error("A workflow table needs key and updated_at columns.");
  const groups = new Map<string, Record<string, unknown>[]>();
  for (const row of rows) {
    const properties = Object.keys(row).filter((key) => key in columns).sort();
    if (!properties.includes("key") || !properties.includes("updatedAt")) throw new Error("Every row needs key and updatedAt.");
    const signature = properties.join("\0"); groups.set(signature, [...(groups.get(signature) ?? []), row]);
  }
  const db = await getDb();
  for (const [signature, group] of groups) {
    const properties = signature.split("\0");
    const set = Object.fromEntries(properties.filter((key) => key !== "key").map((key) => [key, sql.raw(`excluded."${columns[key].name.replaceAll('"', '""')}"`)]));
    const size = Math.max(1, Math.floor(900 / properties.length));
    for (let index = 0; index < group.length; index += size) await db.insert(table).values(group.slice(index, index + size)).onConflictDoUpdate({ target: columns.key, set });
  }
  return rows.length;
}

export async function insertRun(row: WorkflowRunInsert) { await (await getDb()).insert(workflowRuns).values(row); }
export async function updateRunPlain(runKey: string, patch: Partial<Omit<WorkflowRunInsert, "runKey">>) {
  const safe = { ...patch, ...(patch.error ? { error: redact(patch.error) } : {}) };
  await (await getDb()).update(workflowRuns).set(safe).where(eq(workflowRuns.runKey, runKey));
}
export async function findLiveRun(path: string, inputHash: string) { return (await (await getDb()).select().from(workflowRuns).where(and(eq(workflowRuns.path, path), eq(workflowRuns.inputHash, inputHash), sql`${workflowRuns.finishedAt} IS NULL`)).limit(1))[0]; }
export async function findScheduledRun(path: string, scheduledFor: string) { return (await (await getDb()).select().from(workflowRuns).where(and(eq(workflowRuns.path, path), eq(workflowRuns.scheduledFor, scheduledFor))).limit(1))[0]; }
/** Newest run for a workflow, optionally limited to runs started from one workspace commit. */
export async function findLatestRun(workflow: string, workspaceHead?: string) {
  const db = await getDb();
  const conditions = [or(eq(workflowRuns.workflow, workflow), eq(workflowRuns.path, workflow))];
  if (workspaceHead) conditions.push(eq(workflowRuns.workspaceHead, workspaceHead));
  return (await db.select().from(workflowRuns).where(and(...conditions)).orderBy(desc(workflowRuns.startedAt)).limit(1))[0];
}
export async function getRunRow(identifier: string) { return (await (await getDb()).select().from(workflowRuns).where(or(eq(workflowRuns.runKey, identifier), eq(workflowRuns.runId, identifier))).limit(1))[0]; }
export const runLedgerCondition = (runKey: string) => eq(enrichmentRuns.runKey, runKey);

export async function cancelRunTree(runKey: string, reason: string | null): Promise<void> {
  const row = await getRunRow(runKey); if (!row) throw new Error(`Unknown run ${runKey}`);
  if (row.finishedAt !== null) return;
  await updateRunPlain(runKey, { status: "cancelling", stopReason: reason ?? "operator_cancelled", cancelRequestedAt: Date.now() });
  const { cancellationHook } = await import("./approve");
  await cancellationHook.resume(`${row.workflow}.${row.runKey}.cancel`, { reason }).catch((error) => { if (!HookNotFoundError.is(error)) throw error; });
  if (row.runId) { const run = getRun(row.runId); if (await run.exists) await run.cancel(reason === null ? undefined : { cancelReason: reason }); }
}

export async function getRunCostSources(runKey: string) {
  return (await getDb()).select({ source: enrichmentRuns.costSource, calls: sql<number>`count(*)`, costUsd: sql<number>`coalesce(sum(${enrichmentRuns.costUsd}),0)` }).from(enrichmentRuns).where(eq(enrichmentRuns.runKey, runKey)).groupBy(enrichmentRuns.costSource);
}
export async function getRunLedgerSummary(runKey: string) {
  const rows = await (await getDb()).select({ rowKey: enrichmentRuns.rowKey, step: enrichmentRuns.step, status: enrichmentRuns.status, source: enrichmentRuns.costSource, costUsd: enrichmentRuns.costUsd }).from(enrichmentRuns).where(eq(enrichmentRuns.runKey, runKey));
  const keyed = new Map<string, Set<string>>(); const sources = new Map<string, { calls: number; costUsd: number }>();
  let cacheHits = 0, pending = 0, lost = 0, activeStep: string | null = null, unkeyedSuccess = 0, unkeyedEmpty = 0, unkeyedFailed = 0;
  for (const row of rows) {
    if (row.rowKey) { const set = keyed.get(row.rowKey) ?? new Set(); set.add(row.status); keyed.set(row.rowKey, set); }
    else if (["success", "cache_hit"].includes(row.status)) unkeyedSuccess++; else if (row.status === "empty") unkeyedEmpty++; else if (["error", "lost"].includes(row.status)) unkeyedFailed++;
    if (row.status === "cache_hit") cacheHits++; if (row.status === "pending") { pending++; activeStep ??= row.step; } if (row.status === "lost") lost++;
    const source = sources.get(row.source) ?? { calls: 0, costUsd: 0 }; source.calls++; source.costUsd += Number(row.costUsd ?? 0); sources.set(row.source, source);
  }
  let success = unkeyedSuccess, empty = unkeyedEmpty, failed = unkeyedFailed;
  for (const set of keyed.values()) { if (set.has("error") || set.has("lost")) failed++; else if (set.has("success") || set.has("cache_hit")) success++; else if (set.has("empty")) empty++; }
  return { success, empty, failed, cacheHits, pending, lost, activeStep, costSources: [...sources].map(([source, value]) => ({ source, ...value })) };
}

async function finishRun(runKey: string, patch: Partial<Omit<WorkflowRunInsert, "runKey">>) {
  const db = await getDb();
  await db.update(enrichmentRuns).set({ status: "lost", errorKind: "lost", error: "paid call outcome unavailable after terminal run" }).where(and(eq(enrichmentRuns.runKey, runKey), eq(enrichmentRuns.status, "pending")));
  const cost = (await db.select({ costUsd: sql<number>`coalesce(sum(${enrichmentRuns.costUsd}),0)` }).from(enrichmentRuns).where(eq(enrichmentRuns.runKey, runKey)))[0];
  await updateRunPlain(runKey, { ...patch, costUsd: Number(cost?.costUsd ?? 0) });
}
export async function reconcileRun(runKey: string): Promise<WorkflowRunRow> {
  let row = await getRunRow(runKey); if (!row) throw new Error(`Unknown run ${runKey}`);
  if (row.finishedAt !== null || !["running", "waiting", "cancelling"].includes(row.status)) return row;
  const now = Date.now();
  if (!row.runId) { if (now - row.startedAt < 600_000) return row; await finishRun(runKey, { status: "failed", error: "start not recorded", finishedAt: now }); return (await getRunRow(runKey))!; }
  const run = getRun(row.runId);
  if (!(await run.exists)) { await finishRun(runKey, { status: "failed", error: "run state expired", finishedAt: now }); return (await getRunRow(runKey))!; }
  const sdk = await run.status;
  let status: WorkflowStatus | undefined = sdk === "completed" ? "completed" : sdk === "failed" ? "failed" : sdk === "cancelled" ? "cancelled" : undefined;
  if (!status) return row;
  if (row.status === "cancelling") status = "cancelled";
  let error: string | undefined;
  if (status === "failed") try { await run.returnValue; } catch (caught) { const cause = WorkflowRunFailedError.is(caught) ? caught.cause : caught; error = redact(cause); }
  await finishRun(runKey, { status, ...(error ? { error } : {}), finishedAt: now });
  return (await getRunRow(runKey))!;
}

export function assertReadOnlyQuery(query: string): string {
  const value = query.trim().replace(/;+\s*$/, "");
  if (!/^\s*(select|with)\b/i.test(value) || /;|\b(delete|update|insert|replace|drop|alter|create|attach|detach|pragma|vacuum|reindex)\b/i.test(value)) throw new Error("query accepts one read-only SELECT statement");
  return value;
}
export async function executeSelect(query: string) { const result = await (await getRuntime()).client.execute(assertReadOnlyQuery(query)); return result.rows.map((row) => ({ ...row })); }
export const executeReadOnly = executeSelect;
