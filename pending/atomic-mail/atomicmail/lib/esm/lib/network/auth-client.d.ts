export interface AuthClientOptions {
    /** Base URL of auth-service, e.g. "http://localhost:8000". Trailing slashes are stripped. */
    baseUrl: string;
    /**
     * PoW scrypt salt (hex string). When omitted, {@link DEFAULT_POW_SCRYPT_SALT_HEX}
     * is used so clients match the bundled auth-service.
     */
    scryptSaltHex?: string;
}
export interface SignupResult {
    /** Freshly minted API key. The server only returns it once — persist it. */
    apiKey: string;
    sessionJWT: string;
}
export interface LoginResult {
    sessionJWT: string;
}
export interface RenewResult {
    capabilityJWT: string;
}
/** Thrown for any non-2xx HTTP response or malformed payload. */
export declare class AuthClientError extends Error {
    status: number;
    bodyText: string;
    constructor(status: number, bodyText: string, message: string);
}
export declare class AuthClient {
    private readonly baseUrl;
    private readonly scryptSaltHex;
    constructor(options: AuthClientOptions);
    /**
     * Register a new inbox under `username`. Returns the freshly minted API key
     * (the server only ever returns it once — the caller MUST persist it) and
     * a session JWT.
     */
    signup(username: string): Promise<SignupResult>;
    /** Exchange an existing API key for a fresh session JWT. */
    login(apiKey: string): Promise<LoginResult>;
    /**
     * Exchange a session JWT for a short-lived capability JWT (audience:
     * api-service).
     */
    renew(sessionJWT: string): Promise<RenewResult>;
    private fetchChallenge;
    private postSession;
    private parseJsonOrThrow;
    /**
     * Brute-force a PoW nonce. Mirrors `generatePow` in
     * services/auth-service/src/crypto.ts: scrypt(`${challenge}:${nonce}`, salt,
     * 64) until `difficulty` leading bits of the digest are zero.
     *
     * Expected work at the server's POW_DIFFICULTY=6 is ~2^6 = 64 attempts; well
     * within the challenge JWT's 3-minute TTL.
     */
    private solvePoW;
}
//# sourceMappingURL=auth-client.d.ts.map