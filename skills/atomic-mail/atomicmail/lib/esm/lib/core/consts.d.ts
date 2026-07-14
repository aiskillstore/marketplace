/**
 * Fixed proof-of-work scrypt salt. The auth-service passes this string (UTF-8
 * bytes of the hex text, not decoded binary) to `scrypt` as the `salt`
 * argument; all PoW clients must use the same value.
 */
export declare const DEFAULT_POW_SCRYPT_SALT_HEX: string;
/** Production auth-service base URL when unset in env and credentials.json. */
export declare const DEFAULT_AUTH_URL: string;
/** Production JMAP / API base URL when unset in env and credentials.json. */
export declare const DEFAULT_API_URL: string;
export declare const ONE_SEC_MS: number;
export declare const ONE_MIN_MS: number;
export declare const ONE_HOUR_MS: number;
export declare const ONE_DAY_MS: number;
export declare const ONE_MONTH_MS: number;
export declare const ONE_YEAR_MS: number;
//# sourceMappingURL=consts.d.ts.map