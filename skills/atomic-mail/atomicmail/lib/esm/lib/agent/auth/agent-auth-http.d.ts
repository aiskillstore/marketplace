export declare function fetchChallenge(authUrl: string): Promise<{
    challengeJWT: string;
    challenge: string;
    difficulty: number;
}>;
export interface SessionResponse {
    sessionJWT: string;
    apiKey?: string;
}
export declare function exchangeSession(authUrl: string, body: {
    challengeJWT: string;
    powHex: string;
    nonce: string;
    apiKey?: string;
    username?: string;
}): Promise<SessionResponse>;
export declare function fetchCapability(authUrl: string, sessionJWT: string): Promise<string>;
export interface PerformPoWInput {
    authUrl: string;
    scryptSalt: string;
    apiKey?: string;
    username?: string;
    onPowProgress?: (nonce: bigint) => void;
}
export declare function performPoWAndSession(input: PerformPoWInput): Promise<SessionResponse>;
//# sourceMappingURL=agent-auth-http.d.ts.map