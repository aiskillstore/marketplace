/** Parse JMAP responses for integration tests and dev CLIs. */
/** Throws if `EmailSubmission/set` did not create a submission. */
export declare function assertJmapSubmissionCreated(bodyText: string): void;
/**
 * Throws if the first `Blob/upload` response reports `size: 0` for a non-empty
 * payload (common server misconfiguration).
 */
export declare function assertBlobUploadSizesNonZero(bodyText: string, expectBytes: number): void;
//# sourceMappingURL=agent-jmap-verify.d.ts.map