/** Keys allowed in MCP `vars` / skill `--vars` (without leading `$`). */
export declare const USER_VAR_KEY_RE: RegExp;
/**
 * Parses a JSON object of string values (skill `--vars` / MCP `vars`).
 * Throws `Error` with the same messages the CLI used to emit via `fail(...)`.
 */
export declare function parseUserVarsJson(jsonString: string): Record<string, string>;
/** Matches `$FOO_BAR`; excludes JMAP keywords like `$draft` (lowercase). */
export declare const VAR_PATTERN: RegExp;
/** Names substituted from JMAP session / credentials when not overridden in `vars`. */
export declare const SESSION_VAR_NAMES: Set<string>;
export interface SubstituteVarsInput {
    raw: string;
    /** Caller-supplied values; keys are names without `$` (e.g. `TO`, `SUBJECT`). */
    vars?: Record<string, string>;
    /** Invoked only when the name appears in `raw`, is absent from `vars`, and a resolver exists. */
    autoResolvers?: Record<string, () => Promise<string> | string>;
}
export interface SubstituteVarsResult {
    text: string;
}
/** Unique variable names in order of first occurrence (without leading `$`). */
export declare function findVarReferences(raw: string): string[];
/**
 * Replaces every `$VAR_NAME` in `raw` with the corresponding string.
 * Single pass — values are not scanned for further `$` tokens.
 * Throws if any referenced variable has no value (after vars + autoResolvers).
 */
export declare function substituteVars(input: SubstituteVarsInput): Promise<SubstituteVarsResult>;
//# sourceMappingURL=agent-vars.d.ts.map