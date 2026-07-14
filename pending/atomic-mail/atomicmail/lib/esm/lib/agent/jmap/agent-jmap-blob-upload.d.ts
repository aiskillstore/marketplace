import type { JmapSessionPort } from "./agent-jmap.js";
/** One local file to upload before `$ATTACHMENT_*` substitution in ops JSON. */
export interface JmapAttachmentInput {
    path: string;
    filename?: string;
    contentType?: string;
}
export declare function guessMimeTypeFromFilename(name: string): string;
export declare function expandUploadUrl(template: string, accountId: string): string;
export declare function postBinaryBlobUpload(uploadUrlExpanded: string, capabilityJwt: string, bytes: Uint8Array, contentType: string): Promise<{
    blobId: string;
    size: number;
}>;
/**
 * Reads each file, POSTs bytes to the JMAP session `uploadUrl`, and returns
 * placeholder values for use in standard JMAP ops (same batch as
 * `Email/set` / `EmailSubmission/set`).
 *
 * Injected keys (strings): `ATTACHMENT_0_BLOB_ID`, `ATTACHMENT_0_NAME`,
 * `ATTACHMENT_0_TYPE`, `ATTACHMENT_0_SIZE`, … zero-based index per file, plus
 * `ATTACHMENT_COUNT`.
 */
export declare function buildVarsFromAttachmentFiles(session: JmapSessionPort, attachments: JmapAttachmentInput[], pathBase?: string): Promise<Record<string, string>>;
//# sourceMappingURL=agent-jmap-blob-upload.d.ts.map