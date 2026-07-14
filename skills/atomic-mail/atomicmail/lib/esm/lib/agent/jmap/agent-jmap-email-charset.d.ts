import type { JmapEnvelope } from "./agent-jmap.js";
/**
 * Ensures blob-backed `text/*` body parts in `Email/set` `create` include
 * `charset` when omitted, for strict JMAP servers. Skips parts with `partId`
 * (RFC 8621 forbids charset there).
 */
export declare function ensureTextCharsetOnEmailSetBlobParts(envelope: JmapEnvelope): void;
//# sourceMappingURL=agent-jmap-email-charset.d.ts.map