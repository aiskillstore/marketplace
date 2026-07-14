import { AgentSession } from "./agent-session.js";
import { type ResolvedAgentConfig } from "./agent-resolve-config.js";
export interface CreateAgentSessionForCredentialDirOptions {
    /** When true, credentials.json must exist (jmap_request path). */
    requireCredentials?: boolean;
}
export declare function createAgentSessionForCredentialDir(credentialDir: string, envDefaults: Pick<ResolvedAgentConfig, "authUrl" | "apiUrl" | "scryptSalt">, options?: CreateAgentSessionForCredentialDirOptions): Promise<AgentSession>;
//# sourceMappingURL=agent-session-for-dir.d.ts.map