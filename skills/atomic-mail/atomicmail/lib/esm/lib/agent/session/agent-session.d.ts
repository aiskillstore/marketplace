import { type CredentialStore, type SkillFiles } from "./agent-credentials-store.js";
import type { JmapBlobUploadLimits } from "../jmap/agent-jmap-blob-limits.js";
export interface AgentSessionConfig {
    authUrl: string;
    apiUrl: string;
    scryptSalt: string;
    apiKey?: string;
    inboxId?: string;
    credentialDir: string;
    files?: SkillFiles;
    store?: CredentialStore;
}
export interface RegisterResult {
    inbox: string;
    accountId: string;
    /** Present only on first-time signup (not idempotent replay). */
    apiKey?: string;
    idempotent?: boolean;
}
export interface RegisterOptions {
    /**
     * Allows replacing credentials in the current credential directory when the
     * requested username differs from the stored inbox local-part.
     */
    forced?: boolean;
}
/** Local-part of an inbox email, or the whole string if no @. */
export declare function inboxLocalPart(inboxId: string): string;
export declare class AgentSession {
    private readonly authUrl;
    readonly apiUrl: string;
    private readonly scryptSalt;
    private apiKey;
    private inboxId;
    readonly credentialDir: string;
    readonly files: SkillFiles | undefined;
    private readonly store;
    private sessionJWT;
    private capabilityJWT;
    private cachedMailAccountId;
    private cachedUploadUrl;
    private cachedDownloadUrl;
    /** RFC 8620 Session `apiUrl` (POST target); from `/.well-known/jmap`. */
    private cachedJmapPostUrl;
    /** Last successful GET /.well-known/jmap JSON (for RFC 9404 blob limits). */
    private cachedJmapSession;
    constructor(cfg: AgentSessionConfig);
    static create(cfg: AgentSessionConfig): Promise<AgentSession>;
    get hasApiKey(): boolean;
    get currentInboxId(): string | undefined;
    get currentUploadUrl(): string | undefined;
    get currentDownloadUrl(): string | undefined;
    private loadFromStore;
    private currentCredentialArtifacts;
    /**
     * Primary JMAP mail accountId from GET /.well-known/jmap (cached).
     */
    getPrimaryMailAccountId(): Promise<string>;
    invalidateJmapSessionCache(): void;
    private refreshJmapSessionData;
    /**
     * Full URL for JMAP `POST` batches (RFC 8620 Session `apiUrl` from
     * `GET /.well-known/jmap`).
     */
    getJmapPostUrl(): Promise<string>;
    getBlobUploadLimitsForAccount(accountId: string): Promise<JmapBlobUploadLimits | null>;
    /**
     * Register or return existing inbox when username matches (idempotent).
     * Different username requires explicit force to replace credentials and
     * create a new inbox.
     */
    register(username: string, options?: RegisterOptions): Promise<RegisterResult>;
    getCapabilityToken(): Promise<string>;
    private ensureSession;
    destroy(): void;
}
export interface PersistLoginWithApiKeyInput {
    authUrl: string;
    apiUrl: string;
    scryptSalt: string;
    apiKey: string;
    files: SkillFiles;
    onPowProgress?: (nonce: bigint) => void;
}
/** PoW login with an existing API key; writes credentials + JWT files. */
export declare function persistLoginWithApiKey(input: PersistLoginWithApiKeyInput): Promise<{
    inboxId: string;
}>;
//# sourceMappingURL=agent-session.d.ts.map