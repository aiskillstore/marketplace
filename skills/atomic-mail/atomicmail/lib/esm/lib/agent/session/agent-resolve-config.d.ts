import { type SkillFiles } from "./agent-credentials-store.js";
export type ConfigSource = "credentials-file" | "env" | "mixed" | "defaults";
export interface ResolvedAgentConfig {
    authUrl: string;
    apiUrl: string;
    scryptSalt: string;
    apiKey?: string;
    inboxId?: string;
    credentialDir: string;
    files: SkillFiles;
    source: ConfigSource;
}
/**
 * Default credential directory:
 *   1. ATOMIC_MAIL_CREDENTIALS_DIR
 *   2. ~/.atomicmail/ or %USERPROFILE%/.atomicmail
 */
export declare function resolveCredentialDir(): string;
/**
 * AgentSkill / CLI: resolve credential directory from `--credentials-dir` or
 * `ATOMIC_MAIL_CREDENTIALS_DIR`, with `~` expansion (MCP uses `resolveCredentialDir` instead).
 */
export declare function expandCredentialDirInput(dir?: string): string;
/**
 * Merge credentials.json with ATOMIC_MAIL_* env (env wins per field).
 * authUrl and apiUrl fall back to production defaults when unset.
 */
export declare function resolveAgentConfigFromEnv(): Promise<ResolvedAgentConfig>;
//# sourceMappingURL=agent-resolve-config.d.ts.map