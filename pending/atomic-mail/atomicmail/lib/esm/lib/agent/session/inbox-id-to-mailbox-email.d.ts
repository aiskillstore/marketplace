/** Subset of `process.env` read for `$INBOX` normalization (tests may pass a stub). */
export type InboxEmailEnv = {
    ATOMIC_MAIL_INBOX_DOMAIN?: string;
};
export declare function inboxIdToMailboxEmail(inboxId: string, env?: InboxEmailEnv): string;
//# sourceMappingURL=inbox-id-to-mailbox-email.d.ts.map