import type { MaybePromise } from "./types.js";
export declare function delay(ms: number): Promise<void>;
export type RetryCfg = {
    maxTimeoutMs?: number;
    startTimeoutMs?: number;
    backoffMul?: number;
    /** Optional hook before the next retry; must not throw. */
    onBeforeRetry?: (e: unknown) => MaybePromise<void>;
};
/** Retries `fn` on throw with exponential backoff until `maxTimeoutMs` is exceeded. */
export declare function retry<R>(fn: () => MaybePromise<R>, config: RetryCfg): Promise<R>;
//# sourceMappingURL=utils.d.ts.map