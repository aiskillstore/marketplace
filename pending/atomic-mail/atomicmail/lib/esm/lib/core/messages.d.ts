type SharedErrorMap = Record<string, string>;
declare const SHARED_ERRORS: SharedErrorMap;
export declare function sharedError(key: keyof typeof SHARED_ERRORS): string;
export declare function sharedErrorTemplate(key: keyof typeof SHARED_ERRORS, values: Record<string, string | number>): string;
export {};
//# sourceMappingURL=messages.d.ts.map