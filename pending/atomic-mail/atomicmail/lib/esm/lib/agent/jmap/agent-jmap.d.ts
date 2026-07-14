import { type JmapBlobUploadLimits } from "./agent-jmap-blob-limits.js";
import { type JmapAttachmentInput } from "./agent-jmap-blob-upload.js";
export type { JmapAttachmentInput } from "./agent-jmap-blob-upload.js";
export type { JmapBlobUploadLimits } from "./agent-jmap-blob-limits.js";
export declare const DEFAULT_JMAP_USING: readonly ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"];
export declare const BUNDLED_OPS_PRESET_NAMES: readonly ["list_inbox.json", "reply.json", "send_mail.json", "send_mail_attachment.json", "send_mail_blob_attachment.json"];
export declare const JMAP_MAIL_URN: "urn:ietf:params:jmap:mail";
/** RFC 9404 blob extension URN (Blob/upload, Blob/get, Blob/lookup). */
export declare const JMAP_BLOB_URN: "urn:ietf:params:jmap:blob";
export interface JmapEnvelope {
    using: string[];
    methodCalls: unknown[];
}
export declare function parseJmapEnvelope(raw: string, defaultUsing: string[], source: string): JmapEnvelope;
export declare function resolveOpsFilePath(credentialDir: string, opsFile: string): string;
export declare function readOpsFile(credentialDir: string, opsFile: string): Promise<string>;
export declare function extractPrimaryMailAccountId(session: Record<string, unknown>): string;
export interface JmapBlobEndpoints {
    uploadUrl: string;
    downloadUrl: string;
}
export declare function extractBlobEndpoints(session: Record<string, unknown>): JmapBlobEndpoints;
/** RFC 8620 §2 / §3.1: POST target for JMAP API calls from the Session object. */
export declare function extractJmapApiUrl(session: Record<string, unknown>): string;
/**
 * RFC 9404 §3.1 blob limits for one account from GET /.well-known/jmap JSON.
 * Returns null when the account does not advertise `urn:ietf:params:jmap:blob`.
 */
export declare function extractBlobUploadLimits(session: Record<string, unknown>, accountId: string): JmapBlobUploadLimits | null;
export declare function fetchJmapWellKnown(apiUrl: string, capabilityJwt: string): Promise<Record<string, unknown>>;
/** Minimal surface for JMAP execution (implemented by AgentSession). */
export interface JmapSessionPort {
    /** Base used for `GET /.well-known/jmap` (configured `ATOMIC_MAIL_API_URL` / credentials). */
    readonly apiUrl: string;
    readonly files?: {
        credentialsFile: string;
    };
    /** RFC 8620 Session `apiUrl` — full URL for `POST` JMAP batches. */
    getJmapPostUrl(): Promise<string>;
    getPrimaryMailAccountId(): Promise<string>;
    getCapabilityToken(): Promise<string>;
    readonly currentInboxId?: string;
    readonly currentUploadUrl?: string;
    readonly currentDownloadUrl?: string;
    /** RFC 9404 §3.1 limits from cached session; null if blob capability not advertised for the account. */
    getBlobUploadLimitsForAccount(accountId: string): Promise<JmapBlobUploadLimits | null>;
}
export interface RunJmapRequestInput {
    session: JmapSessionPort;
    /** Raw JSON: methodCalls array or full envelope */
    opsJson: string;
    /** Default `using` when the envelope omits it */
    defaultUsing: string[];
    /** Label for parse errors */
    sourceLabel: string;
    dryRun?: boolean;
    /**
     * Local files uploaded via RFC 8620 (`POST` to session `uploadUrl`) before
     * `$VAR` substitution. Injects `ATTACHMENT_0_BLOB_ID`, `ATTACHMENT_0_NAME`,
     * `ATTACHMENT_0_TYPE`, `ATTACHMENT_0_SIZE`, … and `ATTACHMENT_COUNT`.
     */
    attachments?: JmapAttachmentInput[];
    /** Base path for relative `attachments[].path` (default: process cwd). */
    attachmentPathBase?: string;
    /** Values for `$VAR` tokens (keys without `$`). Overrides injected attachment vars. */
    vars?: Record<string, string>;
}
/**
 * Parse ops JSON, substitute `$VAR_NAME` tokens (session + caller vars), POST to JMAP.
 */
export declare function runJmapRequest(input: RunJmapRequestInput): Promise<{
    ok: boolean;
    status: number;
    bodyText: string;
}>;
/**
 * Resolves the JMAP `Mailbox` id for the account inbox (`role: "inbox"`).
 * Used for `$INBOX_MAILBOX_ID` substitution (distinct from `$INBOX`, which is
 * the mailbox *email address* — see `inboxIdToMailboxEmail` for normalization).
 */
export declare function fetchInboxMailboxId(port: JmapSessionPort): Promise<string>;
export declare function postJmap(jmapPostUrl: string, capabilityJwt: string, envelope: JmapEnvelope): Promise<{
    ok: boolean;
    status: number;
    bodyText: string;
}>;
/** Attach _next hints to a successful JMAP JSON object when parseable. */
export declare function attachJmapNextHints(bodyText: string): string;
//# sourceMappingURL=agent-jmap.d.ts.map