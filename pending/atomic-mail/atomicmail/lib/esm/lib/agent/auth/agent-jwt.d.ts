export declare const SESSION_SAFETY_MARGIN_MS = 60000;
export declare const CAPABILITY_SAFETY_MARGIN_MS = 20000;
export interface JwtPayload {
    exp?: number;
    iat?: number;
    jti?: string;
    inboxId?: string;
    [key: string]: unknown;
}
export declare function decodeJwtPayload<T = JwtPayload>(jwt: string): T;
export declare function isJwtExpired(jwt: string, marginMs: number): boolean;
//# sourceMappingURL=agent-jwt.d.ts.map