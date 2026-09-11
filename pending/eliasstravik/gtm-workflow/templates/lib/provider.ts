import { createHash, randomUUID } from "node:crypto";
import { and, eq } from "drizzle-orm";
import { z } from "zod";
import { getStepMetadata } from "workflow";
import { getDb } from "./db";
import { reserveSpend } from "./spend";
import { redact, redactedError } from "./redact";
import {
  enrichmentCache,
  enrichmentRuns,
  type CostSource,
  type EnrichmentErrorKind,
  type EnrichmentStatus,
} from "./schema";

export type PaidCallMeta = {
  runKey: string;
  slug: string;
  rowKey?: string;
  step?: string;
  /** Optional ceiling supplied by an accepted event source. */
  maxSpendUsd?: number;
  concurrency?: number;
};

export class ProviderAuthError extends Error {
  readonly providerErrorKind = "provider_auth";
  override name = "ProviderAuthError";

  constructor(message: string) {
    super(`[provider_auth] ${message}`);
  }
}

export class ProviderQuotaError extends Error {
  readonly providerErrorKind = "provider_quota";
  override name = "ProviderQuotaError";

  constructor(message: string) {
    super(`[provider_quota] ${message}`);
  }
}

export class ProviderPreCallError extends Error {
  readonly providerErrorKind = "pre_call";
  override name = "ProviderPreCallError";
}

export type ProviderInput<T extends z.ZodTypeAny> = {
  step?: string;
  name: string;
  endpoint: string;
  input: unknown;
  schema: T;
  ttlMs: number;
  costUsd?: number;
  costSource?: Exclude<CostSource, "reported">;
  call: () => Promise<
    | z.input<T>
    | { value: z.input<T>; raw?: unknown; costUsd?: number }
  >;
  /** Rebuild the adapter value from a preserved vendor response on cache hits. */
  parseRaw?: (raw: unknown) => z.input<T>;
  meta: PaidCallMeta;
  isEmpty?: (value: z.infer<T>) => boolean;
  /** Shared admission for parallel paid branches; cache hits remain free. */
  admission?: { operation: string; maxSpendUsd: number; maxCalls: number };
};

export type PaidCallResult<T> = {
  value: T;
  costUsd: number;
  costSource: CostSource;
  status: "cache_hit" | "success" | "empty";
};

