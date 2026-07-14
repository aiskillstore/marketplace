export interface JmapBlobUploadLimits {
    maxSizeBlobSet: number | null;
    /** When omitted, skip maxDataSources enforcement (not advertised). */
    maxDataSources?: number;
}
export interface JmapEnvelopeLike {
    using: string[];
    methodCalls: unknown[];
}
export declare function utf8ByteLength(s: string): number;
/** Decoded byte length; throws if the string is not valid standard base64. */
export declare function decodedBase64ByteLength(b64: string): number;
/**
 * Returns total octets for one UploadObject `data` array, or `null` if a literal
 * (non-`#`) blobId slice is present or a `#ref` is not yet in `knownSizes`.
 */
export declare function tryComputeUploadDataOctets(dataUnknown: unknown, knownSizes: ReadonlyMap<string, number>): number | null;
/**
 * Walks `methodCalls` in order and enforces limits for each `Blob/upload` whose
 * `accountId` has an entry in `limitsByAccount`.
 */
export declare function assertBlobUploadEnvelopeWithinLimits(envelope: JmapEnvelopeLike, limitsByAccount: ReadonlyMap<string, JmapBlobUploadLimits | null>): void;
export declare function assertAttachmentBytesWithinBlobLimit(items: readonly {
    label: string;
    byteLength: number;
}[], limits: JmapBlobUploadLimits | null): void;
//# sourceMappingURL=agent-jmap-blob-limits.d.ts.map