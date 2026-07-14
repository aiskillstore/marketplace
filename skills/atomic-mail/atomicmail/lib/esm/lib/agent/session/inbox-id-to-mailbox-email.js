import process from "node:process";
/**
 * Normalizes stored `inboxId` into an RFC5322 mailbox address for `$INBOX`
 * substitution (`From`, submission `envelope`, etc.).
 *
 * Credentials may store only the local-part (`alice`); production mailboxes
 * live at `alice@atomicmail.ai`. Custom stacks can set
 * `ATOMIC_MAIL_INBOX_DOMAIN` (hostname only, optional leading `@` stripped).
 */
const DEFAULT_INBOX_DOMAIN = "atomicmail.ai";
export function inboxIdToMailboxEmail(inboxId, env) {
    const trimmed = inboxId.trim();
    if (trimmed.length === 0)
        return inboxId;
    if (trimmed.includes("@"))
        return trimmed;
    const raw = (env !== undefined
        ? env.ATOMIC_MAIL_INBOX_DOMAIN
        : process.env.ATOMIC_MAIL_INBOX_DOMAIN)?.trim();
    const domain = raw && raw.length > 0
        ? raw.replace(/^@+/, "")
        : DEFAULT_INBOX_DOMAIN;
    return `${trimmed}@${domain}`;
}
