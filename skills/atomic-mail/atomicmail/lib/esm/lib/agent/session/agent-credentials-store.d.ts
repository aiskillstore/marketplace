export interface Credentials {
    apiKey: string;
    inboxId: string;
    authUrl: string;
    apiUrl: string;
    scryptSalt: string;
    uploadUrl: string;
    downloadUrl: string;
}
export interface SkillFiles {
    credentialsFile: string;
    sessionFile: string;
    capabilityFile: string;
}
export interface CredentialArtifacts {
    credentials?: Credentials;
    sessionJwt?: string;
    capabilityJwt?: string;
}
export interface CredentialStore {
    load(): Promise<CredentialArtifacts>;
    /**
     * Persist provided artifacts. Missing fields are left unchanged.
     */
    save(artifacts: CredentialArtifacts): Promise<void>;
    clear(): Promise<void>;
}
export declare function defaultFilesFromOutDir(outDir: string): SkillFiles;
export declare function parseCredentialsJson(raw: string, pathForErrors?: string): Credentials;
export declare function serializeCredentials(creds: Credentials): string;
export declare function writeCredentials(path: string, creds: Credentials): Promise<void>;
export declare function readCredentials(path: string): Promise<Credentials>;
export declare function tryReadCredentials(path: string): Promise<Credentials | undefined>;
export declare function writeJwtFile(path: string, jwt: string): Promise<void>;
export declare function tryReadJwtFile(path: string): Promise<string | undefined>;
export declare class FilesystemCredentialStore implements CredentialStore {
    readonly files: SkillFiles;
    constructor(files: SkillFiles);
    load(): Promise<CredentialArtifacts>;
    save(artifacts: CredentialArtifacts): Promise<void>;
    clear(): Promise<void>;
}
/** Best-effort removal of credential artifacts (ignore missing files). */
export declare function unlinkCredentialArtifacts(files: SkillFiles): Promise<void>;
//# sourceMappingURL=agent-credentials-store.d.ts.map