export async function provider<T extends z.ZodTypeAny>(
  input: ProviderInput<T>,
): Promise<PaidCallResult<z.infer<T>>> {
  input = { ...input, meta: { ...input.meta, step: input.meta.step ?? input.step } };
  const db = await getDb();
  const canonical = stableJson(input.input);
  const inputsHash = createHash("sha256").update(canonical).digest("hex");
  const now = Date.now();
  const acceptedCostSource = input.costSource ?? "fixed";
  const cache = (
    await db
      .select()
      .from(enrichmentCache)
      .where(
        and(
          eq(enrichmentCache.provider, input.name),
          eq(enrichmentCache.endpoint, input.endpoint),
          eq(enrichmentCache.inputsHash, inputsHash),
        ),
      )
      .limit(1)
  )[0];

  if (cache && cache.expiresAt > now) {
    try {
      const raw = JSON.parse(cache.raw ?? cache.value);
      const value = input.schema.parse(input.parseRaw ? input.parseRaw(raw) : raw);
      await insertLedger(input, {
        inputsHash,
        status: "cache_hit",
        costUsd: 0,
        costSource: acceptedCostSource,
        error: null,
        errorKind: null,
      });
      return {
        value,
        costUsd: 0,
        costSource: acceptedCostSource,
        status: "cache_hit",
      };
    } catch (error) {
      await insertLedger(input, {
        inputsHash,
        status: "error",
        costUsd: 0,
        costSource: acceptedCostSource,
        error: redact(error),
        errorKind: "cache_parse",
      });
      throw redactedError(error);
    }
  }

  if (!input.admission && (input.meta.concurrency ?? 1) > 1) {
    if (input.meta.maxSpendUsd === undefined) throw new Error("Parallel row calls require an accepted spending cap");
    input = { ...input, admission: {
      operation: `${getStepMetadata().stepId}:${input.name}:${input.endpoint}:${inputsHash}`,
      maxSpendUsd: input.meta.maxSpendUsd, maxCalls: Number.MAX_SAFE_INTEGER,
    } };
  }
  const ledgerId = input.admission ? await reserveSpend({
    meta: input.meta, operation: input.admission.operation, provider: input.name, endpoint: input.endpoint,
    estimateUsd: input.costUsd ?? 0,
    maxSpendUsd: Math.min(input.admission.maxSpendUsd, input.meta.maxSpendUsd ?? input.admission.maxSpendUsd),
    maxCalls: input.admission.maxCalls,
  }) : randomUUID();
  if (!input.admission) await db.insert(enrichmentRuns).values({
    id: ledgerId,
    runKey: input.meta.runKey,
    workflow: input.meta.slug,
    rowKey: input.meta.rowKey ?? null,
    step: input.meta.step ?? null,
    provider: input.name,
    endpoint: input.endpoint,
    inputsHash,
    status: "pending",
    costUsd: input.costUsd ?? 0,
    costSource: acceptedCostSource,
    error: null,
    errorKind: null,
    createdAt: now,
  });
  else await db.update(enrichmentRuns).set({ inputsHash }).where(eq(enrichmentRuns.id, ledgerId));

  try {
    const called = await input.call();
    const reported = unwrapCallResult(called);
    const value = input.schema.parse(reported.value);
    const empty = input.isEmpty?.(value) ?? isEmpty(value);
    const costUsd = reported.costUsd ?? input.costUsd ?? 0;
    const costSource: CostSource =
      reported.costUsd === undefined ? acceptedCostSource : "reported";
    const status = empty ? "empty" : "success";
    const raw = JSON.stringify(reported.raw) ?? null;
    await db.batch([
      db
        .insert(enrichmentCache)
        .values({
          provider: input.name,
          endpoint: input.endpoint,
          inputsHash,
          inputs: canonical,
          raw,
          value: JSON.stringify(value),
          expiresAt: now + input.ttlMs,
          createdAt: now,
        })
        .onConflictDoUpdate({
          target: [
            enrichmentCache.provider,
            enrichmentCache.endpoint,
            enrichmentCache.inputsHash,
          ],
          set: {
            inputs: canonical,
            raw,
            value: JSON.stringify(value),
            expiresAt: now + input.ttlMs,
            createdAt: now,
          },
        }),
      db
        .update(enrichmentRuns)
        .set({ status, costUsd, costSource, error: null, errorKind: null })
        .where(eq(enrichmentRuns.id, ledgerId)),
    ]);
    return { value, costUsd, costSource, status };
  } catch (error) {
    const errorKind = classifyError(error);
    const costUsd = errorKind === "pre_call" ? 0 : input.costUsd ?? 0;
    await db
      .update(enrichmentRuns)
      .set({
        status: "error",
        costUsd,
        costSource: acceptedCostSource,
        error: redact(error),
        errorKind,
      })
      .where(eq(enrichmentRuns.id, ledgerId));
    throw redactedError(error);
  }
}

async function insertLedger(
  input: Pick<ProviderInput<any>, "meta" | "name" | "endpoint">,
  row: {
    inputsHash: string;
    status: EnrichmentStatus;
    costUsd: number | null;
    costSource: CostSource;
    error: string | null;
    errorKind: EnrichmentErrorKind | null;
  },
) {
  const db = await getDb();
  await db.insert(enrichmentRuns).values({
    id: randomUUID(),
    runKey: input.meta.runKey,
    workflow: input.meta.slug,
    rowKey: input.meta.rowKey ?? null,
    step: input.meta.step ?? null,
    provider: input.name,
    endpoint: input.endpoint,
    inputsHash: row.inputsHash,
    status: row.status,
    costUsd: row.costUsd,
    costSource: row.costSource,
    error: row.error,
    errorKind: row.errorKind,
    createdAt: Date.now(),
  });
}

function classifyError(error: unknown): EnrichmentErrorKind {
  const kind =
    error && typeof error === "object"
      ? (error as { providerErrorKind?: unknown }).providerErrorKind
      : undefined;
  if (
    kind === "pre_call" ||
    kind === "provider_auth" ||
    kind === "provider_quota"
  ) {
    return kind;
  }
  return "call";
}

function unwrapCallResult<T>(
  value: T | { value: T; raw?: unknown; costUsd?: number },
) {
  if (
    value &&
    typeof value === "object" &&
    "value" in value &&
    ("costUsd" in value || "raw" in value)
  ) {
    const reported = value as { value: T; raw?: unknown; costUsd?: number };
    return {
      value: reported.value,
      raw: reported.raw ?? reported.value,
      costUsd: reported.costUsd,
    };
  }
  return { value: value as T, raw: value, costUsd: undefined };
}

function isEmpty(value: unknown): boolean {
  if (value === null) return true;
  if (Array.isArray(value)) return value.length === 0;
  return typeof value === "object" && Object.keys(value as object).length === 0;
}

function stableJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.entries(value)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, item]) => `${JSON.stringify(key)}:${stableJson(item)}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}
